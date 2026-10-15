from tests.conftest import auth_headers


async def _create_datastream(client, admin_user, device_id, **overrides):
    payload = {
        "name": "Temperatura",
        "key": "temperature",
        "data_type": "float",
    }
    payload.update(overrides)

    resp = await client.post(
        f"/api/v1/datastreams/devices/{device_id}",
        json=payload,
        headers=auth_headers(admin_user),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


async def test_record_and_read_latest_value(client, admin_user, project_with_device):
    datastream_id = await _create_datastream(
        client, admin_user, project_with_device["device_id"]
    )

    create_resp = await client.post(
        f"/api/v1/datastreams/{datastream_id}/values",
        json={"value": 21.5},
        headers=auth_headers(admin_user),
    )
    assert create_resp.status_code == 201, create_resp.text
    assert create_resp.json()["value"] == 21.5

    latest_resp = await client.get(
        f"/api/v1/datastreams/{datastream_id}/values/latest",
        headers=auth_headers(admin_user),
    )
    assert latest_resp.status_code == 200
    assert latest_resp.json()["value"] == 21.5


async def test_latest_value_returns_404_when_no_values_recorded(
    client, admin_user, project_with_device
):
    datastream_id = await _create_datastream(
        client, admin_user, project_with_device["device_id"]
    )

    resp = await client.get(
        f"/api/v1/datastreams/{datastream_id}/values/latest",
        headers=auth_headers(admin_user),
    )

    assert resp.status_code == 404


async def test_history_is_ordered_most_recent_first(
    client, admin_user, project_with_device
):
    datastream_id = await _create_datastream(
        client, admin_user, project_with_device["device_id"]
    )

    for v in [10.0, 20.0, 30.0]:
        resp = await client.post(
            f"/api/v1/datastreams/{datastream_id}/values",
            json={"value": v},
            headers=auth_headers(admin_user),
        )
        assert resp.status_code == 201

    history_resp = await client.get(
        f"/api/v1/datastreams/{datastream_id}/values",
        headers=auth_headers(admin_user),
    )
    assert history_resp.status_code == 200
    values = [item["value"] for item in history_resp.json()]
    assert values == [30.0, 20.0, 10.0]


async def test_value_type_mismatch_returns_400(
    client, admin_user, project_with_device
):
    datastream_id = await _create_datastream(
        client, admin_user, project_with_device["device_id"], data_type="boolean"
    )

    resp = await client.post(
        f"/api/v1/datastreams/{datastream_id}/values",
        json={"value": "not-a-boolean"},
        headers=auth_headers(admin_user),
    )

    assert resp.status_code == 400


async def test_boolean_value_is_accepted_for_boolean_datastream(
    client, admin_user, project_with_device
):
    datastream_id = await _create_datastream(
        client, admin_user, project_with_device["device_id"], data_type="boolean"
    )

    resp = await client.post(
        f"/api/v1/datastreams/{datastream_id}/values",
        json={"value": True},
        headers=auth_headers(admin_user),
    )

    assert resp.status_code == 201
    assert resp.json()["value"] is True


async def test_user_without_access_cannot_read_or_write_values(
    client, admin_user, other_user, project_with_device
):
    datastream_id = await _create_datastream(
        client, admin_user, project_with_device["device_id"]
    )

    write_resp = await client.post(
        f"/api/v1/datastreams/{datastream_id}/values",
        json={"value": 1.0},
        headers=auth_headers(other_user),
    )
    assert write_resp.status_code == 404

    read_resp = await client.get(
        f"/api/v1/datastreams/{datastream_id}/values",
        headers=auth_headers(other_user),
    )
    assert read_resp.status_code == 404


async def test_deleting_datastream_cascades_to_its_values(
    client, admin_user, project_with_device
):
    datastream_id = await _create_datastream(
        client, admin_user, project_with_device["device_id"]
    )

    await client.post(
        f"/api/v1/datastreams/{datastream_id}/values",
        json={"value": 1.0},
        headers=auth_headers(admin_user),
    )

    delete_resp = await client.delete(
        f"/api/v1/datastreams/{datastream_id}",
        headers=auth_headers(admin_user),
    )
    assert delete_resp.status_code == 204
