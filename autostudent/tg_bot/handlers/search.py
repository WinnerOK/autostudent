import json

import asyncpg
import meilisearch

from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message, LinkPreviewOptions
from telebot.util import smart_split

from autostudent.repository.summarization import get_summary, get_summaries
from autostudent.repository.summary_format import markdown_keypoints
from autostudent.summarize import search_for_summary_keypoint


async def search_handler(
    message: Message,
    bot: AsyncTeleBot,
    pool: asyncpg.Pool,
    meili_client: meilisearch.Client,
):
    hits = await search_for_summary_keypoint(
        client=meili_client,
        query=message.text,
    )

    if not hits:
        await bot.reply_to(message, "Не смог ничего найти по данному запросу =(")
        return

    conn: asyncpg.Connection
    async with pool.acquire() as conn:
        summaries = await get_summaries(conn, [h['lesson_id'] for h in hits])

    summary_by_lesson = {
        int(s['lesson_id']): (s['video_url'], json.loads(s['summarization']))
        for s in summaries
    }

    msg_hits = []
    for h in hits:
        video_url, summary = summary_by_lesson[h['lesson_id']]
        _, keypoint_id = h['id'].split('_')
        msg_hits.append(markdown_keypoints(video_url, [summary[keypoint_id-1]]))

    msg = "Возможно, вам подойдут эти вхождения:\n" + "\n\n".join(msg_hits).strip()
    for part in smart_split(msg):
        await bot.send_message(
            message.chat.id,
            part,
            parse_mode='MarkdownV2',
            link_preview_options=LinkPreviewOptions(is_disabled=True)
        )
