import asyncio
import asyncpg
from typing import Annotated

import parser

from taskiq import TaskiqScheduler, TaskiqState, TaskiqEvents, TaskiqDepends, Context
from taskiq.cron import cron
from taskiq.schedule_sources import LabelScheduleSource
from taskiq.scheduler import TaskiqScheduler
from taskiq.serializers import ORJSONSerializer
from taskiq_aio_pika import AioPikaBroker
from taskiq_redis import RedisAsyncResultBackend


from autostudent.settings import Settings

settings = Settings()
broker = (
    AioPikaBroker(settings.rmq_dsn)
    .with_result_backend(RedisAsyncResultBackend(str(settings.redis_dsn)))
    .with_serializer(ORJSONSerializer())
)


scheduler = TaskiqScheduler(
    broker=broker,
    sources=[LabelScheduleSource(broker)],
)


@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def startup(state: TaskiqState) -> None:
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
    await state.pool.close()

def db_pool_dep(context: Annotated[Context, TaskiqDepends()]) -> asyncpg.Pool:
    return context.state.pool


@scheduler.cron(cron("*/15 * * * *"), task_id="process_courses_lessons_15min")
async def process_courses_lessons_job(
    db_pool: Annotated[asyncpg.Pool, TaskiqDepends(db_pool_dep)],
):
    conn: asyncpg.Connection
    async with db_pool.acquire() as conn:
        await parser.process_courses_and_lessons(conn)
