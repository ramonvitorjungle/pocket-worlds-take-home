from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI

from app.api.worlds import router
from app.api.healthcheck import router as health_router
from app.config.logs import get_logger

logger = get_logger(__name__)

logger.info("Starting app")


app = FastAPI()

# telemetry(app)
# noinspection PyTypeChecker
app.add_middleware(CorrelationIdMiddleware)
app.include_router(router)
app.include_router(health_router)

logger.info("App started")
