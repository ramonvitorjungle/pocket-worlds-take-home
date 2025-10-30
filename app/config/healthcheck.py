import threading

import uvicorn
from fastapi import FastAPI

from app.api.healthcheck import router

health_app = FastAPI()
health_app.include_router(router)


def health_api():
    uvicorn.run(health_app, host="0.0.0.0", port=9000, log_level="warning")


def run_health_api_on_new_thread():
    health_thread = threading.Thread(target=health_api, daemon=True)
    health_thread.start()
