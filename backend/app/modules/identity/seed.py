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

    ("datastreams:read", "Visualizar datastreams"),
    ("datastreams:create", "Criar datastreams"),
    ("datastreams:update", "Atualizar datastreams"),
    ("datastreams:delete", "Eliminar datastreams"),

    
    ("companies:create", "Criar empresas"),
    ("companies:read", "Visualizar empresas"),
    ("companies:update", "Atualizar empresas"),
    ("companies:manage_members", "Gerir membros da empresa"),
    ("companies:delete", "Eliminar empresas")
]


DEFAULT_ROLES = {
    "admin": {
        "description": "Administrador da plataforma",
        "permissions": [
            "projects:read",
            "projects:create",
            "projects:update",
            "projects:delete",

            "devices:read",
            "devices:create",
            "devices:update",
            "devices:delete",

            "datastreams:read",
            "datastreams:create",
            "datastreams:update",
            "datastreams:delete",

            "users:read",
            "users:create",
            "users:update",
            "users:delete",

            "companies:read",
            "companies:create",
            "companies:update",
            "companies:delete",
            "companies:manage_members",
        ],
    },

    "student": {
        "description": "Role padrão: student",
        "permissions": [
            "projects:read",
            "projects:create",
            "devices:read",
            "datastreams:read",

            "companies:read",
            "companies:create",
        ],
    },

    "teacher": {
        "description": "Role padrão: teacher",
        "permissions": [
            "projects:read",
            "projects:create",
            "projects:update",

            "devices:read",
            "devices:create",
            "devices:update",

            "datastreams:read",
            "datastreams:create",
            "datastreams:update",

            "companies:read",
            "companies:create",
            "companies:update",
            "companies:manage_members",
        ],
    },

    "user": {
        "description": "Role padrão: user",
        "permissions": [
            "devices:read",
            "devices:create",
            "devices:update",

            "datastreams:read",
            "datastreams:create",
            "datastreams:update",

            "companies:read",
            # Um utilizador recém-registado (app móvel) tem de conseguir
            # criar a sua própria empresa para começar a usar a
            # plataforma - sem isto ficava preso logo no onboarding.
            "companies:create",
            "projects:read",
            "projects:create",
        ],
    },
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

    for role_name, role_data in DEFAULT_ROLES.items():
        result = await db.execute(
            select(Role).where(Role.name == role_name)
        )

        role = result.scalar_one_or_none()

        if not role:
            role = Role(
                name=role_name,
                description=role_data["description"],
            )

            db.add(role)
            await db.flush()

        for permission_name in role_data["permissions"]:
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
