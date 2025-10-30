from dataclasses import asdict
from typing import List

from app.config.db import get_db
from app.models.world import World

db = get_db()


async def insert_world(world: World, session=None) -> str:
    result = await db.worlds.insert_one(asdict(world), session=session)
    return result.inserted_id


async def update_world(world: World, session=None) -> bool:
    collection = db.worlds
    result = await collection.update_one({"_id": world.id}, {"$set": asdict(world)}, session=session)
    return result.raw_result["ok"] > 0


async def find_world(id: str, session=None) -> World:
    world = await db.worlds.find_one({"_id": id}, session=session)
    return World(**world)


async def find_all_worlds(session=None) -> List[World]:
    world_dicts = await db.worlds.find(session=session).to_list()
    worlds = [World(**world) for world in world_dicts]
    return worlds


async def find_worlds_with(query: dict, session=None) -> List[World]:
    world_dicts = await db.worlds.find(query, session=session).to_list()
    worlds = [World(**world) for world in world_dicts]
    return worlds
