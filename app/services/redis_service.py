import redis.asyncio as redis
from app.core.config import settings
import json
from typing import Any, Union
from pydantic import BaseModel
import logging
import backoff  # You'll need to add this to requirements.txt

logger = logging.getLogger(__name__)

class RedisService:
    async def set(self, key: str, value: Union[BaseModel, list, dict], expire: int = 3600):
        """Set a value in Redis with proper serialization handling."""
        try:
            await self._ensure_connection()
            if self._redis is None:
                logger.error("❌ Redis connection not available")
                return

            # Log the data being cached
            logger.info(f"📝 Attempting to cache data for key: {key}")
            logger.info(f"📊 Data size: {len(str(value))} characters")

            if isinstance(value, BaseModel):
                serialized_value = value.model_dump()
            elif isinstance(value, list):
                serialized_value = [
                    item.model_dump() if isinstance(item, BaseModel) else item 
                    for item in value
                ]
            else:
                serialized_value = value

            # Convert to JSON string
            json_data = json.dumps(serialized_value)
            logger.info(f"🔄 Serialized data size: {len(json_data)} characters")

            # Set in Redis
            await self._redis.setex(key, expire, json_data)
            logger.info(f"✅ Successfully set key {key} in Redis")
            
            # Verify the data was set
            verification = await self._redis.get(key)
            if verification:
                logger.info("✅ Verified data was cached correctly")
            else:
                logger.error("⚠️ Data was not cached properly")

        except json.JSONEncodeError as e:
            logger.error(f"⚠️ JSON serialization error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"⚠️ Redis set error for key {key}: {str(e)}")
            raise

    async def get(self, key: str) -> Any:
        """Get and deserialize a value from Redis."""
        try:
            await self._ensure_connection()
            if self._redis is None:
                logger.error("❌ Redis connection not available")
                return None

            logger.info(f"🔍 Attempting to get key: {key}")
            cached_value = await self._redis.get(key)
            
            if cached_value:
                logger.info(f"✅ Found data for key: {key}")
                return json.loads(cached_value)
            
            logger.info(f"❌ No data found for key: {key}")
            return None
            
        except Exception as e:
            logger.error(f"⚠️ Redis get error for key {key}: {str(e)}")
            return None

    # ... rest of your methods ...

redis_service = RedisService()