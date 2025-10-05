import json
import functools
import hashlib
import redis.asyncio as aioredis
import os



# Create async Redis client
redis = aioredis.Redis(
    host = os.environ['REDIS_HOST'],
    port=os.environ['REDIS_PORT'], 
    db=os.environ['REDIS_DB']
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

            # Store in Redis with TTL
            await redis.setex(key, ttl, json.dumps(result))
            print("🚀 From API (cached now)")
            return result
        return wrapper
    return decorator