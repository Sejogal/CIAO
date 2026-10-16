import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Callable

import aiomqtt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import settings
from app.db.session import SessionLocal
from app.modules.automation.model import DeviceCommand
from app.modules.datastreams.model import Datastream
from app.modules.devices.model import Device
from app.modules.mqtt.topics import build_command_topic

logger = logging.getLogger("ciao.mqtt.commands")
SessionFactory = Callable[[], AsyncSession] | async_sessionmaker[AsyncSession]
POLL_SECONDS = 1
RETRY_LIMIT = 20


async def publish_pending_commands(
    client: aiomqtt.Client,
    session_factory: SessionFactory = SessionLocal,
    batch_size: int = 20,
) -> int:
    """Publish a locked batch from the transactional command outbox."""
    now = datetime.now(timezone.utc)
    async with session_factory() as db:
        result = await db.execute(
            select(DeviceCommand)
            .where(
                DeviceCommand.status == "pending",
                DeviceCommand.next_attempt_at <= now,
            )
            .order_by(DeviceCommand.created_at)
            .limit(batch_size)
            .with_for_update(skip_locked=True)
        )
        commands = list(result.scalars().all())
        published = 0
        for command in commands:
            stream = await db.get(Datastream, command.datastream_id)
            device = await db.get(Device, stream.device_id) if stream else None
            if not stream or not device or not device.is_active:
                command.status = "failed"
                command.last_error = "Target datastream or active device not found"
                continue

            topic = build_command_topic(device.uuid, stream.key)
            payload = json.dumps({
                "command_id": str(command.id),
                "value": command.value,
                "created_at": now.isoformat(),
            })
            try:
                await client.publish(topic, payload, qos=1, retain=False)
                command.status = "delivered"
                command.delivered_at = datetime.now(timezone.utc)
                command.last_error = None
                published += 1
            except Exception as exc:
                command.attempts += 1
                command.last_error = str(exc)[:2000]
                if command.attempts >= RETRY_LIMIT:
                    command.status = "failed"
                else:
                    delay = min(2 ** min(command.attempts, 8), 300)
                    command.next_attempt_at = datetime.now(timezone.utc) + timedelta(seconds=delay)
                logger.warning("MQTT command %s publish failed: %s", command.id, exc)
                break
        await db.commit()
        return published


async def run_command_publish_loop(
    session_factory: SessionFactory = SessionLocal,
) -> None:
    while True:
        try:
            async with aiomqtt.Client(
                hostname=settings.MQTT_HOST,
                port=settings.MQTT_PORT,
                username=settings.MQTT_USERNAME or None,
                password=settings.MQTT_PASSWORD or None,
            ) as client:
                logger.info("mqtt: command publisher connected")
                while True:
                    await publish_pending_commands(client, session_factory)
                    await asyncio.sleep(POLL_SECONDS)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("mqtt: command publisher disconnected; retrying")
            await asyncio.sleep(5)
