import asyncpg
from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from autostudent.repository.course import get_courses_page
from autostudent.repository.subscription import get_chat_subscriptions
from autostudent.tg_bot.markups import subscription_markup


async def subscription_handler(
    message: Message,
    bot: AsyncTeleBot,
    pool: asyncpg.Pool,
):
    courses_to_request = bot.settings.course_page_size + 1
    async with pool.acquire() as conn:  # type: asyncpg.Connection
        courses = await get_courses_page(conn, page_size=courses_to_request)
        current_subscriptions = await get_chat_subscriptions(conn, message.chat.id)

    courses_found = len(courses)
    if courses:
        courses.pop()

    await bot.reply_to(
        message,
        "Выберите подписки на чат",
        reply_markup=subscription_markup(
            courses=courses,
            current_subscriptions=current_subscriptions,
            current_page=0,
            has_more=(courses_found == courses_to_request),
            subscription_icons=bot.settings.subscription_icons,
        )
    )
