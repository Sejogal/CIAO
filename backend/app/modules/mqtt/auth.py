from hmac import compare_digest

from fastapi import APIRouter, Depends, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import verify_password
from app.db.session import get_db
from app.modules.datastreams.model import Datastream
from app.modules.devices.model import Device

router = APIRouter()


def _same_secret(left: str, right: str) -> bool:
    return compare_digest(left.encode("utf-8"), right.encode("utf-8"))


def _acl_rule(action: str, topic: str) -> dict:
    return {
        "permission": "allow",
        "action": action,
        "topic": f"eq {topic}",
    }


def _denied() -> dict:
    return {"result": "deny", "is_superuser": False}


@router.post("/emqx/authentication")
async def authenticate_emqx_client(
    credentials: dict,
    x_ciao_emqx_secret: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """EMQX HTTP authentication endpoint; protected by a shared internal secret."""
    secret = settings.EMQX_AUTH_SECRET
    if (
        not secret
        or not x_ciao_emqx_secret
        or not _same_secret(x_ciao_emqx_secret, secret)
    ):
        return _denied()

    username = credentials.get("username")
    password = credentials.get("password")
    if not isinstance(username, str) or not isinstance(password, str):
        return _denied()

    # The API's own MQTT account is used by the ingest subscriber and command
    # publisher. Keep it within the CIAO topic namespace.
    if _same_secret(username, settings.MQTT_USERNAME):
        if not _same_secret(password, settings.MQTT_PASSWORD):
            return _denied()
        return {
            "result": "allow",
            "is_superuser": False,
            "acl": [
                _acl_rule("publish", "ciao/devices/#"),
                _acl_rule("subscribe", "ciao/devices/#"),
            ],
        }

    result = await db.execute(
        select(Device).where(
            Device.mqtt_username == username,
            Device.is_active.is_(True),
        )
    )
    device = result.scalar_one_or_none()
    if not device or not device.mqtt_password:
        return _denied()

    try:
        password_matches = verify_password(password, device.mqtt_password)
    except Exception:
        password_matches = False
    if not password_matches:
        return _denied()

    stream_result = await db.execute(
        select(Datastream.key).where(
            Datastream.device_id == device.id,
            Datastream.is_active.is_(True),
        )
    )
    acl = []
    for key in stream_result.scalars():
        acl.extend(
            [
                _acl_rule(
                    "publish", f"ciao/devices/{device.uuid}/datastreams/{key}"
                ),
                _acl_rule(
                    "subscribe", f"ciao/devices/{device.uuid}/commands/{key}"
                ),
            ]
        )

    return {"result": "allow", "is_superuser": False, "acl": acl}
