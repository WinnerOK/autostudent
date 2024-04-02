from textwrap import dedent

from telebot.async_telebot import AsyncTeleBot
from telebot.types import BotCommand, Message

BOT_COMMANDS = [
    BotCommand("/start", "Начать работу с ботом"),
    BotCommand("/help", "Показать доступные команды"),
    BotCommand("/subscribe", "Управлять подписками на курсы"),
    BotCommand("/summary", "Получить краткое содержание лекции"),
]


def get_help_message() -> str:
    return (
        "Доступные команды:\n"
        + "\n".join([f"{cmd.command} - {cmd.description}" for cmd in BOT_COMMANDS])
    )


async def help_handler(message: Message, bot: AsyncTeleBot):
    await bot.send_message(
        message.chat.id,
        get_help_message(),
    )
