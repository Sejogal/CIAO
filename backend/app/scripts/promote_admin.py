import asyncio
import sys

from sqlalchemy import select

from app.db.session import SessionLocal
from app.modules.identity.model import User
from app.modules.identity.role_model import Role


async def promote(email: str) -> None:
    async with SessionLocal() as db:
        user_result = await db.execute(
            select(User).where(User.email == email)
        )
        user = user_result.scalar_one_or_none()

        if not user:
            print(f"No user found with email '{email}'.")
            return

        role_result = await db.execute(
            select(Role).where(Role.name == "admin")
        )
        admin_role = role_result.scalar_one_or_none()

        if not admin_role:
            print(
                "Role 'admin' does not exist yet. "
                "Call POST /api/v1/identity/seed-rbac first."
            )
            return

        user.role_id = admin_role.id
        await db.commit()

        print(f"'{email}' is now an admin.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m app.scripts.promote_admin <email>")
        sys.exit(1)

    asyncio.run(promote(sys.argv[1]))
