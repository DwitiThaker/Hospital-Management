import asyncio

from redis.asyncio import Redis


async def main():
    redis = Redis(
        host="localhost",
        port=6380,
        decode_responses=True,
    )

    try:
        await redis.ping()
        print("Connected to Redis")

        await redis.set(
            "patient:test",
            "Hello from Python",
            ex=60,
        )

        value = await redis.get("patient:test")
        print(value)

    finally:
        await redis.aclose()


if __name__ == "__main__":
    asyncio.run(main())