from datetime import date, time

import pytest

from app import services
from app.models import BookingCreate, RoomCreate


def make_room(conn, capacidad=30):
    return services.create_room(
        conn,
        RoomCreate(
            nombre="Laboratorio de Robótica",
            edificio="Edificio A",
            capacidad=capacidad,
            equipamiento=["ordenadores", "robots"],
        ),
    )


def make_booking(conn, aula_id, inicio="10:00", fin="12:00", fecha="2026-11-10"):
    return services.create_booking(
        conn,
        BookingCreate(
            aula_id=aula_id,
            usuario="mario",
            fecha=date.fromisoformat(fecha),
            hora_inicio=time.fromisoformat(inicio),
            hora_fin=time.fromisoformat(fin),
        ),
    )


# ---------- Validaciones puras ----------


@pytest.mark.parametrize("capacidad", [0, -5])
def test_validate_capacity_rechaza_cero_o_negativa(capacidad):
    with pytest.raises(services.BusinessRuleError):
        services.validate_capacity(capacidad)


def test_validate_capacity_acepta_positiva():
    services.validate_capacity(1)  # no lanza excepción


def test_validate_times_rechaza_inicio_posterior_al_fin():
    with pytest.raises(services.BusinessRuleError):
        services.validate_times(time(12, 0), time(10, 0))


def test_validate_times_rechaza_inicio_igual_al_fin():
    with pytest.raises(services.BusinessRuleError):
        services.validate_times(time(10, 0), time(10, 0))


@pytest.mark.parametrize(
    ("a", "b", "esperado"),
    [
        (("10:00", "12:00"), ("11:00", "13:00"), True),  # ejemplo del enunciado
        (("10:00", "12:00"), ("09:00", "10:30"), True),  # empieza antes
        (("10:00", "12:00"), ("10:30", "11:30"), True),  # dentro
        (("10:00", "12:00"), ("12:00", "13:00"), False),  # justo a continuación
        (("10:00", "12:00"), ("08:00", "10:00"), False),  # justo antes
    ],
)
def test_overlaps(a, b, esperado):
    franja_a = [time.fromisoformat(h) for h in a]
    franja_b = [time.fromisoformat(h) for h in b]
    assert services.overlaps(*franja_a, *franja_b) is esperado


# ---------- Aulas ----------


def test_create_room_asigna_id_y_guarda_datos(conn):
    room = make_room(conn)
    assert room.id == 1
    assert services.get_room(conn, room.id).equipamiento == ["ordenadores", "robots"]


def test_create_room_capacidad_invalida_no_guarda_nada(conn):
    with pytest.raises(services.BusinessRuleError):
        make_room(conn, capacidad=0)
    assert services.list_rooms(conn) == []


def test_get_room_inexistente(conn):
    with pytest.raises(services.NotFoundError):
        services.get_room(conn, 99)


def test_delete_room(conn):
    room = make_room(conn)
    services.delete_room(conn, room.id)
    assert services.list_rooms(conn) == []


def test_delete_room_inexistente(conn):
    with pytest.raises(services.NotFoundError):
        services.delete_room(conn, 99)


# ---------- Reservas ----------


def test_create_booking(conn):
    room = make_room(conn)
    booking = make_booking(conn, room.id)
    assert booking.id == 1
    assert len(services.list_bookings(conn)) == 1


def test_create_booking_aula_inexistente(conn):
    with pytest.raises(services.NotFoundError):
        make_booking(conn, aula_id=99)


def test_create_booking_hora_incorrecta(conn):
    room = make_room(conn)
    with pytest.raises(services.BusinessRuleError):
        make_booking(conn, room.id, inicio="12:00", fin="10:00")


def test_create_booking_solapada(conn):
    room = make_room(conn)
    make_booking(conn, room.id, "10:00", "12:00")
    with pytest.raises(services.ConflictError):
        make_booking(conn, room.id, "11:00", "13:00")


def test_misma_franja_otro_dia_no_es_solape(conn):
    room = make_room(conn)
    make_booking(conn, room.id, fecha="2026-11-10")
    make_booking(conn, room.id, fecha="2026-11-11")
    assert len(services.list_bookings(conn)) == 2


def test_misma_franja_otra_aula_no_es_solape(conn):
    aula_1 = make_room(conn)
    aula_2 = make_room(conn)
    make_booking(conn, aula_1.id)
    make_booking(conn, aula_2.id)
    assert len(services.list_bookings(conn)) == 2


def test_delete_booking(conn):
    room = make_room(conn)
    booking = make_booking(conn, room.id)
    services.delete_booking(conn, booking.id)
    assert services.list_bookings(conn) == []


def test_delete_booking_inexistente(conn):
    with pytest.raises(services.NotFoundError):
        services.delete_booking(conn, 99)


def test_borrar_aula_borra_sus_reservas(conn):
    room = make_room(conn)
    make_booking(conn, room.id)
    services.delete_room(conn, room.id)
    assert services.list_bookings(conn) == []
