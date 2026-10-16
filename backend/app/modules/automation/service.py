from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.automation.model import AutomationRule, DeviceCommand, Notification
from app.modules.automation.schema import AutomationCreate, AutomationUpdate
from app.modules.datastreams.model import Datastream
from app.modules.devices.model import Device
from app.modules.projects.service import ProjectService


def matches(value: object, operator: str, threshold: float) -> bool:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    if operator == "<":
        return value < threshold
    if operator == ">":
        return value > threshold
    return value == threshold


class AutomationService:
    @staticmethod
    async def _validate_action(
        db: AsyncSession,
        project_id: UUID,
        action_type: str,
        target_datastream_id: UUID | None,
        action_value: object | None,
    ) -> tuple[UUID | None, object | None]:
        if action_type == "notification":
            return None, None
        if target_datastream_id is None or action_value is None:
            raise HTTPException(400, "Device control requires a target datastream and value")
        target = await db.get(Datastream, target_datastream_id)
        device = await db.get(Device, target.device_id) if target else None
        if not target or not device or device.project_id != project_id:
            raise HTTPException(400, "Target datastream must belong to the same project")
        if not target.is_active:
            raise HTTPException(400, "Target datastream is inactive")
        if target.data_type not in {"boolean", "integer", "float", "string"}:
            raise HTTPException(400, "Device commands support boolean, integer, float or string values")
        matches_type = (
            isinstance(action_value, bool) if target.data_type == "boolean"
            else isinstance(action_value, int) and not isinstance(action_value, bool) if target.data_type == "integer"
            else isinstance(action_value, (int, float)) and not isinstance(action_value, bool) if target.data_type == "float"
            else isinstance(action_value, str)
        )
        if not matches_type:
            raise HTTPException(400, "Command value does not match the target datastream type")
        return target_datastream_id, action_value

    @staticmethod
    async def create(db: AsyncSession, user_id: UUID, data: AutomationCreate) -> AutomationRule:
        project = await ProjectService.get_for_user(db, data.project_id, user_id)
        if project.owner_id != user_id:
            raise HTTPException(403, "Only the project owner can manage automation rules")
        stream = await db.get(Datastream, data.datastream_id)
        device = await db.get(Device, stream.device_id) if stream else None
        if not stream or not device or device.project_id != project.id:
            raise HTTPException(400, "Datastream must belong to the selected project")
        if stream.data_type not in {"integer", "float"}:
            raise HTTPException(400, "Automation thresholds require a numeric datastream")
        payload = data.model_dump()
        target_id, action_value = await AutomationService._validate_action(
            db, project.id, payload["action_type"], payload["target_datastream_id"], payload["action_value"]
        )
        payload["target_datastream_id"] = target_id
        payload["action_value"] = action_value
        row = AutomationRule(**payload, owner_id=user_id)
        db.add(row)
        await db.flush()
        await db.refresh(row)
        return row

    @staticmethod
    async def list_for_project(db: AsyncSession, user_id: UUID, project_id: UUID) -> list[AutomationRule]:
        await ProjectService.get_for_user(db, project_id, user_id)
        result = await db.execute(select(AutomationRule).where(AutomationRule.project_id == project_id).order_by(AutomationRule.created_at))
        return list(result.scalars().all())

    @staticmethod
    async def _get_owned(db: AsyncSession, user_id: UUID, rule_id: UUID) -> AutomationRule:
        row = await db.get(AutomationRule, rule_id)
        if not row:
            raise HTTPException(404, "Automation rule not found")
        await ProjectService.get_for_user(db, row.project_id, user_id)
        if row.owner_id != user_id:
            raise HTTPException(403, "Only the rule owner can manage it")
        return row

    @staticmethod
    async def update(db: AsyncSession, user_id: UUID, rule_id: UUID, data: AutomationUpdate) -> AutomationRule:
        row = await AutomationService._get_owned(db, user_id, rule_id)
        changes = data.model_dump(exclude_unset=True)
        action_type = changes.get("action_type", row.action_type)
        target_id = changes.get("target_datastream_id", row.target_datastream_id)
        action_value = changes.get("action_value", row.action_value)
        target_id, action_value = await AutomationService._validate_action(
            db, row.project_id, action_type, target_id, action_value
        )
        changes["target_datastream_id"] = target_id
        changes["action_value"] = action_value
        changes["action_type"] = action_type
        for key, value in changes.items():
            setattr(row, key, value)
        await db.flush()
        await db.refresh(row)
        return row

    @staticmethod
    async def delete(db: AsyncSession, user_id: UUID, rule_id: UUID) -> None:
        row = await AutomationService._get_owned(db, user_id, rule_id)
        await db.delete(row)
        await db.flush()

    @staticmethod
    async def evaluate(db: AsyncSession, datastream_id: UUID, value: object) -> int:
        # Cooldown is measured from when the server processed the sample,
        # not from a possibly delayed device timestamp.
        now = datetime.now(timezone.utc)
        result = await db.execute(
            select(AutomationRule).where(
                AutomationRule.datastream_id == datastream_id,
                AutomationRule.is_active.is_(True),
            ).with_for_update()
        )
        triggered = 0
        for rule in result.scalars().all():
            if not matches(value, rule.operator, rule.threshold):
                continue
            if rule.last_triggered_at and now < rule.last_triggered_at + timedelta(seconds=rule.cooldown_seconds):
                continue
            stream = await db.get(Datastream, datastream_id)
            rule.last_triggered_at = now
            db.add(Notification(
                user_id=rule.owner_id,
                project_id=rule.project_id,
                automation_id=rule.id,
                datastream_id=datastream_id,
                title=rule.name,
                message=f"{stream.name if stream else 'Datastream'}: {value} {rule.operator} {rule.threshold}. {rule.action}",
                level="warning",
            ))
            if rule.action_type == "control_device" and rule.target_datastream_id is not None:
                target_stream = await db.get(Datastream, rule.target_datastream_id)
                target_device = await db.get(Device, target_stream.device_id) if target_stream else None
                if target_stream and target_device and target_device.is_active:
                    db.add(DeviceCommand(
                        project_id=rule.project_id,
                        automation_id=rule.id,
                        datastream_id=target_stream.id,
                        value=rule.action_value,
                        next_attempt_at=now,
                    ))
            triggered += 1
        if triggered:
            await db.flush()
        return triggered


class NotificationService:
    @staticmethod
    async def list_for_user(db: AsyncSession, user_id: UUID, limit: int = 100) -> list[Notification]:
        result = await db.execute(select(Notification).where(Notification.user_id == user_id).order_by(Notification.created_at.desc()).limit(limit))
        return list(result.scalars().all())

    @staticmethod
    async def mark_read(db: AsyncSession, user_id: UUID, notification_id: UUID, read: bool) -> Notification:
        row = await db.get(Notification, notification_id)
        if not row or row.user_id != user_id:
            raise HTTPException(404, "Notification not found")
        row.read_at = datetime.now(timezone.utc) if read else None
        await db.flush()
        await db.refresh(row)
        return row

    @staticmethod
    async def mark_all_read(db: AsyncSession, user_id: UUID) -> None:
        result = await db.execute(select(Notification).where(Notification.user_id == user_id, Notification.read_at.is_(None)))
        now = datetime.now(timezone.utc)
        for row in result.scalars().all():
            row.read_at = now
        await db.flush()
