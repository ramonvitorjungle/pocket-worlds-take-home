from fastapi import FastAPI

from app.api.worlds import router

app = FastAPI()

app.include_router(router)