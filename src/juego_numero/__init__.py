"""Juego de adivinar el numero.

Arquitectura en tres capas, cada una con una sola responsabilidad:

- ``generadores``: estrategias (patron Strategy) para elegir el numero secreto.
- ``juego``: reglas de la partida, sin entrada ni salida.
- ``consola``: adaptador de consola y punto de entrada.
"""

from .generadores import Aleatorio, Fijo, Generador
from .juego import Juego, Resultado

__all__ = ["Aleatorio", "Fijo", "Generador", "Juego", "Resultado"]
__version__ = "0.1.0"
