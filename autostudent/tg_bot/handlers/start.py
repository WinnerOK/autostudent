from textwrap import dedent

from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from autostudent.tg_bot.handlers import get_help_message


async def start_handler(message: Message, bot: AsyncTeleBot):
    await bot.send_message(
        message.chat.id,
        dedent(
            f"""
            Привет, {message.from_user.full_name}!
{get_help_message()}
            """,
        ),
    )
