import asyncio
import logging
from typing import Callable

import aiomqtt
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import settings
from app.db.session import SessionLocal
from app.modules.mqtt.ingest import ingest_message
from app.modules.mqtt.topics import VALUE_TOPIC_FILTER

logger = logging.getLogger("ciao.mqtt")

RECONNECT_DELAY_SECONDS = 5

SessionFactory = Callable[[], AsyncSession] | async_sessionmaker[AsyncSession]


async def run_mqtt_ingest_loop(
    hostname: str | None = None,
    port: int | None = None,
    username: str | None = None,
    password: str | None = None,
    session_factory: SessionFactory = SessionLocal,
) -> None:
    """
    Runs forever until the task is cancelled (see app.main's lifespan).
    Reconnects on any MqttError (broker restart, network blip, no broker
    configured at all) instead of giving up - a deployment without MQTT
    wired up yet should not crash the API, it should just keep retrying
    quietly in the background.

    Connection args default to `settings` but can be overridden - used by
    tests to point this at a throwaway local broker instead of whatever
    MQTT_HOST/.env says. `session_factory` defaults to the app's own
    `SessionLocal`, but tests must override it: that engine is a
    process-wide singleton bound to whichever event loop first used it,
    and pytest-asyncio gives every test its own loop, so reusing it
    across tests corrupts the pooled asyncpg connections ("attached to a
    different loop"). Tests pass a factory bound to a fresh per-test
    engine instead, same as the `db_session` fixture does.
    """
    while True:
        try:
            async with aiomqtt.Client(
                hostname=hostname or settings.MQTT_HOST,
                port=port or settings.MQTT_PORT,
                username=username or settings.MQTT_USERNAME or None,
                password=password or settings.MQTT_PASSWORD or None,
            ) as client:
                await client.subscribe(VALUE_TOPIC_FILTER)
                logger.info(
                    "mqtt: subscribed to %s on %s:%s",
                    VALUE_TOPIC_FILTER,
                    settings.MQTT_HOST,
                    settings.MQTT_PORT,
                )

                async for message in client.messages:
                    await _handle_message(message, session_factory)

        except asyncio.CancelledError:
            raise

        except aiomqtt.MqttError as exc:
            logger.warning(
                "mqtt: connection lost (%s); retrying in %ss",
                exc,
                RECONNECT_DELAY_SECONDS,
            )
            await asyncio.sleep(RECONNECT_DELAY_SECONDS)


async def _handle_message(
    message: aiomqtt.Message,
    session_factory: SessionFactory,
) -> None:
    topic = str(message.topic)
    payload = message.payload
    if not isinstance(payload, (bytes, bytearray)):
        payload = str(payload).encode()

    async with session_factory() as db:
        result = await ingest_message(db=db, topic=topic, payload=payload)

    if result.ok:
        logger.debug("mqtt: ingested %s", topic)
    else:
        logger.warning("mqtt: rejected %s: %s", topic, result.reason)
