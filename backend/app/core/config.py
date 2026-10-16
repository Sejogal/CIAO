from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    APP_NAME: str = "Conecta IoT"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # database
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    # jwt
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    DB_HOST: str = "postgres"
    DB_PORT: int = 5432
    DB_NAME: str = "conecta"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"

    REDIS_URL: str = "redis://redis:6379"

    MQTT_HOST: str = "emqx"
    MQTT_PORT: int = 1883
    MQTT_USERNAME: str = "admin"
    MQTT_PASSWORD: str = "public"
    EMQX_AUTH_SECRET: str = ""
    MQTT_DEVICE_OFFLINE_AFTER_SECONDS: int = 120
    MQTT_HEARTBEAT_CHECK_INTERVAL_SECONDS: int = 30

    SECRET_KEY: str

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


    @property
    def database_sync_url(self) -> str:
        return (
            f"postgresql+psycopg://"
            f"{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
