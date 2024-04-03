import asyncpg

from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery


from autostudent.tg_bot.callbacks.types import course_data
from autostudent.tg_bot.markups import lesson_markup
from autostudent.repository.course import get_courses


async def course_data_callback(
    call: CallbackQuery,
    bot: AsyncTeleBot,
    pool: asyncpg.Pool,
) -> None:
    callback_data: dict = course_data.parse(callback_data=call.data)

    # async with pool.acquire() as conn:  # type: asyncpg.Connection
    #     courses = await get_courses(conn)

    courses = ["1. Введение", "2. Первая лекция"]

    await bot.send_message(
        call.message.chat.id, "Выберите занятие:", reply_markup=lesson_markup(courses)
    )
