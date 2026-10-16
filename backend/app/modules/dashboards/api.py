from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.dashboards.schema import (
    DashboardCreate, DashboardResponse, DashboardUpdate,
    WidgetCreate, WidgetResponse, WidgetUpdate,
)
from app.modules.dashboards.service import DashboardService
from app.modules.identity.dependencies import get_current_user
from app.modules.identity.model import User

router = APIRouter()


@router.post("", response_model=DashboardResponse, status_code=status.HTTP_201_CREATED)
async def create_dashboard(data: DashboardCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await DashboardService.create(db, user.id, data)


@router.get("/projects/{project_id}", response_model=list[DashboardResponse])
async def list_dashboards(project_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await DashboardService.list_for_project(db, user.id, project_id)


@router.get("/{dashboard_id}", response_model=DashboardResponse)
async def get_dashboard(dashboard_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await DashboardService.get(db, user.id, dashboard_id)


@router.patch("/{dashboard_id}", response_model=DashboardResponse)
async def update_dashboard(dashboard_id: UUID, data: DashboardUpdate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await DashboardService.update(db, user.id, dashboard_id, data)


@router.delete("/{dashboard_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dashboard(dashboard_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    await DashboardService.delete(db, user.id, dashboard_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{dashboard_id}/widgets", response_model=WidgetResponse, status_code=status.HTTP_201_CREATED)
async def create_widget(dashboard_id: UUID, data: WidgetCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await DashboardService.create_widget(db, user.id, dashboard_id, data)


@router.get("/{dashboard_id}/widgets", response_model=list[WidgetResponse])
async def list_widgets(dashboard_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await DashboardService.list_widgets(db, user.id, dashboard_id)


@router.patch("/widgets/{widget_id}", response_model=WidgetResponse)
async def update_widget(widget_id: UUID, data: WidgetUpdate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await DashboardService.update_widget(db, user.id, widget_id, data)


@router.delete("/widgets/{widget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_widget(widget_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    await DashboardService.delete_widget(db, user.id, widget_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
