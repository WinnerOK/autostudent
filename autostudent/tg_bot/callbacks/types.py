from enum import Enum

from telebot.callback_data import CallbackData

class SubscriptionStatus(str, Enum):
    subscribed = "sub"
    unsubscribed = "unsub"

    @classmethod
    def from_bool(cls, subscribed: bool):
        if subscribed:
            return cls.subscribed
        return cls.unsubscribed


subscription_alter_status = CallbackData(
    "target_status",
    "course_id",
    prefix="sub_st",
)

subscription_change_page = CallbackData(
    "page_num",
    prefix="sub_p",
)

subscription_done = CallbackData(
    prefix="sub_d",
)

course_data = CallbackData("course", prefix="course")
lesson_data = CallbackData("lesson", prefix="lesson")
