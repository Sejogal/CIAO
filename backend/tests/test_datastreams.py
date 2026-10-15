from tests.conftest import auth_headers


async def _create_datastream(client, admin_user, device_id, **overrides):
    payload = {
        "name": "Temperatura",
        "key": "temperature",
        "data_type": "float",
        "unit": "C",
        "min_value": -10,
        "max_value": 60,
    }
    payload.update(overrides)

    return await client.post(
        f"/api/v1/datastreams/devices/{device_id}",
        json=payload,
        headers=auth_headers(admin_user),
    )


async def test_create_datastream(client, admin_user, project_with_device):
    resp = await _create_datastream(
        client, admin_user, project_with_device["device_id"]
    )

    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["key"] == "temperature"
    assert body["device_id"] == project_with_device["device_id"]
    assert body["is_active"] is True


async def test_list_datastreams_by_device(client, admin_user, project_with_device):
    device_id = project_with_device["device_id"]
    await _create_datastream(client, admin_user, device_id)

    resp = await client.get(
        f"/api/v1/datastreams/devices/{device_id}",
        headers=auth_headers(admin_user),
    )

    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 1
    assert body[0]["key"] == "temperature"


async def test_get_datastream_by_id(client, admin_user, project_with_device):
    device_id = project_with_device["device_id"]
    create_resp = await _create_datastream(client, admin_user, device_id)
    datastream_id = create_resp.json()["id"]

    resp = await client.get(
        f"/api/v1/datastreams/{datastream_id}",
        headers=auth_headers(admin_user),
    )

    assert resp.status_code == 200
    assert resp.json()["id"] == datastream_id


async def test_update_datastream(client, admin_user, project_with_device):
    device_id = project_with_device["device_id"]
    create_resp = await _create_datastream(client, admin_user, device_id)
    datastream_id = create_resp.json()["id"]

    resp = await client.patch(
        f"/api/v1/datastreams/{datastream_id}",
        json={"unit": "Celsius"},
        headers=auth_headers(admin_user),
    )

    assert resp.status_code == 200
    assert resp.json()["unit"] == "Celsius"


async def test_delete_datastream(client, admin_user, project_with_device):
    device_id = project_with_device["device_id"]
    create_resp = await _create_datastream(client, admin_user, device_id)
    datastream_id = create_resp.json()["id"]

    delete_resp = await client.delete(
        f"/api/v1/datastreams/{datastream_id}",
        headers=auth_headers(admin_user),
    )
    assert delete_resp.status_code == 204

    get_resp = await client.get(
        f"/api/v1/datastreams/{datastream_id}",
        headers=auth_headers(admin_user),
    )
    assert get_resp.status_code == 404


async def test_duplicate_key_returns_409(client, admin_user, project_with_device):
    device_id = project_with_device["device_id"]
    first = await _create_datastream(client, admin_user, device_id)
    assert first.status_code == 201

    second = await _create_datastream(
        client, admin_user, device_id, name="Temperatura Duplicada"
    )

    assert second.status_code == 409


async def test_update_to_duplicate_key_returns_409(
    client, admin_user, project_with_device
):
    device_id = project_with_device["device_id"]
    await _create_datastream(client, admin_user, device_id)

    second = await _create_datastream(
        client, admin_user, device_id, name="Humidade", key="humidity"
    )
    humidity_id = second.json()["id"]

    resp = await client.patch(
        f"/api/v1/datastreams/{humidity_id}",
        json={"key": "temperature"},
        headers=auth_headers(admin_user),
    )

    assert resp.status_code == 409


async def test_min_greater_than_max_returns_400(
    client, admin_user, project_with_device
):
    resp = await _create_datastream(
        client,
        admin_user,
        project_with_device["device_id"],
        min_value=100,
        max_value=0,
    )

    assert resp.status_code == 400


async def test_update_min_greater_than_max_returns_400(
    client, admin_user, project_with_device
):
    device_id = project_with_device["device_id"]
    create_resp = await _create_datastream(
        client, admin_user, device_id, min_value=0, max_value=50
    )
    datastream_id = create_resp.json()["id"]

    resp = await client.patch(
        f"/api/v1/datastreams/{datastream_id}",
        json={"min_value": 100},
        headers=auth_headers(admin_user),
    )

    assert resp.status_code == 400


async def test_user_without_project_access_cannot_read_datastream(
    client, admin_user, other_user, project_with_device
):
    device_id = project_with_device["device_id"]
    create_resp = await _create_datastream(client, admin_user, device_id)
    datastream_id = create_resp.json()["id"]

    resp = await client.get(
        f"/api/v1/datastreams/{datastream_id}",
        headers=auth_headers(other_user),
    )

    assert resp.status_code == 404


async def test_user_without_project_access_cannot_list_datastreams(
    client, admin_user, other_user, project_with_device
):
    device_id = project_with_device["device_id"]
    await _create_datastream(client, admin_user, device_id)

    resp = await client.get(
        f"/api/v1/datastreams/devices/{device_id}",
        headers=auth_headers(other_user),
    )

    assert resp.status_code == 404


async def test_device_response_never_exposes_secrets(
    client, admin_user, project_with_device
):
    resp = await client.get(
        f"/api/v1/devices/{project_with_device['device_id']}",
        headers=auth_headers(admin_user),
    )

    assert resp.status_code == 200
    body = resp.json()
    assert "token" not in body
    assert "mqtt_password" not in body
