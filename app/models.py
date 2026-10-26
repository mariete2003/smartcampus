"""Esquemas de datos (lo que entra y sale de la API)."""

from datetime import date, time

from pydantic import BaseModel, Field


class RoomCreate(BaseModel):
    nombre: str = Field(min_length=1)
    edificio: str = Field(min_length=1)
    capacidad: int
    equipamiento: list[str] = Field(default_factory=list)


class Room(RoomCreate):
    id: int


class BookingCreate(BaseModel):
    aula_id: int
    usuario: str = Field(min_length=1)
    fecha: date
    hora_inicio: time
    hora_fin: time


class Booking(BookingCreate):
    id: int
