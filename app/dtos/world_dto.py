from dataclasses import dataclass


@dataclass
class WorldDto:
    id: str
    name: str
    description: str
    owner_id: str
