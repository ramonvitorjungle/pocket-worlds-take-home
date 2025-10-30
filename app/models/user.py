from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    name: str
    _id: Optional[str] = None

    @property
    def id(self):
        return self._id
