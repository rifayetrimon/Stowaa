import redis.asyncio as redis
from app.core.config import settings
import json
from typing import Any, Union
from pydantic import BaseModel

class RedisService:
    def __init__(self):
        self.redis = None   

    async def connect(self):
        """Initialize Redis connection."""
        self.redis = await redis.from_url(settings.REDIS_URL, decode_responses=True)

    async def set(self, key: str, value: Union[BaseModel, list, dict], expire: int = 3600):
        """
        Set a value in Redis with proper serialization handling.
        Handles single Pydantic models, lists of models, and dictionaries.
        """
        if isinstance(value, BaseModel):
            serialized_value = value.model_dump()
        elif isinstance(value, list):
            serialized_value = [
                item.model_dump() if isinstance(item, BaseModel) else item 
                for item in value
            ]
        else:
            serialized_value = value

        await self.redis.setex(key, expire, json.dumps(serialized_value))

    async def get(self, key: str) -> Any:
        """Get and deserialize a value from Redis."""
        cached_value = await self.redis.get(key)
        if cached_value:
            return json.loads(cached_value)
        return None

    async def delete(self, key: str):
        """Delete a key from Redis."""
        if self.redis:
            await self.redis.delete(key)

    async def delete_pattern(self, pattern: str):
        """Delete all keys matching a pattern."""
        if self.redis:
            keys = await self.redis.keys(pattern)
            if keys:
                await self.redis.delete(*keys)

    async def close(self):
        """Close Redis connection."""
        if self.redis:
            await self.redis.close()

redis_service = RedisService()