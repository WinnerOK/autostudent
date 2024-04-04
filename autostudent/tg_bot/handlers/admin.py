from taskiq import AsyncTaskiqTask
from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from autostudent.tasks import process_courses_lessons_job


async def force_scrapping_handler(
    message: Message,
    bot: AsyncTeleBot,
):
    if message.from_user.id not in bot.settings.admin_list:
        return
    task: AsyncTaskiqTask = await process_courses_lessons_job.kiq()
    await bot.reply_to(message, f"[ADMIN] started scrapping.\nTask ID: {task.task_id}")
