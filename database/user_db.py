import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Dict, Optional
from config import uri,name_database


class UserDB:
    def __init__(self):
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client[name_database]
        self.collection = self.db['users']

    async def add_user(self, user_id: int):
        existing = await self.collection.find_one({"_id": user_id})
        if existing is None:
            await self.collection.insert_one({"_id": user_id, "favorites": []})

    async def get_favorites(self, user_id: int) -> Optional[List[Dict]]:
        user_doc = await self.collection.find_one({"_id": user_id}, {"favorites": 1})
        if user_doc:
            return user_doc.get("favorites", [])
        return None

    async def add_favorite(self, user_id: int, song: Dict):
        await self.add_user(user_id)
        query = {
            "_id": user_id,
            "favorites": {
                "$not": {
                    "$elemMatch": {
                        "title": song["title"],
                        "author": song["author"]
                    }
                }
            }
        }
        update = {
            "$push": {"favorites": song}
        }
        result = await self.collection.update_one(query, update)
        return result.modified_count  # 1 якщо додано, 0 якщо вже була

    async def remove_favorite(self, user_id: int, title: str, author: str):
        """Видалити пісню з улюблених по назві і автору."""
        update = {
            "$pull": {"favorites": {"title": title, "author": author}}
        }
        result = await self.collection.update_one({"_id": user_id}, update)
        return result.modified_count  # 1 якщо видалено, 0 якщо не знайдено

