const rangeForm = document.querySelector("#range-form");
const guessForm = document.querySelector("#guess-form");
const numeroInput = document.querySelector("#numero");
const guessButton = guessForm.querySelector("button");
const message = document.querySelector("#message");
const attempts = document.querySelector("#attempts");

function mostrarMensaje(texto, tipo = "") {
  message.textContent = texto;
  message.className = `message ${tipo}`.trim();
}

async function pedir(url, datos) {
  const respuesta = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(datos),
  });
  const cuerpo = await respuesta.json();
  if (!respuesta.ok) {
    throw new Error(cuerpo.error || "Ocurrio un error.");
  }
  return cuerpo;
}

rangeForm.addEventListener("submit", async (evento) => {
  evento.preventDefault();
  try {
    const datos = await pedir("/api/nueva", {
      minimo: Number(document.querySelector("#minimo").value),
      maximo: Number(document.querySelector("#maximo").value),
      max_intentos: 7,
    });
    numeroInput.min = datos.minimo;
    numeroInput.max = datos.maximo;
    numeroInput.value = "";
    numeroInput.disabled = false;
    guessButton.disabled = false;
    mostrarMensaje(datos.mensaje);
    attempts.textContent = "Intentos realizados: 0";
    numeroInput.focus();
  } catch (error) {
    mostrarMensaje(error.message, "error");
  }
});

guessForm.addEventListener("submit", async (evento) => {
  evento.preventDefault();
  try {
    const datos = await pedir("/api/adivinar", {
      numero: Number(numeroInput.value),
    });
    attempts.textContent = `Intentos realizados: ${datos.intentos_realizados}`;
    mostrarMensaje(
      datos.mensaje,
      datos.resultado === "ganaste" ? "success" : ""
    );
    if (!datos.en_curso) {
      numeroInput.disabled = true;
      guessButton.disabled = true;
    }
  } catch (error) {
    mostrarMensaje(error.message, "error");
  }
});
