from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from autostudent.repository.course import Course
from autostudent.tg_bot.callbacks.types import (
    SubscriptionStatus,
    subscription_alter_status,
    subscription_change_page,
    subscription_done,
)


def subscription_markup(
    subscription_icons: dict[bool, str],
    courses: list[Course],
    current_subscriptions: list[int],
    current_page: int,
    has_more: bool = True
) -> InlineKeyboardMarkup:
    current_subscriptions = set(current_subscriptions)

    keyboard = InlineKeyboardMarkup()
    for course in courses:
        is_subscribed = course.id in current_subscriptions
        keyboard.add(
            InlineKeyboardButton(
                text=f"{subscription_icons[is_subscribed]} {course.name}",
                callback_data=subscription_alter_status.new(
                    target_status=SubscriptionStatus.from_bool(not is_subscribed),
                    course_id=course.id,
                )
            ),
            row_width=1,
        )
    keyboard.add(
        InlineKeyboardButton(
            text='⬅️' if current_page > 0 else '',
            callback_data=subscription_change_page.new(page_num=current_page - 1) if current_page > 0 else "dummy"
        ),
        InlineKeyboardButton(
            text='➡️' if has_more else '',
            callback_data=subscription_change_page.new(page_num=current_page + 1) if has_more else "dummy"
        ),
        row_width=2,
    )
    keyboard.add(
        InlineKeyboardButton(
            text='Завершить',
            callback_data=subscription_done.new()
        )
    )
    return keyboard
