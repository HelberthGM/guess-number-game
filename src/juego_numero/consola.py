import argparse

from .generadores import Aleatorio
from .juego import Juego, Resultado


def main() -> None:
    parser = argparse.ArgumentParser(description="Adivina el numero")
    parser.add_argument("--minimo", type=int, default=1)
    parser.add_argument("--maximo", type=int, default=100)
    parser.add_argument("-i", "--intentos", type=int, default=7)
    argumentos = parser.parse_args()

    juego = Juego(Aleatorio(), argumentos.minimo, argumentos.maximo, argumentos.intentos)
    juego.nueva_partida()
    print(
        f"Adivina un numero entre {juego.minimo} y {juego.maximo}. "
        f"Tienes {juego.max_intentos} intentos."
    )

    while juego.en_curso:
        try:
            numero = int(input("Tu numero: "))
            resultado = juego.adivinar(numero)
        except ValueError as error:
            print(error)
            continue

        if resultado is Resultado.MAYOR:
            print("El numero secreto es mayor.")
        elif resultado is Resultado.MENOR:
            print("El numero secreto es menor.")
        elif resultado is Resultado.GANASTE:
            print(f"¡Correcto! Lo lograste en {juego.intentos} intentos.")
        else:
            print(f"Perdiste. El numero secreto era {juego.objetivo}.")
