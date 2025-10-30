from os import environ

from pymongo import AsyncMongoClient


MONGO_URL = environ.get("MONGO_URL")
DATABASE = environ.get("DATABASE")
client = AsyncMongoClient(MONGO_URL)


def get_db():
    return client.get_database(DATABASE)
