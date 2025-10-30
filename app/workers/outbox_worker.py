import asyncio
import signal

from app.config.healthcheck import run_health_api_on_new_thread
from app.config.logs import get_worker_logger
from app.consumers.outbox_consumer import outbox_consumer

logger = get_worker_logger(__name__)

logger.info("Starting outbox worker")

should_work = True


def signal_trap(signum, frame):
    global should_work
    should_work = False


signal.signal(signal.SIGTERM, signal_trap)
signal.signal(signal.SIGINT, signal_trap)


async def main():
    while should_work:
        logger.debug("Consuming messages")
        await outbox_consumer()
        logger.debug("Messages consumed")
        await asyncio.sleep(0.1)


if __name__ == '__main__':
    run_health_api_on_new_thread()
    asyncio.run(main())

logger.info("Shutting down outbox worker")
