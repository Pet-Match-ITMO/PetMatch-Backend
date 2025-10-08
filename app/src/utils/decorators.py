import json
import hashlib
import functools
from pydantic import BaseModel
import redis.asyncio as aioredis
from decouple import config



# Create async Redis client
redis = aioredis.Redis(
    host=config('REDIS_HOST'),
    port=config('REDIS_PORT', cast=int), 
    db=config('REDIS_DB', cast=int),
    password=config('REDIS_PASSWORD', default=None)
)

def redis_cache(ttl: int = 60):
    """Async Redis cache decorator (works with async functions)."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Unique key from function + args
            key_raw = f"{func.__name__}:{args}:{kwargs}"
            key = hashlib.sha256(key_raw.encode()).hexdigest()

            # Try cache
            cached = await redis.get(key)
            if cached:
                print("✅ From cache")
                return json.loads(cached)

            # Compute result
            result = await func(*args, **kwargs)

            # check if no python classes are in response
            if isinstance(result, list):
                if result:
                    if isinstance(result[0], BaseModel):
                        result = [i.model_dump() for i in result]
            elif isinstance(result, BaseModel):
                result = result.model_dump()

            # Store in Redis with TTL
            await redis.setex(key, ttl, json.dumps(result))
            print("🚀 From API (cached now)")
            return result
        return wrapper
    return decorator