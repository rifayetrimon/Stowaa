import redis.asyncio as redis
from app.core.config import settings
import json
from typing import Any, Union
from pydantic import BaseModel
import logging
import backoff  # You'll need to add this to requirements.txt

logger = logging.getLogger(__name__)

class RedisService:
    def __init__(self):
        self._redis = None

    @backoff.on_exception(backoff.expo, 
                         (redis.ConnectionError, redis.TimeoutError),
                         max_tries=3)
    async def connect(self):
        """Initialize Redis connection with retry logic."""
        try:
            logger.info(f"Attempting to connect to Redis at: {settings.REDIS_URL}")
            self._redis = await redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_timeout=5,  # 5 seconds timeout
                socket_connect_timeout=5,
                retry_on_timeout=True
            )
            # Test connection
            await self._redis.ping()
            logger.info("Successfully connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            # Don't raise the exception - allow the app to work without Redis
            self._redis = None

    async def _ensure_connection(self):
        """Ensure Redis connection exists"""
        if self._redis is None:
            await self.connect()

    async def set(self, key: str, value: Union[BaseModel, list, dict], expire: int = 3600):
        """Set a value in Redis with proper serialization handling."""
        try:
            await self._ensure_connection()
            if self._redis is None:
                logger.warning("Redis unavailable - skipping cache set")
                return

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
            # Continue without caching

    async def get(self, key: str) -> Any:
        """Get and deserialize a value from Redis."""
        try:
            await self._ensure_connection()
            if self._redis is None:
                logger.warning("Redis unavailable - skipping cache get")
                return None

            cached_value = await self._redis.get(key)
            if cached_value:
                return json.loads(cached_value)
            return None
        except Exception as e:
            logger.error(f"Error getting Redis key {key}: {str(e)}")
            return None

    # ... rest of your methods ...

redis_service = RedisService()