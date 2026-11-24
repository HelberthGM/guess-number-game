from juego_numero.app import create_app


def test_muestra_la_interfaz() -> None:
    client = create_app(testing=True).test_client()
    respuesta = client.get("/")

    assert respuesta.status_code == 200
    assert b"Adivina el n\xc3\xbamero" in respuesta.data
    assert b"Iniciar desaf\xc3\xado" in respuesta.data


def test_health_y_version() -> None:
    client = create_app(testing=True).test_client()

    health = client.get("/health")
    version = client.get("/version")

    assert health.status_code == 200
    assert health.get_json()["status"] == "ok"
    assert version.status_code == 200
    assert "version" in version.get_json()
    assert "commit" in version.get_json()


def test_nueva_partida_y_validacion() -> None:
    client = create_app(testing=True).test_client()

    nueva = client.post("/api/nueva", json={"minimo": 10, "maximo": 20})
    assert nueva.status_code == 200

    fuera = client.post("/api/adivinar", json={"numero": 21})
    assert fuera.status_code == 400
    assert "entre 10 y 20" in fuera.get_json()["error"]


def test_numero_invalido_no_gasta_intento() -> None:
    client = create_app(testing=True).test_client()
    client.post("/api/nueva", json={"minimo": 1, "maximo": 100})

    respuesta = client.post("/api/adivinar", json={"numero": "texto"})

    assert respuesta.status_code == 400


def test_reiniciar_permite_seguir_jugando() -> None:
    client = create_app(testing=True).test_client()
    client.post("/api/nueva", json={"minimo": 1, "maximo": 10})

    with client.session_transaction() as session:
        session["objetivo"] = 5

    ganada = client.post("/api/adivinar", json={"numero": 5})
    assert ganada.status_code == 200
    assert ganada.get_json()["resultado"] == "ganaste"

    reinicio = client.post("/api/nueva", json={"minimo": 1, "maximo": 10})
    assert reinicio.status_code == 200

    intento = client.post("/api/adivinar", json={"numero": 3})
    assert intento.status_code == 200
