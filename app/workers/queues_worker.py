from app.config.healthcheck import run_health_api_on_new_thread
from app.config.logs import get_worker_logger
from app.config.messaging import start_all_queues, subscribe_to_queue
from app.consumers.world_created_consumer import world_created_consumer
from app.consumers.world_updated_consumer import world_updated_consumer

logger = get_worker_logger(__name__)
logger.info("Starting queues worker")

subscribe_to_queue("world.created", world_created_consumer)
subscribe_to_queue("world.updated", world_updated_consumer)

run_health_api_on_new_thread()
start_all_queues()

logger.info("Shutting down queues worker")