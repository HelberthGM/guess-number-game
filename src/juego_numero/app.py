import os

from flask import Flask, jsonify, render_template, request, session
from flask_wtf.csrf import CSRFProtect, generate_csrf

from .generadores import Aleatorio, Fijo
from .juego import Juego, Resultado


def _partida_desde_sesion() -> Juego:
    minimo = int(session.get("minimo", 1))
    maximo = int(session.get("maximo", 100))
    max_intentos = int(session.get("max_intentos", 7))
    objetivo = session.get("objetivo")
    generador = Fijo(int(objetivo)) if objetivo is not None else Aleatorio()
    juego = Juego(generador, minimo, maximo, max_intentos)
    if objetivo is not None:
        juego.nueva_partida()
        juego.intentos = int(session.get("intentos", 0))
        if session.get("resultado") == "ganaste":
            juego.resultado = Resultado.GANASTE
            juego.en_curso = False
        elif session.get("resultado") == "perdiste":
            juego.resultado = Resultado.PERDISTE
            juego.en_curso = False
        else:
            juego.en_curso = True
    return juego


def _guardar_estado(juego: Juego) -> None:
    session["minimo"] = juego.minimo
    session["maximo"] = juego.maximo
    session["max_intentos"] = juego.max_intentos
    session["intentos"] = juego.intentos
    session["en_curso"] = juego.en_curso
    session["resultado"] = juego.resultado.value if juego.resultado else None
    if juego._objetivo is not None:
        session["objetivo"] = juego._objetivo


def create_app(testing: bool = False) -> Flask:
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "juego-numero-desarrollo")
    app.config["WTF_CSRF_ENABLED"] = not testing
    csrf = CSRFProtect()
    csrf.init_app(app)

    @app.context_processor
    def variables_globales():
        return {"csrf_token": generate_csrf}

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"}), 200

    @app.get("/version")
    def version():
        commit = (
            os.getenv("APP_COMMIT")
            or os.getenv("RENDER_GIT_COMMIT")
            or os.getenv("SOURCE_COMMIT")
            or "unknown"
        )
        version = os.getenv("APP_VERSION")
        if version in (None, "", "main", "latest", "unknown"):
            version = "1.0.1"
        return jsonify(
            {
                "version": version,
                "commit": commit[:7],
            }
        )

    @app.get("/")
    def index():
        minimo = int(request.args.get("minimo", session.get("minimo", 1)))
        maximo = int(request.args.get("maximo", session.get("maximo", 100)))
        return render_template("index.html", minimo=minimo, maximo=maximo)

    def datos_json():
        datos = request.get_json(silent=True)
        if datos is None:
            datos = request.form
        return datos

    @app.post("/api/nueva")
    @app.post("/nueva_partida")
    def nueva_partida():
        datos = datos_json()
        try:
            minimo = int(datos.get("minimo", datos.get("min", 1)))
            maximo = int(datos.get("maximo", datos.get("max", 100)))
            max_intentos = int(datos.get("max_intentos", datos.get("intentos", 7)))
            juego = Juego(Aleatorio(), minimo, maximo, max_intentos)
            juego.nueva_partida()
        except (TypeError, ValueError):
            return jsonify({"error": "Parámetros inválidos."}), 400

        _guardar_estado(juego)
        return jsonify(
            {
                "minimo": juego.minimo,
                "maximo": juego.maximo,
                "intentos": juego.intentos,
                "intentos_realizados": juego.intentos,
                "intentos_restantes": juego.intentos_restantes,
                "en_curso": juego.en_curso,
                "mensaje": "Nueva partida iniciada.",
            }
        )

    @app.post("/api/adivinar")
    @app.post("/adivinar")
    def adivinar():
        
        datos = datos_json()
        valor = datos.get("numero", datos.get("intento"))
        if valor in (None, ""):
            return jsonify({"error": "Ingresa un numero para realizar el intento."}), 400
        try:
            numero = int(valor)
        except (TypeError, ValueError):
            return jsonify({"error": "El intento debe ser un numero entero."}), 400

        juego = _partida_desde_sesion()
        if not juego.en_curso:
            return jsonify({"error": "Inicia una nueva partida."}), 400
        try:
            resultado = juego.adivinar(numero)
        except ValueError:
            app.logger.info("Intento inválido en /adivinar")
            return jsonify(
                {"error": f"El numero debe estar entre {juego.minimo} y {juego.maximo}"}
            ), 400
        except RuntimeError:
            app.logger.exception("Error al procesar intento en /adivinar")
            return jsonify({"error": "No se pudo procesar el intento."}), 400

        _guardar_estado(juego)
        respuesta = {
            "resultado": resultado.value,
            "intentos": juego.intentos,
            "intentos_realizados": juego.intentos,
            "intentos_restantes": juego.intentos_restantes,
            "en_curso": juego.en_curso,
        }
        if resultado is Resultado.MAYOR:
            respuesta["mensaje"] = "El numero secreto es mayor."
        elif resultado is Resultado.MENOR:
            respuesta["mensaje"] = "El numero secreto es menor."
        elif resultado is Resultado.GANASTE:
            respuesta["mensaje"] = (
                f"¡Felicitaciones! Adivinaste el numero en {juego.intentos} "
                "intento(s)."
            )
        else:
            respuesta["mensaje"] = (
                f"Perdiste. El numero secreto era {juego.objetivo}."
            )
        return jsonify(respuesta)

    @app.get("/api/estado")
    def estado():
        juego = _partida_desde_sesion()
        return jsonify(
            {
                "minimo": juego.minimo,
                "maximo": juego.maximo,
                "intentos": juego.intentos,
                "intentos_realizados": juego.intentos,
                "intentos_restantes": juego.intentos_restantes,
                "en_curso": juego.en_curso,
                "resultado": juego.resultado.value if juego.resultado else None,
            }
        )

    return app


app = create_app()
