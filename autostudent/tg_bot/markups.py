from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from autostudent.tg_bot.callbacks.types import (
    course_data,
    lesson_data,
)


def course_markup() -> InlineKeyboardMarkup:
    courses = ("C++", "Algorithms")
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        *[
            InlineKeyboardButton(
                text=course,
                callback_data=course_data.new(course=course.lower()),
            )
            for course in courses
        ],
        row_width=2,
    )
    return keyboard


def lesson_markup(lessons) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        *[
            InlineKeyboardButton(
                text=lesson,
                callback_data=lesson_data.new(lesson=lesson.lower()),
            )
            for lesson in lessons
        ],
        row_width=2,
    )
    return keyboard
