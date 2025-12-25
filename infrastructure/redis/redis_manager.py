from typing import Optional
from redis.asyncio import Redis
import logging

logger = logging.getLogger(__name__)

class RedisManager:
    def __init__(self):
        self.client: Optional[Redis] = None

    async def connect(self, redis_url: str):
        self.client = Redis.from_url(redis_url, decode_responses=True)
        await self.client.ping()
        logger.info(f"Redis connected {redis_url}")

    async def close(self):
        if self.client:
            await self.client.aclose()
            logger.info(f"Redis disconnected")

    def get_client(self) -> Redis:
        if not self.client:
            raise RuntimeError("Redis client not connected. Call connect() first.")
        return self.client

redis_manager = RedisManager()
