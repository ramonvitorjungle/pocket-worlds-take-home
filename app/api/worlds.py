from fastapi import APIRouter

from app.config.logs import get_logger
from app.dtos.create_world_dto import CreateWorldDto
from app.dtos.update_world_dto import UpdateWorldDto
from app.services.auth_service import get_user_from_auth
from app.services.worlds_service import create_world, get_world, get_all_worlds, update_world

router = APIRouter(prefix="/worlds")

logger = get_logger(__name__)

@router.get("/")
async def get_active_worlds(owner_id: str = None):
    logger.info(f"Getting worlds for owner: {owner_id}")
    worlds = await get_all_worlds(owner_id)
    return worlds


@router.get("/{id}")
async def get_world_details(id: str):
    logger.info(f"Getting world details for id: {id}")
    world = await get_world(id)
    return world


@router.post("/")
async def create_new_world(create_world_dto: CreateWorldDto):
    logger.info(f"Creating new world: {create_world_dto}")
    owner = get_user_from_auth()
    world_dto = await create_world(create_world_dto, owner)
    return world_dto


@router.put("/{id}")
async def update_world_metadata(id: str, update_world_dto: UpdateWorldDto):
    logger.info(f"Updating world: {id}")
    owner = get_user_from_auth()
    updated_world = await update_world(id, update_world_dto, owner)
    return updated_world
