"""API REST: traduce peticiones HTTP a llamadas a services."""

import sqlite3
from typing import Annotated

from fastapi import Depends, FastAPI, Request, status
from fastapi.responses import JSONResponse

from app import services
from app.config import get_settings
from app.database import get_db
from app.models import Booking, BookingCreate, Room, RoomCreate

app = FastAPI(title="SmartCampus API", version="1.0.0")

Db = Annotated[sqlite3.Connection, Depends(get_db)]


# ---------- Errores de negocio -> códigos HTTP ----------


@app.exception_handler(services.NotFoundError)
async def not_found_handler(request: Request, exc: services.NotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(services.ConflictError)
async def conflict_handler(request: Request, exc: services.ConflictError):
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(services.BusinessRuleError)
async def business_rule_handler(request: Request, exc: services.BusinessRuleError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


# ---------- Health ----------


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "env": get_settings().app_env}


# ---------- Aulas ----------


@app.get("/rooms", response_model=list[Room])
def list_rooms(db: Db):
    return services.list_rooms(db)


@app.get("/rooms/{room_id}", response_model=Room)
def get_room(room_id: int, db: Db):
    return services.get_room(db, room_id)


@app.post("/rooms", response_model=Room, status_code=status.HTTP_201_CREATED)
def create_room(data: RoomCreate, db: Db):
    return services.create_room(db, data)


@app.delete("/rooms/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room(room_id: int, db: Db) -> None:
    services.delete_room(db, room_id)


# ---------- Reservas ----------


@app.get("/bookings", response_model=list[Booking])
def list_bookings(db: Db):
    return services.list_bookings(db)


@app.post("/bookings", response_model=Booking, status_code=status.HTTP_201_CREATED)
def create_booking(data: BookingCreate, db: Db):
    return services.create_booking(db, data)


@app.delete("/bookings/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_booking(booking_id: int, db: Db) -> None:
    services.delete_booking(db, booking_id)
