import asyncio
from typing import Any, Dict

from app.config.logs import get_logger

logger = get_logger(__name__)


async def world_created_consumer(payload: Dict[str, Any]):
    logger.info(f"World created: {payload}")
    # sleeping to make it look like a heavy operation
    await asyncio.sleep(1)
    logger.info(f"World created event consumed")
