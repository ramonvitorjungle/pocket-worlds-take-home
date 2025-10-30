from dataclasses import dataclass
from typing import Optional


@dataclass
class World:
    name: str
    description: str
    owner_id: str
    _id: Optional[str] = None

    @property
    def id(self):
        return self._id
