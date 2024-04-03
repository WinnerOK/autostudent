from typing import Annotated

import asyncpg
from taskiq import TaskiqDepends

import parser
from autostudent.broker import db_pool_dep, bot_dep, broker
from autostudent.repository.subscription import get_course_subscribers


@broker.task(schedule={"cron": "*/15 * * * *"})
async def process_courses_lessons_job(
    db_pool: Annotated[asyncpg.Pool, TaskiqDepends(db_pool_dep)],
):
    conn: asyncpg.Connection
    async with db_pool.acquire() as conn:
        async with conn.transaction():
            await parser.process_courses_and_lessons(conn)


@broker.task
async def send_notifications(
    course_id: int, db_pool: Annotated[asyncpg.Pool, TaskiqDepends(db_pool_dep)]
):
    conn: asyncpg.Connection
    bot = bot_dep()
    async with db_pool.acquire() as conn:
        subs = await get_course_subscribers(conn, course_id)
        for sub in subs:
            await bot.send_message(
                sub,
                f""" Нотификация о {course_id}""",
            )
