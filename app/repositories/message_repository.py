from dataclasses import asdict
from typing import List, Dict, Any

from app.config.db import get_db
from app.models.message import Message

db = get_db()


async def find_all_messages(query: Dict[str, Any]) -> List[Message]:
    messages_dict = await db.messages.find(query).to_list()
    messages = [Message(**world) for world in messages_dict]
    return messages


async def consume_message(id: str, session=None) -> bool:
    result = await db.messages.update_one({"_id": id}, {"$set": {"consumed": True}}, session=session)
    return result.raw_result["ok"] > 0


async def insert_message(message: Message, session=None) -> str:
    result = await db.messages.insert_one(asdict(message), session=session)
    return result.inserted_id
