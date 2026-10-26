"""Lógica de negocio: aquí viven las reglas, separadas de HTTP."""

import json
import sqlite3
from datetime import time

from app.models import Booking, BookingCreate, Room, RoomCreate


class NotFoundError(Exception):
    """El recurso pedido no existe (-> 404)."""


class ConflictError(Exception):
    """La operación choca con datos existentes (-> 409)."""


class BusinessRuleError(Exception):
    """Los datos no cumplen una regla de negocio (-> 400)."""


# ---------- Validaciones (funciones puras, fáciles de testear) ----------


def validate_capacity(capacidad: int) -> None:
    if capacidad <= 0:
        raise BusinessRuleError("La capacidad debe ser mayor que 0")


def validate_times(hora_inicio: time, hora_fin: time) -> None:
    if hora_inicio >= hora_fin:
        raise BusinessRuleError("La hora de inicio debe ser anterior a la hora de fin")


def overlaps(inicio_a: time, fin_a: time, inicio_b: time, fin_b: time) -> bool:
    """Dos franjas se solapan si cada una empieza antes de que acabe la otra."""
    return inicio_a < fin_b and inicio_b < fin_a


# ---------- Aulas ----------


def _row_to_room(row: sqlite3.Row) -> Room:
    return Room(
        id=row["id"],
        nombre=row["nombre"],
        edificio=row["edificio"],
        capacidad=row["capacidad"],
        equipamiento=json.loads(row["equipamiento"]),
    )


def create_room(conn: sqlite3.Connection, data: RoomCreate) -> Room:
    validate_capacity(data.capacidad)
    cur = conn.execute(
        "INSERT INTO rooms (nombre, edificio, capacidad, equipamiento) "
        "VALUES (?, ?, ?, ?)",
        (
            data.nombre,
            data.edificio,
            data.capacidad,
            json.dumps(data.equipamiento, ensure_ascii=False),
        ),
    )
    conn.commit()
    return Room(id=cur.lastrowid, **data.model_dump())


def list_rooms(conn: sqlite3.Connection) -> list[Room]:
    rows = conn.execute("SELECT * FROM rooms ORDER BY id").fetchall()
    return [_row_to_room(row) for row in rows]


def get_room(conn: sqlite3.Connection, room_id: int) -> Room:
    row = conn.execute("SELECT * FROM rooms WHERE id = ?", (room_id,)).fetchone()
    if row is None:
        raise NotFoundError(f"El aula {room_id} no existe")
    return _row_to_room(row)


def delete_room(conn: sqlite3.Connection, room_id: int) -> None:
    cur = conn.execute("DELETE FROM rooms WHERE id = ?", (room_id,))
    conn.commit()
    if cur.rowcount == 0:
        raise NotFoundError(f"El aula {room_id} no existe")


# ---------- Reservas ----------


def _row_to_booking(row: sqlite3.Row) -> Booking:
    return Booking(**dict(row))


def list_bookings(conn: sqlite3.Connection) -> list[Booking]:
    rows = conn.execute("SELECT * FROM bookings ORDER BY id").fetchall()
    return [_row_to_booking(row) for row in rows]


def create_booking(conn: sqlite3.Connection, data: BookingCreate) -> Booking:
    validate_times(data.hora_inicio, data.hora_fin)
    get_room(conn, data.aula_id)  # lanza NotFoundError si el aula no existe

    existentes = conn.execute(
        "SELECT hora_inicio, hora_fin FROM bookings WHERE aula_id = ? AND fecha = ?",
        (data.aula_id, data.fecha.isoformat()),
    ).fetchall()
    for row in existentes:
        inicio = time.fromisoformat(row["hora_inicio"])
        fin = time.fromisoformat(row["hora_fin"])
        if overlaps(data.hora_inicio, data.hora_fin, inicio, fin):
            raise ConflictError("El aula ya está reservada en esa franja horaria")

    cur = conn.execute(
        "INSERT INTO bookings (aula_id, usuario, fecha, hora_inicio, hora_fin) "
        "VALUES (?, ?, ?, ?, ?)",
        (
            data.aula_id,
            data.usuario,
            data.fecha.isoformat(),
            data.hora_inicio.isoformat(),
            data.hora_fin.isoformat(),
        ),
    )
    conn.commit()
    return Booking(id=cur.lastrowid, **data.model_dump())


def delete_booking(conn: sqlite3.Connection, booking_id: int) -> None:
    cur = conn.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
    conn.commit()
    if cur.rowcount == 0:
        raise NotFoundError(f"La reserva {booking_id} no existe")
