from redis.asyncio import Redis

redis_client = Redis(
    host="localhost",
    port=6380,
    decode_responses=True,
)
