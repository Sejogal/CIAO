import asyncio

from app.db.session import SessionLocal
from app.modules.identity.rbac_seed import seed_rbac


async def main():
    async with SessionLocal() as db:
        await seed_rbac(db)

    print("RBAC seed concluído com sucesso.")


if __name__ == "__main__":
    asyncio.run(main())