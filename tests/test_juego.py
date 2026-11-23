import pytest

from juego_numero import Aleatorio, Fijo, Juego, Resultado
from juego_numero.juego import PartidaNoIniciadaError, PartidaTerminadaError


def crear_juego(**kwargs) -> Juego:
    juego = Juego(Fijo(42), **kwargs)
    juego.nueva_partida()
    return juego


def test_gana_al_acertar() -> None:
    juego = crear_juego()

    assert juego.adivinar(42) is Resultado.GANASTE
    assert not juego.en_curso
    assert juego.resultado is Resultado.GANASTE
    assert juego.intentos == 1


def test_indica_si_el_numero_secreto_es_mayor_o_menor() -> None:
    juego = crear_juego()

    assert juego.adivinar(10) is Resultado.MAYOR
    assert juego.adivinar(90) is Resultado.MENOR


def test_pierde_al_agotar_los_intentos() -> None:
    juego = crear_juego(max_intentos=3)

    assert juego.adivinar(1) is Resultado.MAYOR
    assert juego.adivinar(2) is Resultado.MAYOR
    assert juego.adivinar(3) is Resultado.PERDISTE
    assert juego.intentos_restantes == 0
    assert not juego.en_curso


def test_revela_el_objetivo_al_terminar() -> None:
    juego = crear_juego(max_intentos=1)
    juego.adivinar(1)

    assert juego.objetivo == 42


def test_la_estrategia_se_intercambia_sin_tocar_el_juego() -> None:
    fijo = crear_juego()
    aleatorio = Juego(Aleatorio())
    aleatorio.nueva_partida()

    assert fijo.adivinar(42) is Resultado.GANASTE
    assert aleatorio.minimo <= aleatorio.objetivo <= aleatorio.maximo


def test_no_se_puede_jugar_sin_iniciar_partida() -> None:
    with pytest.raises(PartidaNoIniciadaError):
        Juego(Fijo(42)).adivinar(42)


def test_no_se_puede_seguir_jugando_tras_terminar() -> None:
    juego = crear_juego()
    juego.adivinar(42)

    with pytest.raises(PartidaTerminadaError):
        juego.adivinar(42)


def test_rechaza_numeros_fuera_de_rango_sin_gastar_intentos() -> None:
    juego = crear_juego(minimo=1, maximo=100)

    with pytest.raises(ValueError, match="entre 1 y 100"):
        juego.adivinar(101)

    assert juego.intentos == 0


def test_nueva_partida_reinicia_los_intentos() -> None:
    juego = crear_juego(max_intentos=2)
    juego.adivinar(1)
    juego.adivinar(2)
    assert not juego.en_curso

    juego.nueva_partida()

    assert juego.en_curso
    assert juego.intentos == 0
    assert juego.resultado is None


def test_valida_la_configuracion() -> None:
    with pytest.raises(ValueError, match="menor que"):
        Juego(Fijo(1), minimo=10, maximo=1)

    with pytest.raises(ValueError, match="al menos 1"):
        Juego(Fijo(1), max_intentos=0)
