from tests.conftest import auth_headers


async def test_register_and_login(client):
    register_resp = await client.post(
        "/api/v1/identity/register",
        json={
            "full_name": "Jane Doe",
            "email": "jane.doe@example.com",
            "password": "TestPass123!",
        },
    )
    assert register_resp.status_code == 201
    assert "id" in register_resp.json()

    login_resp = await client.post(
        "/api/v1/identity/login",
        data={
            "username": "jane.doe@example.com",
            "password": "TestPass123!",
        },
    )
    assert login_resp.status_code == 200
    assert "access_token" in login_resp.json()


async def test_duplicate_email_registration_is_rejected(client):
    payload = {
        "full_name": "Jane Doe",
        "email": "jane.doe@example.com",
        "password": "TestPass123!",
    }

    first = await client.post("/api/v1/identity/register", json=payload)
    assert first.status_code == 201

    second = await client.post("/api/v1/identity/register", json=payload)
    assert second.status_code == 400


async def test_new_user_has_no_role_and_cannot_create_company(client, regular_user):
    resp = await client.post(
        "/api/v1/companies/companies",
        json={"name": "Should Fail"},
        headers=auth_headers(regular_user),
    )

    assert resp.status_code == 403
    assert resp.json()["detail"] == "User has no assigned role"


async def test_admin_can_create_company_project_and_device(
    client, project_with_device
):
    assert project_with_device["company_id"]
    assert project_with_device["project_id"]
    assert project_with_device["device_id"]


async def test_identity_service_and_device_routes_share_the_same_db_session(
    client, admin_user, project_with_device
):
    """
    Regression test for a real bug: devices/datastreams routes used to import
    get_db from app.db.session while get_current_user (and every other
    module) used a second, separate get_db from app.db.dependencies. Under
    the test override only one of the two was patched, so current_user was
    resolved against the test's isolated session while the route body ran
    against the real, persistent app engine - a project created in the same
    request chain was invisible to the device-ownership check, and reusing
    that persistent engine's pool across pytest's per-test event loops
    corrupted the asyncpg connection ("another operation is in progress").
    Both modules now import get_db from the same place (app.db.session), so
    a single request's current_user and db-dependent business logic always
    see the same transaction/connection.
    """
    device_resp = await client.get(
        f"/api/v1/devices/{project_with_device['device_id']}",
        headers=auth_headers(admin_user),
    )

    assert device_resp.status_code == 200
