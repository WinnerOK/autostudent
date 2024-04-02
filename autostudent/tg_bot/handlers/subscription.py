import asyncpg
from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from autostudent.repository.course import get_courses
from autostudent.repository.subscription import get_chat_subscriptions
from autostudent.tg_bot.markups import subscription_markup


async def subscription_handler(
    message: Message,
    bot: AsyncTeleBot,
    pool: asyncpg.Pool,
):
    async with pool.acquire() as conn:  # type: asyncpg.Connection
        courses = await get_courses(conn, page_size=bot.settings.course_page_size)
        current_subscriptions = await get_chat_subscriptions(conn, message.chat.id)

    await bot.reply_to(
        message,
        "Выберите подписки на чат",
        reply_markup=subscription_markup(
            courses=courses,
            current_subscriptions=current_subscriptions,
            current_page=0,
            has_more=len(courses) <=bot.settings.course_page_size,
            subscription_icons=bot.settings.subscription_icons,
        )
    )
