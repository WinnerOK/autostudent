from enum import Enum

from telebot.callback_data import CallbackData

language_level_data = CallbackData("level", prefix="lang_level")


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

