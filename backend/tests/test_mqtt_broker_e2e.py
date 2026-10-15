"""
End-to-end check that the wiring itself works: a real MQTT broker, a real
network publish, and app.modules.mqtt.client.run_mqtt_ingest_loop actually
subscribing and consuming - not just ingest_message() called directly (see
test_mqtt_ingest.py for that). Uses amqtt as a disposable local broker; see
README_CIAO.md Prioridade 5 - production points this at a real broker
(EMQX), only the local dev/test broker is swapped out here.
"""

import asyncio
import json
import socket
import time

import aiomqtt
import pytest_asyncio
from amqtt.broker import Broker
from amqtt.contexts import BrokerConfig, ListenerConfig
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from tests.conftest import auth_headers

from app.core.config import settings
from app.modules.datastream_values.model import DatastreamValue
from app.modules.mqtt.client import run_mqtt_ingest_loop
from app.modules.mqtt.topics import build_value_topic


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest_asyncio.fixture
async def mqtt_broker():
    port = _free_port()
    broker = Broker(
        BrokerConfig(listeners={"default": ListenerConfig(bind=f"127.0.0.1:{port}")})
    )
    await broker.start()
    try:
        yield port
    finally:
        await broker.shutdown()


@pytest_asyncio.fixture
async def mqtt_ingest_task(mqtt_broker):
    # A fresh engine, not app.db.session.SessionLocal: that one is a
    # process-wide singleton bound to whichever event loop first touched
    # it, and reusing it from this test's own loop corrupts the pooled
    # asyncpg connections (see run_mqtt_ingest_loop's docstring).
    engine = create_async_engine(settings.database_url, future=True)
    session_factory = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )

    task = asyncio.create_task(
        run_mqtt_ingest_loop(
            hostname="127.0.0.1",
            port=mqtt_broker,
            session_factory=session_factory,
        )
    )
    # The loop connects and subscribes before its first `async for`; give
    # it a moment so the publish below isn't racing the subscription.
    await asyncio.sleep(0.3)
    try:
        yield
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        await engine.dispose()


async def _publish(port: int, topic: str, payload: dict) -> None:
    async with aiomqtt.Client(hostname="127.0.0.1", port=port) as publisher:
        await publisher.publish(topic, payload=json.dumps(payload).encode())


async def _wait_for_value(db_session, datastream_id, timeout=5.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        result = await db_session.execute(
            select(DatastreamValue).where(
                DatastreamValue.datastream_id == datastream_id
            )
        )
        value = result.scalar_one_or_none()
        if value is not None:
            return value
        await asyncio.sleep(0.1)
    return None


async def test_publishing_over_a_real_broker_creates_a_datastream_value(
    mqtt_ingest_task,
    mqtt_broker,
    db_session,
    client,
    admin_user,
    project_with_device,
):
    device_id = project_with_device["device_id"]
    device_uuid = project_with_device["device_uuid"]
    device_token = project_with_device["device_token"]

    ds_resp = await client.post(
        f"/api/v1/datastreams/devices/{device_id}",
        json={"name": "Temperatura", "key": "temperature", "data_type": "float"},
        headers=auth_headers(admin_user),
    )
    assert ds_resp.status_code == 201, ds_resp.text
    datastream_id = ds_resp.json()["id"]

    # The test's get_db override just yields db_session - unlike the real
    # get_db, it never commits per request (same-session reads don't need
    # it). The MQTT ingest task runs on a genuinely separate connection
    # (see mqtt_ingest_task), so it can only see the device/datastream
    # created above once this transaction is actually committed.
    await db_session.commit()

    topic = build_value_topic(device_uuid, "temperature")
    await _publish(mqtt_broker, topic, {"token": device_token, "value": 23.4})

    value = await _wait_for_value(db_session, datastream_id)

    assert value is not None
    assert value.value == 23.4


async def test_publishing_with_wrong_token_over_a_real_broker_is_dropped(
    mqtt_ingest_task,
    mqtt_broker,
    db_session,
    client,
    admin_user,
    project_with_device,
):
    device_id = project_with_device["device_id"]
    device_uuid = project_with_device["device_uuid"]

    ds_resp = await client.post(
        f"/api/v1/datastreams/devices/{device_id}",
        json={"name": "Temperatura", "key": "temperature", "data_type": "float"},
        headers=auth_headers(admin_user),
    )
    assert ds_resp.status_code == 201, ds_resp.text
    datastream_id = ds_resp.json()["id"]

    await db_session.commit()

    topic = build_value_topic(device_uuid, "temperature")
    await _publish(mqtt_broker, topic, {"token": "forged-token", "value": 99.9})

    value = await _wait_for_value(db_session, datastream_id, timeout=1.5)

    assert value is None
