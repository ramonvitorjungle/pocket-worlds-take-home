from dataclasses import asdict
from typing import List

from app.config.db import get_db
from app.models.world import World

db = get_db()


async def insert_world(world: World) -> str:
    result = await db.worlds.insert_one(asdict(world))
    return result.inserted_id


async def update_world(world: World) -> bool:
    result = await db.worlds.update_one({"_id": world.id}, {"$set": asdict(world)})
    return result.raw_result["ok"] > 0


async def find_world(id: str) -> World:
    world = await db.worlds.find_one({"_id": id})
    return World(**world)


async def find_all_worlds() -> List[World]:
    world_dicts = await db.worlds.find().to_list()
    worlds = [World(**world) for world in world_dicts]
    return worlds


async def find_worlds_with(query: dict) -> List[World]:
    world_dicts = await db.worlds.find(query).to_list()
    worlds = [World(**world) for world in world_dicts]
    return worlds
