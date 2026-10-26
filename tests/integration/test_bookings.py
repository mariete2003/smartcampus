def test_get_bookings_vacio(client):
    response = client.get("/bookings")
    assert response.status_code == 200
    assert response.json() == []


def test_post_booking(client, booking_payload):
    response = client.post("/bookings", json=booking_payload)
    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["hora_inicio"] == "10:00:00"


def test_get_bookings_lista_las_creadas(client, booking_payload):
    client.post("/bookings", json=booking_payload)
    assert len(client.get("/bookings").json()) == 1


def test_post_booking_aula_inexistente(client, booking_payload):
    response = client.post("/bookings", json={**booking_payload, "aula_id": 99})
    assert response.status_code == 404


def test_post_booking_hora_incorrecta(client, booking_payload):
    payload = {**booking_payload, "hora_inicio": "12:00", "hora_fin": "10:00"}
    assert client.post("/bookings", json=payload).status_code == 400


def test_post_booking_solapada(client, booking_payload):
    client.post("/bookings", json=booking_payload)
    solapada = {**booking_payload, "hora_inicio": "11:00", "hora_fin": "13:00"}
    response = client.post("/bookings", json=solapada)
    assert response.status_code == 409


def test_post_booking_contigua_permitida(client, booking_payload):
    client.post("/bookings", json=booking_payload)
    siguiente = {**booking_payload, "hora_inicio": "12:00", "hora_fin": "13:00"}
    assert client.post("/bookings", json=siguiente).status_code == 201


def test_post_booking_fecha_invalida(client, booking_payload):
    payload = {**booking_payload, "fecha": "no-es-una-fecha"}
    assert client.post("/bookings", json=payload).status_code == 422


def test_delete_booking(client, booking_payload):
    booking_id = client.post("/bookings", json=booking_payload).json()["id"]
    assert client.delete(f"/bookings/{booking_id}").status_code == 204
    assert client.get("/bookings").json() == []


def test_delete_booking_inexistente(client):
    assert client.delete("/bookings/99").status_code == 404
