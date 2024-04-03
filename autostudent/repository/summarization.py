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
            SELECT
                summarization
            FROM autostudent.videos_summarization
            WHERE video_url = $1;
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
            INSERT INTO autostudent.videos_summarization(
                video_url,
                lesson_id,
                summarization
            ) VALUES (
                $1,
                $2,
                $3
            );
            """,
        ),
        video_url,
        lesson_id,
        summarization
    )
