from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    ENV: str = "dev"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "cornerpocket"
    DB_USER: str = "cp"
    DB_PASSWORD: str = "changeme"
    JWT_SECRET: str = "change_me"
    CORS_ORIGINS: str = "http://localhost:19006,http://localhost:8081"

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
