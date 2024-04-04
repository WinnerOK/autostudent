import json

import asyncpg
import meilisearch

from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message, LinkPreviewOptions
from telebot.util import smart_split
import telebot.formatting as fmt


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
        print("finding summaries")
        summaries = await get_summaries(conn, [h['lesson_id'] for h in hits])

    summary_by_lesson = {
        int(s['lesson_id']): s
        for s in summaries
    }

    msg_hits = []
    for h in hits:
        summary_data = summary_by_lesson[h['lesson_id']]
        video_url = summary_data['video_url']
        summary = json.loads(summary_data['summarization'])
        lesson_name = summary_data['lesson_name']
        lesson_url = summary_data['lesson_url']
        course_name = summary_data['course_name']

        _, keypoint_id = h['id'].split('_')
        print(f"getting resp for {h}")
        msg_hits.append(f"{fmt.escape_markdown(course_name)}: {fmt.mlink(lesson_name, lesson_url)}\n{markdown_keypoints(video_url, [summary[int(keypoint_id) - 1]])}")

    msg = "Возможно, вам подойдут эти вхождения:\n" + "\n\n".join(msg_hits).strip()
    for part in smart_split(msg):
        await bot.send_message(
            message.chat.id,
            part,
            parse_mode='MarkdownV2',
            link_preview_options=LinkPreviewOptions(is_disabled=True)
        )
