"""Adaptador de consola: traduce entrada/salida a llamadas al dominio."""

from __future__ import annotations

import argparse
import random
from collections.abc import Sequence

from .generadores import Aleatorio
from .juego import Juego, Resultado

PISTAS = {
    Resultado.MAYOR: "El numero secreto es mayor.",
    Resultado.MENOR: "El numero secreto es menor.",
}


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="juego-numero",
        description="Adivina el numero secreto en el menor numero de intentos.",
    )
    parser.add_argument("-n", "--minimo", type=int, default=1)
    parser.add_argument("-m", "--maximo", type=int, default=100)
    parser.add_argument("-i", "--intentos", type=int, default=7)
    parser.add_argument(
        "--semilla",
        type=int,
        default=None,
        help="Semilla del generador aleatorio (util para repetir partidas).",
    )
    return parser


def jugar(juego: Juego) -> None:
    print(
        f"Adivina el numero entre {juego.minimo} y {juego.maximo}. "
        f"Tienes {juego.max_intentos} intentos."
    )

    while juego.en_curso:
        try:
            entrada = input(f"[{juego.intentos + 1}/{juego.max_intentos}] Tu numero: ")
        except (EOFError, KeyboardInterrupt):
            print("\nPartida cancelada.")
            return

        try:
            numero = int(entrada)
        except ValueError:
            print("Introduce un numero entero.")
            continue

        try:
            resultado = juego.adivinar(numero)
        except ValueError as error:
            print(error)
            continue

        if resultado is Resultado.GANASTE:
            print(f"¡Correcto! Lo lograste en {juego.intentos} intentos.")
        elif resultado is Resultado.PERDISTE:
            print(f"Sin intentos. El numero era {juego.objetivo}.")
        else:
            print(PISTAS[resultado])


def main(argv: Sequence[str] | None = None) -> int:
    parser = construir_parser()
    args = parser.parse_args(argv)

    try:
        juego = Juego(
            Aleatorio(random.Random(args.semilla)),
            minimo=args.minimo,
            maximo=args.maximo,
            max_intentos=args.intentos,
        )
    except ValueError as error:
        parser.error(str(error))

    juego.nueva_partida()
    jugar(juego)
    return 0
