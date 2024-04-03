from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="local.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    telegram_token: str = Field()
    pg_dsn: PostgresDsn = Field()
    redis_dsn: RedisDsn = Field()
    rmq_dsn: str = Field()
    meili_dsn: str = Field()
    yandex_session_id: str = Field()

    course_page_size: int = 10
    subscription_icons: dict[bool, str] = {
        True: '✅',
        False: '❌',
    }
