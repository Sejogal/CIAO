from tests.conftest import auth_headers


async def test_new_user_gets_default_role_once_rbac_is_seeded(
    client, rbac_seeded
):
    register_resp = await client.post(
        "/api/v1/identity/register",
        json={
            "full_name": "Default Role User",
            "email": "default.role@example.com",
            "password": "TestPass123!",
        },
    )
    assert register_resp.status_code == 201

    login_resp = await client.post(
        "/api/v1/identity/login",
        data={
            "username": "default.role@example.com",
            "password": "TestPass123!",
        },
    )
    token = login_resp.json()["access_token"]

    # the default "user" role grants companies:read
    resp = await client.get(
        "/api/v1/companies/companies",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200


async def test_admin_can_promote_user_to_another_role(
    client, admin_user, regular_user
):
    resp = await client.patch(
        f"/api/v1/identity/users/{regular_user['id']}/role",
        json={"role_name": "teacher"},
        headers=auth_headers(admin_user),
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["role"]["name"] == "teacher"
    assert "companies:create" in body["permissions"]


async def test_promote_to_unknown_role_returns_400(
    client, admin_user, regular_user
):
    resp = await client.patch(
        f"/api/v1/identity/users/{regular_user['id']}/role",
        json={"role_name": "superhero"},
        headers=auth_headers(admin_user),
    )

    assert resp.status_code == 400


async def test_non_admin_cannot_promote_users(
    client, regular_user, other_user, admin_user
):
    resp = await client.patch(
        f"/api/v1/identity/users/{other_user['id']}/role",
        json={"role_name": "teacher"},
        headers=auth_headers(regular_user),
    )

    assert resp.status_code == 403


async def test_promoted_user_can_use_new_permissions(
    client, admin_user, regular_user
):
    promote_resp = await client.patch(
        f"/api/v1/identity/users/{regular_user['id']}/role",
        json={"role_name": "teacher"},
        headers=auth_headers(admin_user),
    )
    assert promote_resp.status_code == 200

    create_resp = await client.post(
        "/api/v1/companies/companies",
        json={"name": "Teacher's Company"},
        headers=auth_headers(regular_user),
    )

    assert create_resp.status_code == 201
