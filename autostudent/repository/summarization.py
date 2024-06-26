from textwrap import dedent
from typing import Optional

import asyncpg


async def try_find_summarization_for_video(
    conn: asyncpg.Connection,
    video_url: str,
) -> Optional[str]:
    row = await conn.fetchrow(
        dedent(
            """
            select
                summarization
            from autostudent.videos_summarization
            where video_url = $1;
            """,
        ),
        video_url,
    )

    if not row:
        return None

    return row['summarization']


async def insert_summarization_for_video(
    conn: asyncpg.Connection,
    video_url: str,
    lesson_id: int,
    summarization: str,
) -> None:
    await conn.fetch(
        dedent(
            """
            insert into autostudent.videos_summarization(
                video_url,
                lesson_id,
                summarization
            ) values (
                $1,
                $2,
                $3
            ) on conflict do nothing ;
            """,
        ),
        video_url,
        lesson_id,
        summarization
    )


async def get_summary(conn: asyncpg.Connection, lesson_id):
    return await conn.fetchrow(
        """
        select video_url, summarization from autostudent.videos_summarization where lesson_id = $1;
        """,
        int(lesson_id),
    )


async def get_summaries(conn: asyncpg.Connection, lesson_ids):
    return await conn.fetch(
        """
        select
            vs.lesson_id as lesson_id,
            vs.video_url as video_url,
            vs.summarization as summarization,
            l.name as lesson_name,
            l.lms_url as lesson_url,
            c.name as course_name
        from autostudent.videos_summarization vs
        join autostudent.lessons l on l.id = vs.lesson_id
        join autostudent.courses c on c.id = l.course_id
        where lesson_id = any($1::bigint[]);
        """,
        list(map(int, lesson_ids)),
    )
