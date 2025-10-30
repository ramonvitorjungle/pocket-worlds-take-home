from dataclasses import dataclass


@dataclass
class World:
    name: str
    description: str
    owner_id: str
    _id: str

    @property
    def id(self):
        return self._id
