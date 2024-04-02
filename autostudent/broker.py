import asyncio
from typing import Annotated

import asyncpg
from taskiq_aio_pika import AioPikaBroker
from taskiq import TaskiqScheduler, Context, TaskiqState, TaskiqEvents, TaskiqDepends
from taskiq_redis import RedisAsyncResultBackend
from taskiq.serializers import ORJSONSerializer
from taskiq.schedule_sources import LabelScheduleSource
from telebot.async_telebot import AsyncTeleBot

from autostudent.settings import Settings

settings = Settings()
broker = (
    AioPikaBroker(settings.rmq_dsn)
    .with_result_backend(RedisAsyncResultBackend(str(settings.redis_dsn)))
    .with_serializer(ORJSONSerializer())
)

# docs: https://taskiq-python.github.io/guide/scheduling-tasks.html
scheduler = TaskiqScheduler(
    broker=broker,
    sources=[LabelScheduleSource(broker)],
)

@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def startup(state: TaskiqState) -> None:
    # Here we store connection pool on startup for later use.
    try:
        state.pool = await asyncio.wait_for(
            asyncpg.create_pool(
                dsn=str(settings.pg_dsn),
            ),
            timeout=5.0,
        )
    except asyncio.TimeoutError as e:
        msg = "Couldn't connect to database"
        raise RuntimeError(msg) from e
    
@broker.on_event(TaskiqEvents.WORKER_SHUTDOWN)
async def shutdown(state: TaskiqState) -> None:
    # Here we close our pool on shutdown event.
    await state.pool.close()


def db_pool_dep(context: Annotated[Context, TaskiqDepends()]) -> asyncpg.Pool:
    return context.state.pool

def bot_dep() -> AsyncTeleBot:
    bot = AsyncTeleBot(settings.telegram_token)
    bot.settings = settings
    return bot

@broker.task
async def add_one(
    value: int,
    db_pool: Annotated[asyncpg.Pool, TaskiqDepends(db_pool_dep)],
) -> int:
    conn: asyncpg.Connection
    async with db_pool.acquire() as conn:
        a = await conn.fetchrow("select 55;")
        return value + a[0] + 1