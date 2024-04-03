import asyncio
from functools import partial

import asyncpg
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_filters import AdvancedCustomFilter
from telebot.callback_data import CallbackDataFilter
from telebot.types import CallbackQuery

from autostudent.settings import Settings
from autostudent.tg_bot import callbacks, handlers
from autostudent.broker import broker, add_one
from autostudent.tg_bot.callbacks.subscription import (
    subscription_status_callback,
    subscription_done_callback,
    subscription_change_page_callback,
)
from autostudent.tg_bot.callbacks.types import (
    subscription_alter_status,
    subscription_done,
    subscription_change_page,
)


def register_handlers(bot: AsyncTeleBot, pool: asyncpg.Pool) -> None:
    bot.register_message_handler(
        partial(
            handlers.start_handler,
            pool=pool,
        ),
        commands=["start"],
        pass_bot=True,
    )

    bot.register_message_handler(
        handlers.help_handler,
        commands=["help"],
        pass_bot=True,
    )

    bot.register_message_handler(
        partial(
            handlers.subscription_handler,
            pool=pool,
        ),
        commands=["subscribe"],
        pass_bot=True,
    )

    bot.register_callback_query_handler(
        partial(
            subscription_status_callback,
            pool=pool,
        ),
        func=None,
        config=subscription_alter_status.filter(),
        pass_bot=True,
    )

    bot.register_callback_query_handler(
        subscription_done_callback,
        func=None,
        config=subscription_done.filter(),
        pass_bot=True,
    )

    bot.register_callback_query_handler(
        partial(
            subscription_change_page_callback,
            pool=pool,
        ),
        func=None,
        config=subscription_change_page.filter(),
        pass_bot=True,
    )

    bot.register_message_handler(
        partial(
            handlers.summary_handler,
            pool=pool,
        ),
        commands=["summary"],
        pass_bot=True,
    )

    bot.register_callback_query_handler(
        partial(
            callbacks.course_data_callback,
            pool=pool,
        ),
        func=None,
        config=callbacks.course_data.filter(),
        pass_bot=True,
    )

    bot.register_callback_query_handler(
        partial(
            callbacks.lesson_data_callback,
            pool=pool,
        ),
        func=None,
        config=callbacks.lesson_data.filter(),
        pass_bot=True,
    )

    bot.register_callback_query_handler(
        partial(
            callbacks.lesson_data_callback,
            pool=pool,
        ),
        func=None,
        config=callbacks.lesson_data.filter(),
        pass_bot=True,
    )


class CallbackFilter(AdvancedCustomFilter):
    key = "config"

    async def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)


async def main():
    settings = Settings()

    try:
        pool: asyncpg.Pool = await asyncio.wait_for(
            asyncpg.create_pool(
                dsn=str(settings.pg_dsn),
            ),
            timeout=5.0,
        )
    except asyncio.TimeoutError as e:
        msg = "Couldn't connect to database"
        raise RuntimeError(msg) from e

    await broker.startup()

    # Пример как стартануть таску. Результат таски можно не дожидаться. Она все-равно выполнится
    # task = await add_one.kiq(1)
    # result = await task.wait_result()
    # print(f"Task execution took: {result.execution_time} seconds.")
    # if not result.is_err:
    #     print(f"Returned value: {result.return_value}")
    # else:
    #     print("Error found while executing task.")

    bot = AsyncTeleBot(settings.telegram_token)
    bot.settings = settings
    bot.add_custom_filter(CallbackFilter())
    register_handlers(bot, pool)
    await bot.delete_my_commands()
    await bot.set_my_commands(handlers.BOT_COMMANDS)

    print("Bot is started")
    try:
        await bot.polling()
    finally:
        await pool.close()
        await broker.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
