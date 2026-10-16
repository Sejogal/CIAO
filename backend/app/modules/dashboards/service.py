from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.dashboards.model import Dashboard, Widget
from app.modules.dashboards.schema import (
    DashboardCreate, DashboardUpdate, WidgetCreate, WidgetUpdate,
)
from app.modules.datastreams.service import DatastreamService
from app.modules.projects.service import ProjectService


class DashboardService:
    @staticmethod
    async def _get(db: AsyncSession, dashboard_id: UUID, user_id: UUID) -> Dashboard:
        dashboard = await db.get(Dashboard, dashboard_id)
        if not dashboard:
            raise HTTPException(404, "Dashboard not found")
        await ProjectService.get_for_user(db, dashboard.project_id, user_id)
        return dashboard

    @staticmethod
    async def create(db: AsyncSession, user_id: UUID, data: DashboardCreate) -> Dashboard:
        project = await ProjectService.get_for_user(db, data.project_id, user_id)
        if project.owner_id != user_id:
            raise HTTPException(403, "Only the project owner can manage dashboards")
        row = Dashboard(**data.model_dump(), owner_id=user_id)
        db.add(row)
        await db.flush()
        await db.refresh(row)
        return row

    @staticmethod
    async def list_for_project(db: AsyncSession, user_id: UUID, project_id: UUID) -> list[Dashboard]:
        await ProjectService.get_for_user(db, project_id, user_id)
        result = await db.execute(select(Dashboard).where(Dashboard.project_id == project_id).order_by(Dashboard.created_at))
        return list(result.scalars().all())

    @staticmethod
    async def get(db: AsyncSession, user_id: UUID, dashboard_id: UUID) -> Dashboard:
        return await DashboardService._get(db, dashboard_id, user_id)

    @staticmethod
    async def update(db: AsyncSession, user_id: UUID, dashboard_id: UUID, data: DashboardUpdate) -> Dashboard:
        row = await DashboardService._get(db, dashboard_id, user_id)
        if row.owner_id != user_id:
            raise HTTPException(403, "Only the dashboard owner can update it")
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(row, key, value)
        await db.flush()
        await db.refresh(row)
        return row

    @staticmethod
    async def delete(db: AsyncSession, user_id: UUID, dashboard_id: UUID) -> None:
        row = await DashboardService._get(db, dashboard_id, user_id)
        if row.owner_id != user_id:
            raise HTTPException(403, "Only the dashboard owner can delete it")
        await db.delete(row)
        await db.flush()

    @staticmethod
    async def list_widgets(db: AsyncSession, user_id: UUID, dashboard_id: UUID) -> list[Widget]:
        await DashboardService._get(db, dashboard_id, user_id)
        result = await db.execute(select(Widget).where(Widget.dashboard_id == dashboard_id).order_by(Widget.created_at))
        return list(result.scalars().all())

    @staticmethod
    async def create_widget(db: AsyncSession, user_id: UUID, dashboard_id: UUID, data: WidgetCreate) -> Widget:
        dashboard = await DashboardService._get(db, dashboard_id, user_id)
        if dashboard.owner_id != user_id:
            raise HTTPException(403, "Only the dashboard owner can manage widgets")
        stream = await DatastreamService.get_for_user(db, data.datastream_id, user_id)
        from app.modules.devices.service import DeviceService
        device = await DeviceService.get_for_user(db, stream.device_id, user_id)
        if device.project_id != dashboard.project_id:
            raise HTTPException(400, "Datastream must belong to the dashboard project")
        row = Widget(dashboard_id=dashboard_id, **data.model_dump())
        db.add(row)
        await db.flush()
        await db.refresh(row)
        return row

    @staticmethod
    async def update_widget(db: AsyncSession, user_id: UUID, widget_id: UUID, data: WidgetUpdate) -> Widget:
        row = await db.get(Widget, widget_id)
        if not row:
            raise HTTPException(404, "Widget not found")
        dashboard = await DashboardService._get(db, row.dashboard_id, user_id)
        if dashboard.owner_id != user_id:
            raise HTTPException(403, "Only the dashboard owner can manage widgets")
        changes = data.model_dump(exclude_unset=True)
        if "datastream_id" in changes:
            stream = await DatastreamService.get_for_user(db, changes["datastream_id"], user_id)
            from app.modules.devices.service import DeviceService
            device = await DeviceService.get_for_user(db, stream.device_id, user_id)
            if device.project_id != dashboard.project_id:
                raise HTTPException(400, "Datastream must belong to the dashboard project")
        for key, value in changes.items():
            setattr(row, key, value)
        await db.flush()
        await db.refresh(row)
        return row

    @staticmethod
    async def delete_widget(db: AsyncSession, user_id: UUID, widget_id: UUID) -> None:
        row = await db.get(Widget, widget_id)
        if not row:
            raise HTTPException(404, "Widget not found")
        dashboard = await DashboardService._get(db, row.dashboard_id, user_id)
        if dashboard.owner_id != user_id:
            raise HTTPException(403, "Only the dashboard owner can manage widgets")
        await db.delete(row)
        await db.flush()
