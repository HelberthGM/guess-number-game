from enum import Enum

from .generadores import Generador


class Resultado(Enum):
    MAYOR = "mayor"
    MENOR = "menor"
    GANASTE = "ganaste"
    PERDISTE = "perdiste"


class PartidaNoIniciadaError(RuntimeError):
    pass


class PartidaTerminadaError(RuntimeError):
    pass


class Juego:
    def __init__(
        self,
        generador: Generador,
        minimo: int = 1,
        maximo: int = 100,
        max_intentos: int = 7,
    ) -> None:
        if minimo >= maximo:
            raise ValueError("El minimo debe ser menor que el maximo")
        if max_intentos < 1:
            raise ValueError("Debe haber al menos 1 intento")

        self.generador = generador
        self.minimo = minimo
        self.maximo = maximo
        self.max_intentos = max_intentos
        self._objetivo: int | None = None
        self.intentos = 0
        self.resultado: Resultado | None = None
        self.en_curso = False

    def nueva_partida(self) -> None:
        self._objetivo = self.generador.obtener(self.minimo, self.maximo)
        self.intentos = 0
        self.resultado = None
        self.en_curso = True

    @property
    def objetivo(self) -> int:
        if self._objetivo is None:
            raise PartidaNoIniciadaError("La partida no ha sido iniciada")
        return self._objetivo

    @property
    def intentos_restantes(self) -> int:
        return max(0, self.max_intentos - self.intentos)

    def adivinar(self, numero: int) -> Resultado:
        if not self.en_curso:
            if self.resultado is not None:
                raise PartidaTerminadaError("La partida ya termino")
            raise PartidaNoIniciadaError("La partida no ha sido iniciada")
        if not self.minimo <= numero <= self.maximo:
            raise ValueError(
                f"El numero debe estar entre {self.minimo} y {self.maximo}"
            )

        self.intentos += 1
        if numero == self._objetivo:
            self.resultado = Resultado.GANASTE
            self.en_curso = False
            return self.resultado
        if self.intentos >= self.max_intentos:
            self.resultado = Resultado.PERDISTE
            self.en_curso = False
            return self.resultado
        if self._objetivo is not None and numero < self._objetivo:
            return Resultado.MAYOR
        return Resultado.MENOR
