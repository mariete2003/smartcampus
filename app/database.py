"""Conexión a SQLite y creación de las tablas."""

import os
import sqlite3
from collections.abc import Iterator

from app.config import get_settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS rooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    edificio TEXT NOT NULL,
    capacidad INTEGER NOT NULL,
    equipamiento TEXT NOT NULL DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aula_id INTEGER NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
    usuario TEXT NOT NULL,
    fecha TEXT NOT NULL,
    hora_inicio TEXT NOT NULL,
    hora_fin TEXT NOT NULL
);
"""


def connect(db_path: str) -> sqlite3.Connection:
    folder = os.path.dirname(db_path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.commit()


def get_db() -> Iterator[sqlite3.Connection]:
    """Dependencia de FastAPI: abre una conexión por petición y la cierra al final."""
    conn = connect(get_settings().db_path)
    try:
        init_db(conn)
        yield conn
    finally:
        conn.close()
