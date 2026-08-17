import logging
import structlog


logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)

logger = structlog.get_logger()