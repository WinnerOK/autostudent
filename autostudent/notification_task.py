from typing import Annotated

import asyncpg
from taskiq import TaskiqDepends
from telebot.async_telebot import AsyncTeleBot

from autostudent.broker import db_pool_dep, broker, bot_dep
from autostudent.repository.subscription import get_course_subscribers
from autostudent.repository.summary_format import markdown_keypoints


@broker.task
async def send_notifications(
    course_id: int,
    course_name: str,
    lecture_name: str,
    video_url: str,
    summary: str,
    db_pool: Annotated[asyncpg.Pool, TaskiqDepends(db_pool_dep)],
    bot: Annotated[AsyncTeleBot, TaskiqDepends(bot_dep)],
):
    conn: asyncpg.Connection
    async with db_pool.acquire() as conn:
        subs = await get_course_subscribers(conn, course_id)
        md = markdown_keypoints(video_url, summary)
        msg = f'Появилась новая лекция по "{course_name}": "{lecture_name}"\nСуммаризация:\n' + md
        for sub in subs:
            await bot.send_message(
                sub,
                msg,
            )
