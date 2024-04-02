from enum import Enum

from telebot.callback_data import CallbackData


course_data = CallbackData("course", prefix="course")

lesson_data = CallbackData("lesson", prefix="lesson")
