from tests.conftest import auth_headers
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.modules.automation.model import DeviceCommand
from app.modules.mqtt.commands import publish_pending_commands


async def _create_datastream(client, user, device_id, data_type="float", key="temperature"):
    response = await client.post(
        f"/api/v1/datastreams/devices/{device_id}",
        json={"name": key.title(), "key": key, "data_type": data_type},
        headers=auth_headers(user),
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


async def test_matching_value_creates_notification_and_cooldown_suppresses_repeat(
    client, admin_user, project_with_device
):
    headers = auth_headers(admin_user)
    stream_id = await _create_datastream(
        client, admin_user, project_with_device["device_id"]
    )
    rule = await client.post(
        "/api/v1/automations",
        json={
            "project_id": project_with_device["project_id"],
            "datastream_id": stream_id,
            "name": "Temperatura elevada",
            "operator": ">",
            "threshold": 30,
            "cooldown_seconds": 3600,
        },
        headers=headers,
    )
    assert rule.status_code == 201, rule.text

    for value in (35, 40):
        saved = await client.post(
            f"/api/v1/datastreams/{stream_id}/values",
            json={"value": value},
            headers=headers,
        )
        assert saved.status_code == 201, saved.text

    notifications = await client.get("/api/v1/notifications", headers=headers)
    assert notifications.status_code == 200
    assert len(notifications.json()) == 1
    notification_id = notifications.json()[0]["id"]
    read = await client.patch(
        f"/api/v1/notifications/{notification_id}",
        json={"read": True},
        headers=headers,
    )
    assert read.status_code == 200
    assert read.json()["read_at"] is not None


async def test_automation_requires_numeric_datastream(
    client, admin_user, project_with_device
):
    headers = auth_headers(admin_user)
    stream_id = await _create_datastream(
        client, admin_user, project_with_device["device_id"], "boolean"
    )
    response = await client.post(
        "/api/v1/automations",
        json={
            "project_id": project_with_device["project_id"],
            "datastream_id": stream_id,
            "name": "Estado ligado",
            "operator": ">",
            "threshold": 1,
        },
        headers=headers,
    )
    assert response.status_code == 400


async def test_user_without_project_access_cannot_create_automation(
    client, admin_user, other_user, project_with_device
):
    stream_id = await _create_datastream(
        client, admin_user, project_with_device["device_id"]
    )
    response = await client.post(
        "/api/v1/automations",
        json={
            "project_id": project_with_device["project_id"],
            "datastream_id": stream_id,
            "name": "Regra",
            "operator": ">",
            "threshold": 10,
        },
        headers=auth_headers(other_user),
    )
    assert response.status_code == 404


async def test_matching_rule_queues_and_publishes_device_command(
    client, db_session, admin_user, project_with_device
):
    headers = auth_headers(admin_user)
    source_id = await _create_datastream(client, admin_user, project_with_device["device_id"])
    target_id = await _create_datastream(
        client, admin_user, project_with_device["device_id"], "boolean", "relay"
    )
    rule = await client.post(
        "/api/v1/automations",
        json={
            "project_id": project_with_device["project_id"],
            "datastream_id": source_id,
            "name": "Ativar relé",
            "operator": ">",
            "threshold": 30,
            "action_type": "control_device",
            "target_datastream_id": target_id,
            "action_value": True,
        },
        headers=headers,
    )
    assert rule.status_code == 201, rule.text

    sample = await client.post(
        f"/api/v1/datastreams/{source_id}/values",
        json={"value": 35},
        headers=headers,
    )
    assert sample.status_code == 201, sample.text
    await db_session.commit()

    queued = await db_session.execute(select(DeviceCommand))
    command = queued.scalar_one()
    assert command.status == "pending"
    assert command.value is True

    class FakeMqttClient:
        published: list[tuple[str, str, int]] = []

        async def publish(self, topic, payload, qos, retain):
            self.published.append((topic, payload, qos))

    fake_client = FakeMqttClient()
    session_factory = async_sessionmaker(bind=db_session.bind, expire_on_commit=False)
    count = await publish_pending_commands(fake_client, session_factory)
    assert count == 1
    topic, payload, qos = fake_client.published[0]
    assert topic == f"ciao/devices/{project_with_device['device_uuid']}/commands/relay"
    assert '"value": true' in payload
    assert qos == 1

    await db_session.refresh(command)
    assert command.status == "delivered"
