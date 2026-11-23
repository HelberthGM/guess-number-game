"""Estrategias (patron Strategy) para elegir el numero secreto."""

from __future__ import annotations

import random
from abc import ABC, abstractmethod


class Generador(ABC):
    """Contrato comun de las estrategias de generacion.

    El contexto (``Juego``) depende solo de esta abstraccion, nunca de una
    implementacion concreta. Asi el algoritmo se puede intercambiar sin
    modificar la logica de la partida.
    """

    @abstractmethod
    def obtener(self, minimo: int, maximo: int) -> int:
        """Devuelve un entero dentro del rango inclusivo [minimo, maximo]."""


class Aleatorio(Generador):
    """Estrategia de produccion: un numero al azar dentro del rango."""

    def __init__(self, rng: random.Random | None = None) -> None:
        self._rng = rng or random.Random()

    def obtener(self, minimo: int, maximo: int) -> int:
        return self._rng.randint(minimo, maximo)


class Fijo(Generador):
    """Estrategia determinista: siempre devuelve el mismo numero.

    Existe para que los tests sean reproducibles sin parchear ``random``.
    """

    def __init__(self, valor: int) -> None:
        self._valor = valor

    def obtener(self, minimo: int, maximo: int) -> int:
        if not minimo <= self._valor <= maximo:
            raise ValueError(
                f"El valor fijo {self._valor} esta fuera del rango "
                f"[{minimo}, {maximo}]"
            )
        return self._valor
