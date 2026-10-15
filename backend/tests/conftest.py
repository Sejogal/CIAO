import asyncio
import os
import sys
from pathlib import Path

os.environ["DB_NAME"] = "ciao_test"

if sys.platform == "win32":
    # asyncpg + ProactorEventLoop under pytest-asyncio's per-test event
    # loops causes spurious "another operation is in progress" errors on
    # Windows once more than one test runs; the selector loop doesn't.
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.modules.identity.role_model import Role

BACKEND_DIR = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session", autouse=True)
def _migrate_test_database():
    alembic_cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    command.upgrade(alembic_cfg, "head")
    yield


@pytest_asyncio.fixture
async def db_session():
    # Function-scoped engine: pytest-asyncio gives each test its own event
    # loop, and asyncpg connections can't be reused across event loops, so
    # the engine (and its pool) must not outlive a single test.
    engine = create_async_engine(settings.database_url, future=True)

    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())

    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session):
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


async def _register_and_login(
    client: AsyncClient,
    email: str,
    full_name: str = "Test User",
    password: str = "TestPass123!",
) -> dict:
    register_resp = await client.post(
        "/api/v1/identity/register",
        json={
            "full_name": full_name,
            "email": email,
            "password": password,
        },
    )
    assert register_resp.status_code == 201, register_resp.text

    user_id = register_resp.json()["id"]

    login_resp = await client.post(
        "/api/v1/identity/login",
        data={"username": email, "password": password},
    )
    assert login_resp.status_code == 200, login_resp.text

    token = login_resp.json()["access_token"]

    return {"id": user_id, "token": token}


@pytest_asyncio.fixture
async def rbac_seeded(db_session):
    from app.modules.identity.seed import seed_rbac

    await seed_rbac(db_session)


@pytest_asyncio.fixture
async def regular_user(client):
    return await _register_and_login(
        client,
        email="user.regular@example.com",
        full_name="Regular User",
    )


@pytest_asyncio.fixture
async def other_user(client):
    return await _register_and_login(
        client,
        email="user.other@example.com",
        full_name="Other User",
    )


@pytest_asyncio.fixture
async def admin_user(client, db_session, rbac_seeded):
    user = await _register_and_login(
        client,
        email="user.admin@example.com",
        full_name="Admin User",
    )

    result = await db_session.execute(
        select(Role).where(Role.name == "admin")
    )
    admin_role = result.scalar_one()

    await db_session.execute(
        text("UPDATE users SET role_id = :role_id WHERE id = :user_id"),
        {"role_id": str(admin_role.id), "user_id": user["id"]},
    )
    await db_session.commit()

    return user


def auth_headers(user: dict) -> dict:
    return {"Authorization": f"Bearer {user['token']}"}


@pytest_asyncio.fixture
async def project_with_device(client, admin_user):
    company_resp = await client.post(
        "/api/v1/companies/companies",
        json={"name": "Test Company"},
        headers=auth_headers(admin_user),
    )
    assert company_resp.status_code == 201, company_resp.text
    company_id = company_resp.json()["id"]

    project_resp = await client.post(
        "/api/v1/projects/projects",
        json={"name": "Test Project", "company_id": company_id},
        headers=auth_headers(admin_user),
    )
    assert project_resp.status_code == 201, project_resp.text
    project_id = project_resp.json()["id"]

    device_resp = await client.post(
        f"/api/v1/devices/projects/{project_id}",
        json={"name": "Test Device"},
        headers=auth_headers(admin_user),
    )
    assert device_resp.status_code == 201, device_resp.text
    device_body = device_resp.json()

    return {
        "company_id": company_id,
        "project_id": project_id,
        "device_id": device_body["id"],
        "device_uuid": device_body["uuid"],
        "device_token": device_body["token"],
    }
