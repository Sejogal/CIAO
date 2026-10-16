from tests.conftest import auth_headers


async def _create_datastream(client, user, device_id, *, key="temperature"):
    response = await client.post(
        f"/api/v1/datastreams/devices/{device_id}",
        json={"name": key.title(), "key": key, "data_type": "float"},
        headers=auth_headers(user),
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


async def test_dashboard_and_widget_crud(client, admin_user, project_with_device):
    headers = auth_headers(admin_user)
    stream_id = await _create_datastream(
        client, admin_user, project_with_device["device_id"]
    )

    created = await client.post(
        "/api/v1/dashboards",
        json={"project_id": project_with_device["project_id"], "name": "Sala"},
        headers=headers,
    )
    assert created.status_code == 201, created.text
    dashboard_id = created.json()["id"]

    widget = await client.post(
        f"/api/v1/dashboards/{dashboard_id}/widgets",
        json={"datastream_id": stream_id, "name": "Temperatura", "widget_type": "chart"},
        headers=headers,
    )
    assert widget.status_code == 201, widget.text
    assert widget.json()["datastream_id"] == stream_id

    listing = await client.get(
        f"/api/v1/dashboards/{dashboard_id}/widgets", headers=headers
    )
    assert listing.status_code == 200
    assert [item["id"] for item in listing.json()] == [widget.json()["id"]]

    removed = await client.delete(
        f"/api/v1/dashboards/widgets/{widget.json()['id']}", headers=headers
    )
    assert removed.status_code == 204


async def test_dashboard_rejects_datastream_from_another_project(
    client, admin_user, project_with_device
):
    headers = auth_headers(admin_user)
    other_project = await client.post(
        "/api/v1/projects/projects",
        json={"name": "Outro projeto", "company_id": project_with_device["company_id"]},
        headers=headers,
    )
    assert other_project.status_code == 201, other_project.text
    other_device = await client.post(
        f"/api/v1/devices/projects/{other_project.json()['id']}",
        json={"name": "Outro dispositivo"},
        headers=headers,
    )
    assert other_device.status_code == 201, other_device.text
    stream_id = await _create_datastream(client, admin_user, other_device.json()["id"])
    dashboard = await client.post(
        "/api/v1/dashboards",
        json={"project_id": project_with_device["project_id"], "name": "Sala"},
        headers=headers,
    )
    assert dashboard.status_code == 201
    result = await client.post(
        f"/api/v1/dashboards/{dashboard.json()['id']}/widgets",
        json={"datastream_id": stream_id, "name": "Widget", "widget_type": "value"},
        headers=headers,
    )
    assert result.status_code == 400
