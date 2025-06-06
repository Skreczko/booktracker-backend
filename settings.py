import os

from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    debug: bool = True
    swagger_username: SecretStr = SecretStr(os.environ.get("SWAGGER_USERNAME", "admin"))
    swagger_password: SecretStr = SecretStr(os.environ.get("SWAGGER_PASSWORD", "admin"))

    # Database configuration
    postgres_password: SecretStr = SecretStr(
        os.environ.get("POSTGRES_PASSWORD", "postgres")
    )
    postgres_user: SecretStr = SecretStr(os.environ.get("POSTGRES_USER", "postgres"))
    postgres_db: str = os.environ.get("POSTGRES_DB", "book-tracker")
    postgres_host: SecretStr = SecretStr(os.environ.get("POSTGRES_HOST", "postgres"))
    postgres_port: int = int(os.environ.get("POSTGRES_PORT", "5432"))

    class Config:
        env_file = ".env"
        extra = "allow"

    @property
    def async_database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user.get_secret_value()}:{self.postgres_password.get_secret_value()}"
            f"@{self.postgres_host.get_secret_value()}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def sync_database_url(self) -> str:
        """Used by Alembic (psychopg2)"""
        return (
            f"postgresql://{self.postgres_user.get_secret_value()}:{self.postgres_password.get_secret_value()}"
            f"@{self.postgres_host.get_secret_value()}:{self.postgres_port}/{self.postgres_db}"
        )


def get_config() -> Config:
    return Config()
