from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.identity.role_model import Role
from app.modules.identity.permission_model import Permission


PERMISSIONS = [
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
    ("companies:manage_members", "Gerir membros das empresas")
]


ROLES = {
    "ADMIN": {
        "description": "Administrador do sistema",
        "permissions": [
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
            "datastreams:read",
            "datastreams:create",
            "datastreams:update",
            "datastreams:delete",
            "companies:create",
            "companies:read",
            "companies:update",
            "companies:manage_members"
        ],
    },
    "DEVELOPER": {
        "description": "Desenvolvedor",
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
        ],
    },
    "USER": {
        "description": "Utilizador comum",
        "permissions": [
            "projects:read",
            "devices:read",
            "devices:create",
            "datastreams:read",
        ],
    },
}


async def seed_rbac(db: AsyncSession):
    # -----------------------------------------
    # 1. Criar permissions
    # -----------------------------------------

    permissions_map: dict[str, Permission] = {}

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

        permissions_map[name] = permission

    # -----------------------------------------
    # 2. Criar roles
    # -----------------------------------------

    for role_name, role_data in ROLES.items():

        result = await db.execute(
            select(Role).where(
                Role.name == role_name
            )
        )

        role = result.scalar_one_or_none()

        if not role:
            role = Role(
                name=role_name,
                description=role_data["description"],
            )

            db.add(role)
            await db.flush()

        # -----------------------------------------
        # 3. Associar permissions
        # -----------------------------------------

        for permission_name in role_data["permissions"]:

            permission = permissions_map[permission_name]

            if permission not in role.permissions:
                role.permissions.append(permission)

    await db.commit()