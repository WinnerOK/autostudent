import asyncpg


async def insert_user(conn: asyncpg.Connection, chat_id: int) -> None:
    await conn.execute(
        "insert into autostudent.users (chat_id) "
        "values ($1) "
        "on conflict(chat_id) do nothing ",
        chat_id,
    )
