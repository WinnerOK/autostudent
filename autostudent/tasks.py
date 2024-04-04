import logging
from typing import Annotated

import asyncpg
import meilisearch
from taskiq import TaskiqDepends

import autostudent.parser as parser
from autostudent.broker import db_pool_dep, broker
from autostudent.settings import Settings


@broker.task(schedule=[{"cron": "*/15 * * * *"}])
async def process_courses_lessons_job(
    db_pool: Annotated[asyncpg.Pool, TaskiqDepends(db_pool_dep)],
):
    meilisearch_client = meilisearch.Client(Settings().meili_dsn)
    try:
        await parser.process_courses_and_lessons(db_pool, meilisearch_client)
    except Exception as e:
        logging.exception("Scrapping faced error")
