from datetime import datetime
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Message:
    queue_to_publish: str
    message: Dict[str, Any]
    _id: str
    created_at: datetime = datetime.now()
    consumed: bool = False

    @property
    def id(self):
        return self._id
