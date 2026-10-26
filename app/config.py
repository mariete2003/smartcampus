"""Configuración leída de variables de entorno (nada fijo en el código)."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_env: str
    app_port: int
    db_path: str


def get_settings() -> Settings:
    return Settings(
        app_env=os.getenv("APP_ENV", "development"),
        app_port=int(os.getenv("APP_PORT", "8000")),
        db_path=os.getenv("DB_PATH", "smartcampus.db"),
    )
