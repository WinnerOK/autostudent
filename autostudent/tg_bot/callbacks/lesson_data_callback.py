import asyncpg

from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery

from autostudent.repository.sql_operations import get_summary
from autostudent.tg_bot.callbacks.types import lesson_data


async def lesson_data_callback(
    call: CallbackQuery,
    bot: AsyncTeleBot,
    pool: asyncpg.Pool,
) -> None:
    callback_data: dict = lesson_data.parse(callback_data=call.data)

    async with pool.acquire() as conn:  # type: # ayncpg.Connection
        summary = await get_summary(conn, callback_data["lesson"])

    await bot.send_message(call.message.chat.id, summary[0]["summarization"])
