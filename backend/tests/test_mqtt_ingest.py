import json

from tests.conftest import auth_headers

from app.modules.mqtt.ingest import ingest_message
from app.modules.mqtt.topics import build_value_topic, parse_value_topic


def _payload(value, token, **extra):
    return json.dumps({"token": token, "value": value, **extra}).encode()


async def _create_datastream(client, admin_user, device_id, **overrides):
    payload = {"name": "Temperatura", "key": "temperature", "data_type": "float"}
    payload.update(overrides)

    resp = await client.post(
        f"/api/v1/datastreams/devices/{device_id}",
        json=payload,
        headers=auth_headers(admin_user),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def test_build_and_parse_value_topic_round_trip():
    topic = build_value_topic("device-123", "temperature")
    assert topic == "ciao/devices/device-123/datastreams/temperature"
    assert parse_value_topic(topic) == ("device-123", "temperature")


def test_parse_value_topic_rejects_unrelated_topics():
    assert parse_value_topic("ciao/devices/device-123/other") is None
    assert parse_value_topic("not/even/close") is None


async def test_valid_message_creates_a_datastream_value(
    db_session, client, admin_user, project_with_device
):
    device_id = project_with_device["device_id"]
    device_uuid = project_with_device["device_uuid"]
    device_token = project_with_device["device_token"]
    await _create_datastream(client, admin_user, device_id)

    topic = build_value_topic(device_uuid, "temperature")
    result = await ingest_message(
        db=db_session,
        topic=topic,
        payload=_payload(21.5, device_token),
    )

    assert result.ok is True
    assert result.value is not None
    assert result.value.value == 21.5


async def test_wrong_token_is_rejected(
    db_session, client, admin_user, project_with_device
):
    device_id = project_with_device["device_id"]
    device_uuid = project_with_device["device_uuid"]
    await _create_datastream(client, admin_user, device_id)

    topic = build_value_topic(device_uuid, "temperature")
    result = await ingest_message(
        db=db_session,
        topic=topic,
        payload=_payload(21.5, "not-the-real-token"),
    )

    assert result.ok is False
    assert "Invalid token" in result.reason


async def test_unknown_device_is_rejected(db_session):
    topic = build_value_topic("not-a-real-device-uuid", "temperature")
    result = await ingest_message(
        db=db_session,
        topic=topic,
        payload=_payload(21.5, "whatever"),
    )

    assert result.ok is False
    assert "Unknown or inactive device" in result.reason


async def test_unknown_datastream_key_is_rejected(
    db_session, client, admin_user, project_with_device
):
    device_uuid = project_with_device["device_uuid"]
    device_token = project_with_device["device_token"]

    topic = build_value_topic(device_uuid, "does-not-exist")
    result = await ingest_message(
        db=db_session,
        topic=topic,
        payload=_payload(21.5, device_token),
    )

    assert result.ok is False
    assert "Unknown datastream" in result.reason


async def test_value_type_mismatch_is_rejected(
    db_session, client, admin_user, project_with_device
):
    device_id = project_with_device["device_id"]
    device_uuid = project_with_device["device_uuid"]
    device_token = project_with_device["device_token"]
    await _create_datastream(client, admin_user, device_id, data_type="boolean")

    topic = build_value_topic(device_uuid, "temperature")
    result = await ingest_message(
        db=db_session,
        topic=topic,
        payload=_payload("not-a-boolean", device_token),
    )

    assert result.ok is False
    assert "does not match data_type" in result.reason


async def test_malformed_json_is_rejected(db_session):
    topic = build_value_topic("whatever", "temperature")
    result = await ingest_message(db=db_session, topic=topic, payload=b"not json")

    assert result.ok is False
    assert "not valid JSON" in result.reason


async def test_unrecognised_topic_is_rejected(db_session):
    result = await ingest_message(
        db=db_session, topic="totally/unrelated/topic", payload=_payload(1, "x")
    )

    assert result.ok is False
    assert "Unrecognised topic" in result.reason


async def test_ingest_marks_device_online_and_updates_last_seen(
    db_session, client, admin_user, project_with_device
):
    device_id = project_with_device["device_id"]
    device_uuid = project_with_device["device_uuid"]
    device_token = project_with_device["device_token"]
    await _create_datastream(client, admin_user, device_id)

    topic = build_value_topic(device_uuid, "temperature")
    await ingest_message(db=db_session, topic=topic, payload=_payload(21.5, device_token))

    device_resp = await client.get(
        f"/api/v1/devices/{device_id}",
        headers=auth_headers(admin_user),
    )
    assert device_resp.status_code == 200
    body = device_resp.json()
    assert body["status"] == "online"
    assert body["last_seen"] is not None
