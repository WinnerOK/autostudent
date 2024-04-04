import asyncpg
import meilisearch

from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from autostudent.summarize import search_for_summary_keypoint


async def search_handler(
    message: Message,
    bot: AsyncTeleBot,
    pool: asyncpg.Pool,
    meili_client: meilisearch.Client,
):
    resp = await search_for_summary_keypoint(
        client=meili_client,
        query=message.text,
    )

    if resp is None:
        await bot.reply_to(message, "Не смог ничего найти по данному запросу =(")
        return

    await bot.reply_to(message, str(resp))
