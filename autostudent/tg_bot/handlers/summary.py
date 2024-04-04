from textwrap import dedent
import asyncpg
from autostudent.repository.course import get_courses_with_summaries

from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from autostudent.tg_bot.markups import course_markup


async def summary_handler(
    message: Message,
    bot: AsyncTeleBot,
    pool: asyncpg.Pool,
):
    async with pool.acquire() as conn:  # type: asyncpg.Connection
        courses = await get_courses_with_summaries(conn)

    await bot.send_message(
        message.chat.id,
        dedent(
            f"""
            Выберите курс:
            """,
        ),
        reply_markup=course_markup(courses),
    )
