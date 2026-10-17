from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.identity.dependencies import (
    get_current_user,
    require_permission,
)
from app.modules.identity.model import User

from app.modules.projects.schema import (
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
)
from app.modules.projects.service import ProjectService


router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)

#CRIAR PROJETO
@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(require_permission("projects:create"))
    ],
)

async def create_project(
    data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await ProjectService.create(
        db=db,
        user_id=current_user.id,
        data=data,
    )

#LISTAR TODOS PROJETOS DO USUÁRIO LOGADO
@router.get("", response_model=list[ProjectResponse])
async def list_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_permission("projects:read")
    ),
):
    return await ProjectService.list_for_user(
        db=db,
        user_id=current_user.id,
    )

#OBTER PROJETO POR ID
@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    dependencies=[
        Depends(require_permission("projects:read"))
    ],
)
async def get_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await ProjectService.get_for_user(
        db=db,
        project_id=project_id,
        user_id=current_user.id,
    )

#ATUALIZAR PROJETO
@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
    dependencies=[Depends(require_permission("projects:update"))],
)
async def update_project(
    project_id: UUID,
    data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await ProjectService.update(
        db=db,
        project_id=project_id,
        user_id=current_user.id,
        data=data,
    )


#ELIMINAR PROJETO
@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("projects:delete"))],
)
async def delete_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await ProjectService.delete(
        db=db,
        project_id=project_id,
        user_id=current_user.id,
    )

    return None
