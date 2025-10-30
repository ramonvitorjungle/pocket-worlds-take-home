import uuid
from typing import List

from fastapi import HTTPException

from app.dtos.create_world_dto import CreateWorldDto
from app.dtos.update_world_dto import UpdateWorldDto
from app.dtos.world_dto import WorldDto
from app.factories.world_dto_factory import build_world_dto
from app.models.user import User
from app.models.world import World
from app.repositories import world_repository
from app.repositories.world_repository import insert_world, find_world, find_all_worlds, find_worlds_with


async def create_world(create_world_dto: CreateWorldDto, owner: User) -> WorldDto:
    _id = str(uuid.uuid4())
    world = World(name=create_world_dto.name, description=create_world_dto.description, owner_id=owner.id, _id=_id)
    await insert_world(world)
    return build_world_dto(world=world)


async def get_world(id: str) -> WorldDto:
    world = await find_world(id)
    if world is None:
        raise HTTPException(status_code=404, detail="World not found")
    return build_world_dto(world=world)


async def get_all_worlds(owner_id: str = None) -> List[WorldDto]:
    if owner_id is None:
        worlds = await find_all_worlds()
        worlds_dto = [build_world_dto(x) for x in worlds]
        return worlds_dto
    else:
        worlds = await find_worlds_with({owner_id: owner_id})
        worlds_dto = [build_world_dto(x) for x in worlds]
        return worlds_dto


async def update_world(id: str, update_world_dto: UpdateWorldDto, owner: User) -> WorldDto:
    world = await find_world(id)
    if world is None:
        raise HTTPException(status_code=404, detail="World not found")
    if world.owner_id != owner.id:
        raise HTTPException(status_code=403, detail="Not authorized to update world")
    if world.name is not None:
        world.name = update_world_dto.name
    if world.description is not None:
        world.description = update_world_dto.description
    updated = await world_repository.update_world(world)
    if not updated:
        raise HTTPException(status_code=500, detail="Could not update world")
    return build_world_dto(world=world)