import random
from abc import ABC, abstractmethod


class Generador(ABC):
    @abstractmethod
    def obtener(self, minimo: int, maximo: int) -> int:
        pass


class Aleatorio(Generador):
    def __init__(self, generador: random.Random | None = None) -> None:
        self._generador = generador or random.Random()

    def obtener(self, minimo: int, maximo: int) -> int:
        return self._generador.randint(minimo, maximo)


class Fijo(Generador):
    def __init__(self, valor: int) -> None:
        self.valor = valor

    def obtener(self, minimo: int, maximo: int) -> int:
        if not minimo <= self.valor <= maximo:
            raise ValueError(
                f"El valor fijo {self.valor} esta fuera del rango "
                f"entre {minimo} y {maximo}"
            )
        return self.valor
