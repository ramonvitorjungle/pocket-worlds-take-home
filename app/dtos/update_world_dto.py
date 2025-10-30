from dataclasses import dataclass
from typing import Optional


@dataclass
class UpdateWorldDto:
    name: Optional[str]
    description: Optional[str]