"""
Redis caching layer for high-performance note operations.
Reduces database load and improves response times.
"""
import json
import logging
import os
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import redis.asyncio as redis
from .config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """High-performance caching service using Redis."""
    
    def __init__(self):
        self.redis_client = None
        self.cache_ttl = 300  # 5 minutes default TTL
        
    async def get_redis_client(self) -> redis.Redis:
        """Get Redis client with connection pooling."""
        if self.redis_client is None:
            self.redis_client = redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", "6379")),
                password=os.getenv("REDIS_PASSWORD"),
                db=int(os.getenv("REDIS_DB", "0")),
                decode_responses=True,
                max_connections=20,
                retry_on_timeout=True
            )
        return self.redis_client

    async def get_notes_cache_key(self, user_id: str, include_deleted: bool = False, limit: int = 20, offset: int = 0) -> str:
        """Generate cache key for notes list."""
        return f"notes:user:{user_id}:deleted:{include_deleted}:limit:{limit}:offset:{offset}"

    async def get_note_cache_key(self, note_id: str, user_id: str) -> str:
        """Generate cache key for single note."""
        return f"note:{note_id}:user:{user_id}"

    async def get_user_notes_count_key(self, user_id: str, include_deleted: bool = False) -> str:
        """Generate cache key for notes count."""
        return f"notes_count:user:{user_id}:deleted:{include_deleted}"

    async def get_notes(self, user_id: str, include_deleted: bool = False, limit: int = 20, offset: int = 0) -> Optional[List[Dict]]:
        """Get notes from cache."""
        try:
            redis_client = await self.get_redis_client()
            cache_key = await self.get_notes_cache_key(user_id, include_deleted, limit, offset)
            cached_data = await redis_client.get(cache_key)
            
            if cached_data:
                return json.loads(cached_data)
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    async def set_notes(self, user_id: str, notes: List[Dict], include_deleted: bool = False, limit: int = 20, offset: int = 0, ttl: int = None) -> bool:
        """Set notes in cache."""
        try:
            redis_client = await self.get_redis_client()
            cache_key = await self.get_notes_cache_key(user_id, include_deleted, limit, offset)
            ttl = ttl or self.cache_ttl
            
            await redis_client.setex(cache_key, ttl, json.dumps(notes, default=str))
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    async def get_note(self, note_id: str, user_id: str) -> Optional[Dict]:
        """Get single note from cache."""
        try:
            redis_client = await self.get_redis_client()
            cache_key = await self.get_note_cache_key(note_id, user_id)
            cached_data = await redis_client.get(cache_key)
            
            if cached_data:
                return json.loads(cached_data)
            return None
        except Exception as e:
            logger.error(f"Cache get note error: {e}")
            return None

    async def set_note(self, note: Dict, ttl: int = None) -> bool:
        """Set single note in cache."""
        try:
            redis_client = await self.get_redis_client()
            cache_key = await self.get_note_cache_key(note["id"], note["user_id"])
            ttl = ttl or self.cache_ttl
            
            await redis_client.setex(cache_key, ttl, json.dumps(note, default=str))
            return True
        except Exception as e:
            logger.error(f"Cache set note error: {e}")
            return False

    async def invalidate_user_notes(self, user_id: str) -> bool:
        """Invalidate all notes cache for a user."""
        try:
            redis_client = await self.get_redis_client()
            
            # Get all keys for this user
            pattern = f"notes:user:{user_id}:*"
            keys = await redis_client.keys(pattern)
            
            if keys:
                await redis_client.delete(*keys)
            
            # Also invalidate note count cache
            count_pattern = f"notes_count:user:{user_id}:*"
            count_keys = await redis_client.keys(count_pattern)
            
            if count_keys:
                await redis_client.delete(*count_keys)
            
            return True
        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")
            return False

    async def invalidate_note(self, note_id: str, user_id: str) -> bool:
        """Invalidate specific note cache."""
        try:
            redis_client = await self.get_redis_client()
            cache_key = await self.get_note_cache_key(note_id, user_id)
            await redis_client.delete(cache_key)
            
            # Also invalidate user's notes list cache
            await self.invalidate_user_notes(user_id)
            
            return True
        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")
            return False

    async def get_notes_count(self, user_id: str, include_deleted: bool = False) -> Optional[int]:
        """Get notes count from cache."""
        try:
            redis_client = await self.get_redis_client()
            cache_key = await self.get_user_notes_count_key(user_id, include_deleted)
            cached_count = await redis_client.get(cache_key)
            
            if cached_count:
                return int(cached_count)
            return None
        except Exception as e:
            logger.error(f"Cache get count error: {e}")
            return None

    async def set_notes_count(self, user_id: str, count: int, include_deleted: bool = False, ttl: int = None) -> bool:
        """Set notes count in cache."""
        try:
            redis_client = await self.get_redis_client()
            cache_key = await self.get_user_notes_count_key(user_id, include_deleted)
            ttl = ttl or self.cache_ttl
            
            await redis_client.setex(cache_key, ttl, str(count))
            return True
        except Exception as e:
            logger.error(f"Cache set count error: {e}")
            return False

    async def increment_notes_count(self, user_id: str, include_deleted: bool = False, increment: int = 1) -> bool:
        """Increment notes count in cache."""
        try:
            redis_client = await self.get_redis_client()
            cache_key = await self.get_user_notes_count_key(user_id, include_deleted)
            
            await redis_client.incrby(cache_key, increment)
            await redis_client.expire(cache_key, self.cache_ttl)
            
            return True
        except Exception as e:
            logger.error(f"Cache increment error: {e}")
            return False

    async def close(self):
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()


# Global cache service instance
cache_service = CacheService()
