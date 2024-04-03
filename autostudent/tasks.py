from typing import Annotated

import asyncpg
from taskiq import TaskiqDepends
import meilisearch

import parser
from autostudent.broker import db_pool_dep, broker
from settings import Settings


@broker.task(schedule={'cron': "*/15 * * * *"})
async def process_courses_lessons_job(
    db_pool: Annotated[asyncpg.Pool, TaskiqDepends(db_pool_dep)],
):
    conn: asyncpg.Connection
    meilisearch_client = meilisearch.Client(Settings().meili_dsn)
    async with db_pool.acquire() as conn:
        async with conn.transaction():
            await parser.process_courses_and_lessons(conn, meilisearch_client)

