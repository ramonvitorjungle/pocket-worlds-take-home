from contextlib import asynccontextmanager
from os import environ

from pymongo import AsyncMongoClient, WriteConcern
from pymongo.read_concern import ReadConcern

MONGO_URL = environ.get("MONGO_URL")
DATABASE = environ.get("DATABASE")
_client = None


def get_client():
    global _client
    if _client is None:
        # The server selection timeout could be extracted to an env var
        _client = AsyncMongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
    return _client


def get_db():
    return get_client().get_database(DATABASE)


def get_collection_with_options(collection):
    return collection.with_options(write_concern=WriteConcern("majority"), j=True, read_concern=ReadConcern("majority"))


def get_session():
    return get_client().start_session()


async def start_transaction(session):
    # The max_commit_time_ms could be extracted to an env var
    return await session.start_transaction(write_concern=WriteConcern("majority"), read_concern=ReadConcern("majority"), max_commit_time_ms=3000)


@asynccontextmanager
async def transaction():
    session = get_session()
    try:
        await start_transaction(session)
        yield session
        await session.commit_transaction()
    except Exception as e:
        await session.end_session()
        raise e