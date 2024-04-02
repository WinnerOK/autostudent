from textwrap import dedent

import asyncpg


async def get_chat_subscriptions(
    conn: asyncpg.Connection,
    chat_id: int
) -> list[int]:  # список id курсов
    rows = await conn.fetch(
        dedent(
            """
            select course_id
            from autostudent.subscriptions
            where chat_id = $1
            """
        ),
        chat_id
    )

    return [
        r[0]
        for r in rows
    ]


async def get_course_subscribers(
    conn: asyncpg.Connection,
    course_id: int
) -> list[int]:  # список chat id подписчиков курса
    rows = await conn.fetch(
        dedent(
            """
            select chat_id
            from autostudent.subscriptions
            where course_id = $1
            """
        ),
        course_id
    )

    return [
        r[0]
        for r in rows
    ]


async def subscribe_chat(
    conn: asyncpg.Connection,
    chat_id: int,
    course_id: int,
):
    await conn.execute(
        dedent(
            """
            insert into autostudent.subscriptions(chat_id, course_id)
            values ($1, $2)
            on conflict do nothing
            """
        ),
        chat_id,
        course_id
    )


async def unsubscribe_chat(
    conn: asyncpg.Connection,
    chat_id: int,
    course_id: int,
):
    await conn.execute(
        dedent(
            """
            delete from autostudent.subscriptions
            where chat_id=$1 and course_id=$2
            """
        ),
        chat_id,
        course_id
    )
