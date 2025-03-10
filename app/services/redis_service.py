import redis.asyncio as redis
from app.core.config import settings
import json
from typing import Any, Union
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class RedisService:
    def __init__(self):
        self._redis = None   # Changed from self.redis to self._redis for consistency

    async def connect(self):
        """Initialize Redis connection."""
        try:
            self._redis = await redis.from_url(settings.REDIS_URL, decode_responses=True)
            # Test connection
            await self._redis.ping()
            logger.info("Successfully connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            raise

    async def _ensure_connection(self):
        """Ensure Redis connection exists"""
        if self._redis is None:
            await self.connect()

    async def set(self, key: str, value: Union[BaseModel, list, dict], expire: int = 3600):
        """Set a value in Redis with proper serialization handling."""
        await self._ensure_connection()
        try:
            if isinstance(value, BaseModel):
                serialized_value = value.model_dump()
            elif isinstance(value, list):
                serialized_value = [
                    item.model_dump() if isinstance(item, BaseModel) else item 
                    for item in value
                ]
            else:
                serialized_value = value

            await self._redis.setex(key, expire, json.dumps(serialized_value))
            logger.debug(f"Successfully set Redis key: {key}")
        except Exception as e:
            logger.error(f"Error setting Redis key {key}: {str(e)}")
            raise

    async def get(self, key: str) -> Any:
        """Get and deserialize a value from Redis."""
        await self._ensure_connection()
        try:
            cached_value = await self._redis.get(key)
            if cached_value:
                return json.loads(cached_value)
            return None
        except Exception as e:
            logger.error(f"Error getting Redis key {key}: {str(e)}")
            return None

    async def delete(self, key: str):
        """Delete a key from Redis."""
        await self._ensure_connection()
        try:
            await self._redis.delete(key)
            logger.debug(f"Successfully deleted Redis key: {key}")
        except Exception as e:
            logger.error(f"Error deleting Redis key {key}: {str(e)}")

    async def delete_pattern(self, pattern: str):
        """Delete all keys matching a pattern."""
        await self._ensure_connection()
        try:
            keys = await self._redis.keys(pattern)
            if keys:
                await self._redis.delete(*keys)
                logger.debug(f"Successfully deleted keys matching pattern: {pattern}")
        except Exception as e:
            logger.error(f"Error deleting keys with pattern {pattern}: {str(e)}")

    async def close(self):
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            self._redis = None
            logger.info("Redis connection closed")

redis_service = RedisService()