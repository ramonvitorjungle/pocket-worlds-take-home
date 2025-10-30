from app.config.db import transaction
from app.config.logs import get_worker_logger
from app.config.messaging import publish_message
from app.repositories.message_repository import find_all_messages, consume_message


logger = get_worker_logger(__name__)


async def outbox_consumer() -> None:
    all_messages = await find_all_messages({"consumed": False})
    sorted_messages = sorted(all_messages, key=lambda x: x.created_at)
    if len(sorted_messages) == 0:
        return
    logger.info("Consuming {} messages".format(len(sorted_messages)))
    for message in sorted_messages:
        async with transaction() as session:
            publish_message(message.queue_to_publish, message.message)
            await consume_message(message.id, session)
