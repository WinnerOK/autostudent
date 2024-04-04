import logging
from typing import Annotated

import asyncpg
from taskiq import TaskiqDepends

import meilisearch
from telebot.async_telebot import AsyncTeleBot

import autostudent.parser as parser
from autostudent.broker import db_pool_dep, broker
from autostudent.repository.subscription import get_course_subscribers
from settings import Settings


@broker.task(schedule=[{"cron": "*/15 * * * *"}])
async def process_courses_lessons_job(
    db_pool: Annotated[asyncpg.Pool, TaskiqDepends(db_pool_dep)],
):
    conn: asyncpg.Connection
    meilisearch_client = meilisearch.Client(Settings().meili_dsn)
    async with db_pool.acquire() as conn:
        async with conn.transaction():
            await parser.process_courses_and_lessons(conn, meilisearch_client)

    meilisearch_client = meilisearch.Client(Settings().meili_dsn)
    try:
        await parser.process_courses_and_lessons(db_pool, meilisearch_client)
    except Exception as e:
        logging.exception("Scrapping faced error")



@broker.task
async def send_notifications(
    course_id: int,
    db_pool: Annotated[asyncpg.Pool, TaskiqDepends(db_pool_dep)],
    bot: Annotated[AsyncTeleBot, TaskiqDepends(bot_dep)],
):
    conn: asyncpg.Connection
    print("send")
    async with db_pool.acquire() as conn:
        subs = await get_course_subscribers(conn, course_id)
        print(subs)
        for sub in subs:
            await bot.send_message(
                sub,
                f""" Нотификация о {course_id}""",
            )
