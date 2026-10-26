import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Cliente HTTP contra la app, con una base de datos SQLite temporal por test."""
    monkeypatch.setenv("DB_PATH", str(tmp_path / "test.db"))
    monkeypatch.setenv("APP_ENV", "test")
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def room_payload():
    return {
        "nombre": "Laboratorio de Robótica",
        "edificio": "Edificio A",
        "capacidad": 30,
        "equipamiento": ["ordenadores", "robots", "impresora 3D"],
    }


@pytest.fixture
def room_id(client, room_payload):
    return client.post("/rooms", json=room_payload).json()["id"]


@pytest.fixture
def booking_payload(room_id):
    return {
        "aula_id": room_id,
        "usuario": "mario",
        "fecha": "2026-11-10",
        "hora_inicio": "10:00",
        "hora_fin": "12:00",
    }
