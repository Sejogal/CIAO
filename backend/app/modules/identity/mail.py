import asyncio
import smtplib
import ssl
from email.message import EmailMessage
from urllib.parse import urlencode, urlsplit, urlunsplit, parse_qsl

from app.core.config import settings


def mail_is_configured() -> bool:
    return bool(settings.MAIL_HOST and settings.MAIL_FROM)


def _send_email(to: str, subject: str, body: str) -> None:
    message = EmailMessage()
    message["From"] = settings.MAIL_FROM
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP(settings.MAIL_HOST, settings.MAIL_PORT, timeout=15) as smtp:
        smtp.ehlo()
        if settings.MAIL_STARTTLS:
            smtp.starttls(context=context)
            smtp.ehlo()
        if settings.MAIL_USERNAME:
            smtp.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD or "")
        smtp.send_message(message)


async def send_email(to: str, subject: str, body: str) -> None:
    await asyncio.to_thread(_send_email, to, subject, body)


def password_reset_link(token: str) -> str:
    parts = urlsplit(settings.PASSWORD_RESET_URL)
    query = dict(parse_qsl(parts.query))
    query["token"] = token
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), ""))
