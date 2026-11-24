import json
import os
import re
import subprocess
import time
from http.cookiejar import CookieJar
from urllib.error import URLError
from urllib.request import HTTPCookieProcessor, Request, build_opener, urlopen

import pytest

pytestmark = pytest.mark.integration


def ejecutar(*argumentos: str, entorno: dict[str, str] | None = None) -> None:
    variables = os.environ.copy()
    if entorno:
        variables.update(entorno)
    subprocess.run(argumentos, check=True, env=variables)


def obtener(url: str) -> dict:
    with urlopen(url, timeout=5) as respuesta:
        assert respuesta.status == 200
        return json.loads(respuesta.read())


def solicitar(url: str, datos: dict, token: str | None = None,
              opener=None) -> tuple[int, dict]:
    headers = {"Content-Type": "application/json"}
    if token:
        headers["X-CSRFToken"] = token
    solicitud = Request(
        url,
        data=json.dumps(datos).encode(),
        headers=headers,
        method="POST",
    )
    lector = opener.open if opener else urlopen
    with lector(solicitud, timeout=5) as respuesta:
        return respuesta.status, json.loads(respuesta.read())


def test_compose_sirve_la_aplicacion() -> None:
    try:
        subprocess.run(
            ["docker", "compose", "version"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        pytest.skip("Docker Compose no está disponible")

    puerto = "18081"
    entorno = {"PORT": puerto, "APP_VERSION": "1.0.1", "APP_COMMIT": "integration"}

    ejecutar(
        "docker",
        "compose",
        "up",
        "--build",
        "-d",
        entorno=entorno,
    )

    try:
        base_url = f"http://127.0.0.0:{puerto}"
        for _ in range(30):
            try:
                salud = obtener(f"{base_url}/health")
                break
            except (URLError, TimeoutError, ConnectionResetError):
                time.sleep(1)
        else:
            pytest.fail("La aplicación no respondió en /health")

        assert salud == {"status": "ok"}

        cookies = CookieJar()
        opener = build_opener(HTTPCookieProcessor(cookies))
        with opener.open(f"{base_url}/", timeout=5) as respuesta:
            assert respuesta.status == 200
            pagina = respuesta.read()
            assert b"Adivina el" in pagina

        coincidencia = re.search(
            rb'<meta name="csrf-token" content="([^"]+)">',
            pagina,
        )
        assert coincidencia
        token = coincidencia.group(1).decode()

        version = obtener(f"{base_url}/version")
        assert version["version"] == "1.0.1"
        assert version["commit"] == "integra"

        estado, nueva = solicitar(
            f"{base_url}/api/nueva",
            {"minimo": 10, "maximo": 20},
            token,
            opener,
        )
        assert estado == 200
        assert nueva["en_curso"] is True
    finally:
        ejecutar("docker", "compose", "down", "--remove-orphans", entorno=entorno)
