from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.identity.permission_model import Permission
from app.modules.identity.role_model import Role


PERMISSIONS = [
    ("users:read", "Visualizar utilizadores"),
    ("users:create", "Criar utilizadores"),
    ("users:update", "Atualizar utilizadores"),
    ("users:delete", "Eliminar utilizadores"),

    ("roles:read", "Visualizar roles"),
    ("roles:create", "Criar roles"),
    ("roles:update", "Atualizar roles"),
    ("roles:delete", "Eliminar roles"),

    ("permissions:read", "Visualizar permissões"),
    ("permissions:create", "Criar permissões"),
    ("permissions:update", "Atualizar permissões"),
    ("permissions:delete", "Eliminar permissões"),

    ("devices:read", "Visualizar dispositivos"),
    ("devices:create", "Criar dispositivos"),
    ("devices:update", "Atualizar dispositivos"),
    ("devices:delete", "Eliminar dispositivos"),

    ("projects:read", "Visualizar projetos"),
    ("projects:create", "Criar projetos"),
    ("projects:update", "Atualizar projetos"),
    ("projects:delete", "Eliminar projetos"),
]


ROLES = [
    ("admin", "Administrador do sistema"),
    ("user", "Utilizador normal"),
]


async def seed_rbac(db: AsyncSession):
    permissions_by_name = {}

    # Criar permissions
    for name, description in PERMISSIONS:
        result = await db.execute(
            select(Permission).where(
                Permission.name == name
            )
        )

        permission = result.scalar_one_or_none()

        if not permission:
            permission = Permission(
                name=name,
                description=description,
            )

            db.add(permission)
            await db.flush()

        permissions_by_name[name] = permission

    # Criar roles
    roles_by_name = {}

    for name, description in ROLES:
        result = await db.execute(
            select(Role).where(
                Role.name == name
            )
        )

        role = result.scalar_one_or_none()

        if not role:
            role = Role(
                name=name,
                description=description,
            )

            db.add(role)
            await db.flush()

        roles_by_name[name] = role

    # Admin recebe todas as permissions
    admin_role = roles_by_name["admin"]

    for permission in permissions_by_name.values():
        if permission not in admin_role.permissions:
            admin_role.permissions.append(permission)

    # User recebe apenas permissions básicas
    user_role = roles_by_name["user"]

    basic_permissions = [
        "users:read",
        "devices:read",
        "devices:create",
        "projects:read",
    ]

    for permission_name in basic_permissions:
        permission = permissions_by_name[permission_name]

        if permission not in user_role.permissions:
            user_role.permissions.append(permission)

    await db.commit()