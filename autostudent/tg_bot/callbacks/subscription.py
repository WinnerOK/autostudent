import asyncpg
from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery

from autostudent.repository.course import get_courses_page
from autostudent.repository.subscription import subscribe_chat, unsubscribe_chat, get_chat_subscriptions
from autostudent.tg_bot.callbacks.types import (
    SubscriptionStatus,
    subscription_alter_status,
    subscription_change_page,
)
from autostudent.tg_bot.markups import subscription_markup


async def subscription_status_callback(
    call: CallbackQuery,
    bot: AsyncTeleBot,
    pool: asyncpg.Pool,
):
    callback_data: dict = subscription_alter_status.parse(callback_data=call.data)
    is_currently_subscribed = callback_data['target_status'] == SubscriptionStatus.subscribed
    async with pool.acquire() as conn:
        async with conn.transaction():
            if is_currently_subscribed:
                await subscribe_chat(conn, call.message.chat.id, int(callback_data['course_id']))
            else:
                await unsubscribe_chat(conn, call.message.chat.id, int(callback_data['course_id']))

    # Ищем нажатую кнопку и обновляем в ней данные
    reply_markup = call.message.reply_markup
    for row_idx, kb_row in enumerate(reply_markup.keyboard[:-2]):  # две последние строки - элементы управления
        for col_idx, btn in enumerate(kb_row):
            if btn.callback_data != call.data:
                continue

            reply_markup.keyboard[row_idx][col_idx].text = bot.settings.subscription_icons[
                                                               is_currently_subscribed] + btn.text[1:]
            reply_markup.keyboard[row_idx][col_idx].callback_data = subscription_alter_status.new(
                target_status=SubscriptionStatus.from_bool(not is_currently_subscribed),
                course_id=callback_data['course_id'],
            )

    await bot.edit_message_reply_markup(
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        reply_markup=reply_markup
    )


async def subscription_done_callback(
    call: CallbackQuery,
    bot: AsyncTeleBot,
):
    await bot.delete_message(
        chat_id=call.message.chat.id,
        message_id=call.message.id,
    )


async def subscription_change_page_callback(
    call: CallbackQuery,
    bot: AsyncTeleBot,
    pool: asyncpg.Pool,
):
    callback_data: dict = subscription_change_page.parse(callback_data=call.data)
    page_num = int(callback_data['page_num'])

    courses_to_request = bot.settings.course_page_size + 1

    async with pool.acquire() as conn:  # type: asyncpg.Connection
        courses = await get_courses_page(conn, page_num=page_num, page_size=courses_to_request)
        current_subscriptions = await get_chat_subscriptions(conn, call.message.chat.id)

    courses_found = len(courses)
    if courses:
        courses.pop()

    reply_markup = call.message.reply_markup
    reply_markup.keyboard[-2][-1].text = ''
    if len(courses) > 0:
        reply_markup = subscription_markup(
            courses=courses,
            current_subscriptions=current_subscriptions,
            current_page=page_num,
            has_more=(courses_found == courses_to_request),
            subscription_icons=bot.settings.subscription_icons,
        )
    await bot.edit_message_reply_markup(
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        reply_markup=reply_markup
    )
