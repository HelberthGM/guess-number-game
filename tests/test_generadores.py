import random

import pytest

from juego_numero.generadores import Aleatorio, Fijo, Generador


def test_generador_es_abstracto() -> None:
    with pytest.raises(TypeError):
        Generador()  # type: ignore[abstract]


def test_aleatorio_respeta_el_rango() -> None:
    generador = Aleatorio(random.Random(1234))
    numeros = {generador.obtener(1, 6) for _ in range(200)}
    assert numeros == {1, 2, 3, 4, 5, 6}


def test_aleatorio_es_reproducible_con_la_misma_semilla() -> None:
    primero = Aleatorio(random.Random(7)).obtener(1, 100)
    segundo = Aleatorio(random.Random(7)).obtener(1, 100)
    assert primero == segundo


def test_fijo_devuelve_su_valor() -> None:
    assert Fijo(42).obtener(1, 100) == 42


def test_fijo_fuera_de_rango_falla() -> None:
    with pytest.raises(ValueError, match="fuera del rango"):
        Fijo(500).obtener(1, 100)
