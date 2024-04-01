import asyncio
from taskiq_aio_pika import AioPikaBroker
from taskiq_redis import RedisAsyncResultBackend

from autostudent.settings import Settings

settings = Settings()
broker = (
    AioPikaBroker(settings.rmq_dsn)
    .with_result_backend(RedisAsyncResultBackend(str(settings.redis_dsn)))
)

# TODO: embed db connection
#  https://taskiq-python.github.io/guide/state-and-deps.html#state

@broker.task
async def add_one(value: int) -> int:
    return value + 1