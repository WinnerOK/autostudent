from textwrap import dedent

import asyncpg


async def get_courses(conn: asyncpg.Connection):
    return await conn.fetch(
        """
        select id, name from autostudent.courses;
        """
    )


async def get_lessons(conn: asyncpg.Connection, course_id):
    return await conn.fetch(
        """
        select id, name from autostudent.lessons where course_id = $1;
        """,
        int(course_id),
    )


async def get_summary(conn: asyncpg.Connection, lesson_id):
    return await conn.fetch(
        """
        select summarization from autostudent.videos_summarization where lesson_id = $1;
        """,
        int(lesson_id),
    )


async def get_subscriptions(conn: asyncpg.Connection, couse_id):
    return await conn.fetch(
        """
        select chat_id from autostudent.videos_summarization where course_id = $1;
        """
    )
