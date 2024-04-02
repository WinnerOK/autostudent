from textwrap import dedent

import asyncpg


async def get_courses(conn: asyncpg.Connection):
    return await conn.fetch(
        """
        select name from autostudent.courses;
        """
    )


async def get_lessons(conn: asyncpg.Connection, course_id):
    return await conn.fetch(
        """
        select name from autostudent.lessons where course_id = $1;
        """
    )
