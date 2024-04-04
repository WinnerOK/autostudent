import asyncpg

from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery, LinkPreviewOptions
from telebot.util import smart_split

from autostudent.repository.summarization import get_summary
from autostudent.repository.summary_format import markdown_keypoints
from autostudent.tg_bot.callbacks.types import lesson_data


async def lesson_data_callback(
    call: CallbackQuery,
    bot: AsyncTeleBot,
    pool: asyncpg.Pool,
) -> None:
    callback_data: dict = lesson_data.parse(callback_data=call.data)

    async with pool.acquire() as conn:  # type: # ayncpg.Connection
        summary = await get_summary(conn, callback_data["lesson"])

    md = markdown_keypoints(summary['video_url'], summary["summarization"])
    for part in smart_split(md):
        await bot.send_message(
            call.message.chat.id,
            part,
            parse_mode='MarkdownV2',
            link_preview_options=LinkPreviewOptions(is_disabled=True)
        )
