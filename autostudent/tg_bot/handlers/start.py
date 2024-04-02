import asyncpg
from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from autostudent.repository.user import insert_user
from autostudent.tg_bot.handlers.help import get_help_message


async def start_handler(
    message: Message,
    bot: AsyncTeleBot,
    pool: asyncpg.Pool,
):
    async with pool.acquire() as conn:
        await insert_user(conn, message.chat.id)
    await bot.reply_to(
        message,
        f"Привет, {message.from_user.full_name}!\n{get_help_message()}",
    )
