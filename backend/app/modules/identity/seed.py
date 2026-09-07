from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.identity.role_model import Role
from app.modules.identity.role_permission_model import RolePermission
from app.modules.identity.permission_model import Permission


DEFAULT_PERMISSIONS = [
    ("users:read", "Visualizar utilizadores"),
    ("users:create", "Criar utilizadores"),
    ("users:update", "Atualizar utilizadores"),
    ("users:delete", "Eliminar utilizadores"),

    ("projects:read", "Visualizar projetos"),
    ("projects:create", "Criar projetos"),
    ("projects:update", "Atualizar projetos"),
    ("projects:delete", "Eliminar projetos"),

    ("devices:read", "Visualizar dispositivos"),
    ("devices:create", "Criar dispositivos"),
    ("devices:update", "Atualizar dispositivos"),
    ("devices:delete", "Eliminar dispositivos"),
]


DEFAULT_ROLES = {
    "admin": [
        "users:read",
        "users:create",
        "users:update",
        "users:delete",
        "projects:read",
        "projects:create",
        "projects:update",
        "projects:delete",
        "devices:read",
        "devices:create",
        "devices:update",
        "devices:delete",
        "companies:create",
        "companies:read",
        "companies:update",
        "companies:manage_members"
    ],
    "user": [
        "projects:read",
        "projects:create",
        "projects:update",
        "devices:read",
        "devices:create",
        "devices:update",
    ],
    "student": [
        "projects:read",
        "projects:create",
        "devices:read",
        "companies:create",
        "companies:read"
    ],
    "teacher": [
        "projects:read",
        "projects:create",
        "projects:update",
        "devices:read",
        "devices:create",
        "devices:update",
    ],
}


async def seed_rbac(db: AsyncSession):
    permissions = {}

    for name, description in DEFAULT_PERMISSIONS:
        result = await db.execute(
            select(Permission).where(Permission.name == name)
        )

        permission = result.scalar_one_or_none()

        if not permission:
            permission = Permission(
                name=name,
                description=description,
            )

            db.add(permission)
            await db.flush()

        permissions[name] = permission

    for role_name, permission_names in DEFAULT_ROLES.items():
        result = await db.execute(
            select(Role).where(Role.name == role_name)
        )

        role = result.scalar_one_or_none()

        if not role:
            role = Role(
                name=role_name,
                description=f"Role padrão: {role_name}",
            )

            db.add(role)
            await db.flush()

        for permission_name in permission_names:
            permission = permissions[permission_name]

            result = await db.execute(
                select(RolePermission).where(
                    RolePermission.role_id == role.id,
                    RolePermission.permission_id == permission.id,
                )
            )

            existing = result.scalar_one_or_none()

            if not existing:
                db.add(
                    RolePermission(
                        role_id=role.id,
                        permission_id=permission.id,
                    )
                )

    await db.commit()