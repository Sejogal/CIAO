import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Callable

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import settings
from app.db.session import SessionLocal
from app.modules.devices.model import Device

logger = logging.getLogger("ciao.mqtt.heartbeat")
SessionFactory = Callable[[], AsyncSession] | async_sessionmaker[AsyncSession]


async def mark_stale_devices_offline(
    db: AsyncSession,
    *,
    now: datetime | None = None,
    timeout_seconds: int | None = None,
) -> int:
    current_time = now or datetime.now(timezone.utc)
    timeout = timeout_seconds or settings.MQTT_DEVICE_OFFLINE_AFTER_SECONDS
    cutoff = current_time - timedelta(seconds=timeout)
    result = await db.execute(
        update(Device)
        .where(
            Device.is_active.is_(True),
            Device.status == "online",
            Device.last_seen.is_not(None),
            Device.last_seen <= cutoff,
        )
        .values(status="offline")
        .returning(Device.id)
    )
    changed = len(result.scalars().all())
    if changed:
        await db.flush()
        logger.info("mqtt: marked %s stale device(s) offline", changed)
    return changed


async def run_device_heartbeat_loop(
    session_factory: SessionFactory = SessionLocal,
) -> None:
    interval = settings.MQTT_HEARTBEAT_CHECK_INTERVAL_SECONDS
    while True:
        try:
            async with session_factory() as db:
                changed = await mark_stale_devices_offline(db)
                await db.commit()
            if changed:
                logger.info("mqtt: heartbeat sweep completed")
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("mqtt: heartbeat sweep failed")
        await asyncio.sleep(interval)
