def test_get_rooms_vacio(client):
    response = client.get("/rooms")
    assert response.status_code == 200
    assert response.json() == []


def test_post_room(client, room_payload):
    response = client.post("/rooms", json=room_payload)
    assert response.status_code == 201
    assert response.json() == {"id": 1, **room_payload}


def test_get_rooms_lista_las_creadas(client, room_payload):
    client.post("/rooms", json=room_payload)
    client.post("/rooms", json={**room_payload, "nombre": "Aula 2.3"})
    assert len(client.get("/rooms").json()) == 2


def test_get_room_por_id(client, room_id, room_payload):
    response = client.get(f"/rooms/{room_id}")
    assert response.status_code == 200
    assert response.json()["nombre"] == room_payload["nombre"]


def test_get_room_inexistente(client):
    assert client.get("/rooms/99").status_code == 404


def test_post_room_capacidad_cero(client, room_payload):
    response = client.post("/rooms", json={**room_payload, "capacidad": 0})
    assert response.status_code == 400


def test_post_room_capacidad_negativa(client, room_payload):
    response = client.post("/rooms", json={**room_payload, "capacidad": -3})
    assert response.status_code == 400


def test_post_room_sin_campos_obligatorios(client):
    assert client.post("/rooms", json={"nombre": "Aula"}).status_code == 422


def test_delete_room(client, room_id):
    assert client.delete(f"/rooms/{room_id}").status_code == 204
    assert client.get(f"/rooms/{room_id}").status_code == 404


def test_delete_room_inexistente(client):
    assert client.delete("/rooms/99").status_code == 404
