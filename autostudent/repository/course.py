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


async def get_courses(conn: asyncpg.Connection, page_num=0, page_size=10) -> list[Course]:
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

