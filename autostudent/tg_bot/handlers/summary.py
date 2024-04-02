from textwrap import dedent

from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from autostudent.tg_bot.markups import course_markup


async def summary_handler(message: Message, bot: AsyncTeleBot):
    await bot.send_message(
        message.chat.id,
        dedent(
            f"""
            Выберите курс:
            """,
        ),
        reply_markup=course_markup(),
    )
