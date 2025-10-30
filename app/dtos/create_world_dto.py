from dataclasses import dataclass


@dataclass
class CreateWorldDto:
    name: str
    description: str
