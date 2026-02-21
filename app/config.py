# app/config.py

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Backend Lectura Contadores"
    APP_VERSION: str = "0.1.0"

    class Config:
        env_file = ".env"


settings = Settings()
