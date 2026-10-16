from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.automation.schema import (
    AutomationCreate, AutomationResponse, AutomationUpdate,
    NotificationReadUpdate, NotificationResponse,
)
from app.modules.automation.service import AutomationService, NotificationService
from app.modules.identity.dependencies import get_current_user
from app.modules.identity.model import User

automation_router = APIRouter()
notification_router = APIRouter()


@automation_router.post("", response_model=AutomationResponse, status_code=status.HTTP_201_CREATED)
async def create_rule(data: AutomationCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await AutomationService.create(db, user.id, data)


@automation_router.get("/projects/{project_id}", response_model=list[AutomationResponse])
async def list_rules(project_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await AutomationService.list_for_project(db, user.id, project_id)


@automation_router.patch("/{rule_id}", response_model=AutomationResponse)
async def update_rule(rule_id: UUID, data: AutomationUpdate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await AutomationService.update(db, user.id, rule_id, data)


@automation_router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(rule_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    await AutomationService.delete(db, user.id, rule_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@notification_router.get("", response_model=list[NotificationResponse])
async def list_notifications(limit: int = Query(default=100, ge=1, le=500), db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await NotificationService.list_for_user(db, user.id, limit)


@notification_router.patch("/{notification_id}", response_model=NotificationResponse)
async def update_notification(notification_id: UUID, data: NotificationReadUpdate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await NotificationService.mark_read(db, user.id, notification_id, data.read)


@notification_router.post("/read-all", status_code=status.HTTP_204_NO_CONTENT)
async def mark_all_read(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    await NotificationService.mark_all_read(db, user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
