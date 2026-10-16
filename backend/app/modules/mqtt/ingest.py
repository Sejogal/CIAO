import json
from dataclasses import dataclass
from datetime import datetime, timezone
from hmac import compare_digest

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.datastream_values.model import DatastreamValue
from app.modules.datastream_values.repository import DatastreamValueRepository
from app.modules.datastream_values.service import value_matches_data_type
from app.modules.datastreams.repository import DatastreamRepository
from app.modules.devices.repository import DeviceRepository
from app.modules.mqtt.topics import parse_value_topic
from app.modules.automation.service import AutomationService


@dataclass
class IngestResult:
    ok: bool
    reason: str | None = None
    value: DatastreamValue | None = None


async def ingest_message(
    db: AsyncSession,
    topic: str,
    payload: bytes,
) -> IngestResult:
    """
    Turns one raw MQTT message into a DatastreamValue row, or a reason it
    was rejected. Never raises - a malformed/malicious message must not
    kill the subscriber loop, it just gets logged and dropped.

    Payload contract: {"token": "<device.token>", "value": <any>,
    "recorded_at": "<iso timestamp, optional>"}. EMQX authenticates
    individual MQTT credentials and topic ACLs through its HTTP authenticator.
    The payload token remains a second application-level check before the
    value is accepted.
    """

    parsed_topic = parse_value_topic(topic)
    if not parsed_topic:
        return IngestResult(ok=False, reason=f"Unrecognised topic: {topic}")
    device_uuid, key = parsed_topic

    try:
        body = json.loads(payload)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return IngestResult(ok=False, reason="Payload is not valid JSON")

    if not isinstance(body, dict) or "value" not in body:
        return IngestResult(ok=False, reason="Payload must be a JSON object with a 'value' field")

    token = body.get("token")
    if not isinstance(token, str):
        return IngestResult(ok=False, reason="Payload is missing a 'token' field")

    device = await DeviceRepository.get_by_uuid(db=db, uuid=device_uuid)
    if not device or not device.is_active:
        return IngestResult(ok=False, reason=f"Unknown or inactive device: {device_uuid}")

    if not compare_digest(token, device.token):
        return IngestResult(ok=False, reason=f"Invalid token for device: {device_uuid}")

    datastream = await DatastreamRepository.get_by_key(
        db=db,
        device_id=device.id,
        key=key,
    )
    if not datastream:
        return IngestResult(ok=False, reason=f"Unknown datastream '{key}' for device {device_uuid}")

    value = body["value"]
    if not value_matches_data_type(value, datastream.data_type):
        return IngestResult(
            ok=False,
            reason=f"Value does not match data_type '{datastream.data_type}' for {device_uuid}/{key}",
        )

    recorded_at_raw = body.get("recorded_at")
    recorded_at = datetime.now(timezone.utc)
    if isinstance(recorded_at_raw, str):
        try:
            recorded_at = datetime.fromisoformat(recorded_at_raw)
        except ValueError:
            pass

    created = await DatastreamValueRepository.create(
        db=db,
        value=DatastreamValue(
            datastream_id=datastream.id,
            value=value,
            recorded_at=recorded_at,
        ),
    )

    await AutomationService.evaluate(
        db=db,
        datastream_id=datastream.id,
        value=value,
    )

    await DeviceRepository.update(
        db=db,
        device=device,
        data={"status": "online", "last_seen": datetime.now(timezone.utc)},
    )

    await db.commit()

    return IngestResult(ok=True, value=created)
