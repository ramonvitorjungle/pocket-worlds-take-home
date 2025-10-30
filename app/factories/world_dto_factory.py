from app.dtos.world_dto import WorldDto
from app.models.world import World


def build_world_dto(world: World) -> WorldDto:
    return WorldDto(id=world.id, name=world.name, description=world.description, owner_id=world.owner_id)
