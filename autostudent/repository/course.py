from dataclasses import dataclass
from textwrap import dedent

import asyncpg


@dataclass
class Course:
    id: int
    name: str
    lms_url: str

    @classmethod
    def from_db(cls, db_record: asyncpg.Record):
        d = dict(db_record)
        return cls(
            id=d['id'],
            name=d['name'],
            lms_url=d['lms_url'],
        )


async def get_courses_page(conn: asyncpg.Connection, page_num=0, page_size=10) -> list[Course]:
    rows = await conn.fetch(
        dedent(
            """
            select id, name, lms_url
            from autostudent.courses
            order by id
            offset $1
            limit $2
            """
        ),
        page_size * page_num,
        page_size,
    )

    return [
        Course.from_db(r)
        for r in rows
    ]


async def get_courses(conn: asyncpg.Connection):
    return await conn.fetch(
        """
        select id, name, lms_url from autostudent.courses
        order by lms_url
        ;
        """
    )

async def get_courses_with_summaries(conn: asyncpg.Connection):
    return await conn.fetch(
        """
        select c.id, c.name, c.lms_url
        from autostudent.courses c
        where exists(
                      select 1
                      from autostudent.lessons l
                               join autostudent.videos_summarization vs on l.id = vs.lesson_id
                      where l.course_id = c.id
                  )
        order by c.lms_url
        ;
        """
    )

async def get_lessons_by_course(conn: asyncpg.Connection, course_id):
    return await conn.fetch(
        """
        select id, name, lesson_number, lms_url from autostudent.lessons
        where course_id = $1
        order by lms_url
        ;
        """,
        course_id,
    )


async def insert_course(conn: asyncpg.Connection, name, lms_url):
    res = await conn.fetchrow(
        """
        insert into autostudent.courses (name, lms_url) values ($1, $2)
        returning id;
        """,
        name,
        lms_url,
    )

    return res[0]


async def check_exsisting_course(conn: asyncpg.Connection, title, url):
    return await conn.fetch(
        "select id from autostudent.courses where name = $1 and lms_url = $2;",
        title,
        url,
    )
