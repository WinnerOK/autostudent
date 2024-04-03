import asyncpg


async def get_lesson_count_in_course(conn: asyncpg.Connection, course_id):
    return await conn.fetchval(
        """
        SELECT COUNT(*) FROM autostudent.lessons
        WHERE course_id = $1;
        """,
        course_id,
    )


async def check_exsisting_lesson(conn: asyncpg.Connection, title, course_id):
    return await conn.fetch(
        "SELECT id FROM autostudent.lessons WHERE name = $1 AND course_id = $2;",
        title,
        course_id,
    )


async def insert_lesson(
    conn: asyncpg.Connection, course_id, name, lesson_number, lms_url
):
    return await conn.execute(
        """
        INSERT INTO autostudent.lessons (course_id, name, lesson_number, lms_url)
        VALUES ($1, $2, $3, $4)
        RETURNING id;
        """,
        course_id,
        name,
        lesson_number,
        lms_url,
    )


async def get_lessons(conn: asyncpg.Connection, course_id):
    return await conn.fetch(
        """
        select id, name from autostudent.lessons where course_id = $1;
        """,
        int(course_id),
    )
