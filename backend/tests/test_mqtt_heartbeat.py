from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import update

from app.modules.devices.model import Device
from app.modules.mqtt.heartbeat import mark_stale_devices_offline


async def test_stale_online_device_is_marked_offline(
    client, db_session, admin_user, project_with_device
):
    now = datetime.now(timezone.utc)
    device_id = UUID(project_with_device["device_id"])
    await db_session.execute(
        update(Device)
        .where(Device.id == device_id)
        .values(status="online", last_seen=now - timedelta(seconds=121))
    )

    changed = await mark_stale_devices_offline(
        db_session, now=now, timeout_seconds=120
    )
    assert changed == 1

    response = await client.get(
        f"/api/v1/devices/{device_id}",
        headers={"Authorization": f"Bearer {admin_user['token']}"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "offline"


async def test_recent_heartbeat_keeps_device_online(
    db_session, project_with_device
):
    now = datetime.now(timezone.utc)
    device_id = UUID(project_with_device["device_id"])
    await db_session.execute(
        update(Device)
        .where(Device.id == device_id)
        .values(status="online", last_seen=now - timedelta(seconds=60))
    )

    changed = await mark_stale_devices_offline(
        db_session, now=now, timeout_seconds=120
    )
    assert changed == 0
    device = await db_session.get(Device, device_id)
    assert device.status == "online"
