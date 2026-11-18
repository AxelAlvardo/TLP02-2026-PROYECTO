"""tlp/espanol/llm_experimento.py - Fase 2 (punto 6): ¿sigue un LLM las reglas de la gramática formal?

Le da a un LLM (Claude, ChatGPT o Gemini) las reglas de producción y el léxico de la gramática, y le pide analizar
las oraciones del conjunto de prueba siguiendo SOLO esas reglas. Compara cada respuesta con lo que espera la
gramática (el veredicto del parser propio) y escribe un .md con un resumen y todas las respuestas.

Configuración: archivo .env en la raíz del proyecto (plantilla: .env.ejemplo)
  ANTHROPIC_API_KEY (Claude) | OPENAI_API_KEY (ChatGPT) | GEMINI_API_KEY (Gemini)   llena SOLO la que vas a usar
  LLM_MODELO                                                                      nombre del modelo de ese proveedor
Prompt: casos/espanol/prompt_llm.txt (edítalo para agregar o quitar ejemplos: zero-shot / few-shot).

Uso:  python -m tlp.espanol.llm_experimento              # las 71 oraciones
      python -m tlp.espanol.llm_experimento --limite 5   # solo las 5 primeras (prueba barata)
Salida: resultados/fase2/llm/respuestas_<proveedor>_<modelo>_<fecha-hora>.md

Resumen (referencia = lo que acepta la gramática, es decir, el veredicto del parser propio):
  coincide                      el LLM da el mismo veredicto que la gramática
  desviación hacia el español   el LLM ACEPTA una oración que la gramática rechaza pero que SÍ es español correcto
  aceptó una agramatical        el LLM ACEPTA una oración que la gramática rechaza y que NO es español correcto
  sobre-rechazo                 el LLM RECHAZA una oración que la gramática sí deriva
  sin respuesta válida          error de la API o respuesta sin un JSON con "acepta"
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from collections import Counter
from dataclasses import dataclass
from datetime import datetime

from .conjunto import RAIZ, Caso, cargar_conjunto
from .gramatica_es import REGLAS_BNF, ParserEspanol, lexico_para_prompt

RUTA_ENV = os.path.join(RAIZ, ".env")
RUTA_PROMPT = os.path.join(RAIZ, "casos", "espanol", "prompt_llm.txt")
DESTINO = os.path.join(RAIZ, "resultados", "fase2", "llm")
PROVEEDORES = {"ANTHROPIC_API_KEY": "claude", "OPENAI_API_KEY": "chatgpt", "GEMINI_API_KEY": "gemini"}
MAX_TOKENS = 4096                 # holgado: en los modelos de razonamiento, lo que "piensan" también cuenta
ESPERAS_LIMITE = (10, 20, 40)     # segundos de espera si el proveedor responde "límite de peticiones"
LIMITE_PETICIONES = ("429", "rate limit", "rate_limit", "too many requests", "quota", "resource_exhausted")


class ErrorConfiguracion(Exception):
    pass


# ------------------------------------------------------------------ configuración (.env) y prompt
def leer_env(ruta: str = RUTA_ENV) -> dict[str, str]:
    """Lee el archivo .env: líneas CLAVE=valor; las que empiezan con '#' son comentarios."""
    if not os.path.exists(ruta):
        raise ErrorConfiguracion(f"No existe {ruta}. Copia .env.ejemplo como .env y llena tu clave y LLM_MODELO.")
    valores = {}
    with open(ruta, encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if linea and not linea.startswith("#") and "=" in linea:
                clave, valor = linea.split("=", 1)
                valores[clave.strip()] = valor.strip().strip('"').strip("'")
    return valores


def elegir_proveedor(valores: dict[str, str]) -> tuple[str, str, str]:
    """(proveedor, clave, modelo) según la ÚNICA clave de API llena en el .env."""
    llenas = [k for k in PROVEEDORES if valores.get(k)]
    if not llenas:
        raise ErrorConfiguracion("No hay ninguna clave de API en .env. Llena UNA de estas líneas: "
                                 "ANTHROPIC_API_KEY (Claude), OPENAI_API_KEY (ChatGPT) o GEMINI_API_KEY (Gemini).")
    if len(llenas) > 1:
        raise ErrorConfiguracion(f"Hay más de una clave en .env ({', '.join(llenas)}). "
                                 "Deja solo la del proveedor que quieres usar.")
    modelo = valores.get("LLM_MODELO", "")
    if not modelo:
        raise ErrorConfiguracion("Falta LLM_MODELO en .env: escribe el nombre del modelo que quieres usar.")
    return PROVEEDORES[llenas[0]], valores[llenas[0]], modelo


def leer_prompt(ruta: str = RUTA_PROMPT) -> tuple[str, str]:
    """(instrucciones de sistema, plantilla del mensaje). Quita los comentarios '#' y separa las dos secciones."""
    with open(ruta, encoding="utf-8") as f:
        texto = "\n".join(l for l in f.read().splitlines() if not l.lstrip().startswith("#"))
    if "=== SISTEMA ===" not in texto or "=== USUARIO ===" not in texto:
        raise ErrorConfiguracion(f"{ruta} debe tener las secciones '=== SISTEMA ===' y '=== USUARIO ==='.")
    sistema, usuario = texto.split("=== USUARIO ===", 1)
    sistema, usuario = sistema.split("=== SISTEMA ===", 1)[1].strip(), usuario.strip()
    if "{oracion}" not in usuario:
        raise ErrorConfiguracion(f"La sección USUARIO de {ruta} debe incluir la marca {{oracion}}.")
    return sistema, usuario


def completar(plantilla: str, oracion: str) -> str:
    """Inserta la gramática, el léxico y la oración en la plantilla del prompt."""
    return (plantilla.replace("{gramatica}", REGLAS_BNF).replace("{lexico}", lexico_para_prompt())
            .replace("{oracion}", oracion))


def contar_ejemplos(plantilla: str) -> int:
    """Número de ejemplos resueltos del prompt (líneas 'Oración: ...' sin contar la de {oracion})."""
    return sum(1 for l in plantilla.splitlines() if l.startswith("Oración:") and "{oracion}" not in l)


# ------------------------------------------------------------------ llamada al LLM
def crear_cliente(proveedor: str, clave: str, modelo: str):
    """Devuelve llamar(sistema, mensaje) -> (texto de la respuesta, nota) para el proveedor elegido."""
    if proveedor == "claude":
        import anthropic
        cliente = anthropic.Anthropic(api_key=clave)

        def pedir(sistema, mensaje, **extra):
            r = cliente.messages.create(model=modelo, max_tokens=MAX_TOKENS, system=sistema,
                                        messages=[{"role": "user", "content": mensaje}], **extra)
            return "".join(b.text for b in r.content if getattr(b, "type", "") == "text")
    elif proveedor == "chatgpt":
        import openai
        cliente = openai.OpenAI(api_key=clave)

        def pedir(sistema, mensaje, **extra):
            r = cliente.chat.completions.create(model=modelo, max_completion_tokens=MAX_TOKENS, **extra,
                                                messages=[{"role": "system", "content": sistema},
                                                          {"role": "user", "content": mensaje}])
            return r.choices[0].message.content or ""
    else:
        from google import genai
        from google.genai import types
        cliente = genai.Client(api_key=clave)

        def pedir(sistema, mensaje, **extra):
            config = types.GenerateContentConfig(system_instruction=sistema, max_output_tokens=MAX_TOKENS, **extra)
            return cliente.models.generate_content(model=modelo, contents=mensaje, config=config).text or ""

    def llamar(sistema: str, mensaje: str) -> tuple[str, str]:
        extra, nota = {"temperature": 0}, ""
        for espera in (*ESPERAS_LIMITE, None):
            try:
                return pedir(sistema, mensaje, **extra), nota
            except Exception as e:                                       # noqa: BLE001 (cada SDK tiene sus clases)
                texto = str(e).lower()
                if "temperature" in texto and extra:                     # modelos que no aceptan temperature=0
                    extra, nota = {}, "el modelo no acepta temperature=0; se usó su temperatura por defecto"
                    continue
                if espera is not None and any(s in texto for s in LIMITE_PETICIONES):
                    time.sleep(espera)
                    continue
                raise
        raise RuntimeError("se agotaron los reintentos por límite de peticiones")
    return llamar


def extraer_json(texto: str) -> dict | None:
    m = re.search(r"\{.*\}", texto or "", re.S)
    if not m:
        return None
    try:
        j = json.loads(m.group())
    except json.JSONDecodeError:
        return None
    return j if isinstance(j, dict) else None


def _veredicto(j: dict | None) -> bool | None:
    """Valor de "acepta" en la respuesta (admite true/false o 'true'/'false'); None si no es válido."""
    v = (j or {}).get("acepta")
    if isinstance(v, bool):
        return v
    if isinstance(v, str) and v.strip().lower() in ("true", "false", "sí", "si", "no"):
        return v.strip().lower() in ("true", "sí", "si")
    return None


# ------------------------------------------------------------------ experimento
@dataclass
class Respuesta:
    caso: Caso
    esperado: bool                 # lo que acepta la gramática (veredicto del parser propio)
    texto: str                     # respuesta cruda del LLM
    nota: str = ""
    error: str = ""

    @property
    def llm(self) -> bool | None:
        return _veredicto(extraer_json(self.texto))

    @property
    def resultado(self) -> str:
        if self.llm is None:
            return "sin respuesta válida"
        if self.llm == self.esperado:
            return "coincide"
        if self.llm:
            return "desviación hacia el español" if self.caso.gramatical_es else "aceptó una agramatical"
        return "sobre-rechazo"


def ejecutar(casos: list[Caso], llamar, sistema: str, plantilla: str, progreso=print) -> list[Respuesta]:
    parser, respuestas = ParserEspanol(), []
    for i, c in enumerate(casos, 1):
        esperado = parser.parse(c.oracion)[0] is not None
        texto, nota, error = "", "", ""
        try:
            texto, nota = llamar(sistema, completar(plantilla, c.oracion))
        except Exception as e:                                           # noqa: BLE001
            error = f"{type(e).__name__}: {e}"
            if i == 1:                                                   # clave o modelo mal escritos: no seguir
                raise ErrorConfiguracion(f"La primera llamada al LLM falló ({error}). "
                                         "Revisa la clave y LLM_MODELO en .env.") from e
        r = Respuesta(c, esperado, texto, nota, error)
        respuestas.append(r)
        progreso(f"[{i}/{len(casos)}] {c.oracion} -> {r.resultado}")
    return respuestas


def _veredicto_txt(v: bool | None) -> str:
    return "—" if v is None else ("ACEPTA" if v else "RECHAZA")


def escribir_md(respuestas: list[Respuesta], proveedor: str, modelo: str, sistema: str, plantilla: str,
                ruta: str) -> str:
    n, cuenta = len(respuestas), Counter(r.resultado for r in respuestas)
    L = [f"# Respuestas del LLM — {proveedor} / {modelo}", "",
         f"- Fecha: {datetime.now():%Y-%m-%d %H:%M}",
         f"- Prompt: `casos/espanol/prompt_llm.txt` con {contar_ejemplos(plantilla)} ejemplos resueltos "
         "(0 = zero-shot)",
         f"- Oraciones analizadas: {n}", "",
         "## Resumen", "",
         "Referencia: lo que acepta la gramática (veredicto del parser propio).", "",
         "| Resultado | Oraciones |", "|---|---|",
         f"| Coincide con la gramática | {cuenta['coincide']}/{n} |",
         f"| Desviación hacia el español (acepta lo que la gramática rechaza, pero es español correcto) | "
         f"{cuenta['desviación hacia el español']} |",
         f"| Aceptó una oración agramatical | {cuenta['aceptó una agramatical']} |",
         f"| Sobre-rechazo (rechaza lo que la gramática deriva) | {cuenta['sobre-rechazo']} |",
         f"| Sin respuesta válida | {cuenta['sin respuesta válida']} |", "",
         "## Prompt usado", "", "### Sistema", "", "````text", sistema, "````", "",
         "### Usuario (la marca {oracion} se reemplaza por cada oración)", "",
         "````text", plantilla.replace("{gramatica}", REGLAS_BNF).replace("{lexico}", lexico_para_prompt()), "````",
         "", "## Respuestas", ""]
    for r in respuestas:
        c = r.caso
        L += [f"### [{c.id:02d}] {c.oracion}", "",
              f"- Nivel {c.nivel} · español correcto: {'sí' if c.gramatical_es else 'no'} · fenómeno: {c.fenomeno}",
              f"- Esperado (gramática): **{_veredicto_txt(r.esperado)}** · LLM: **{_veredicto_txt(r.llm)}** · "
              f"resultado: **{r.resultado}**"]
        if r.nota:
            L.append(f"- Nota: {r.nota}")
        if r.error:
            L.append(f"- Error: `{r.error}`")
        L += ["", "Respuesta del LLM:", "", "````text", r.texto.strip() or "(vacía)", "````", ""]
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    return ruta


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m tlp.espanol.llm_experimento",
                                 description="Pide a un LLM analizar el conjunto de prueba con las reglas de la gramática.")
    ap.add_argument("--limite", type=int, default=0, help="analizar solo las N primeras oraciones (prueba barata)")
    a = ap.parse_args(argv)
    try:
        proveedor, clave, modelo = elegir_proveedor(leer_env())
        sistema, plantilla = leer_prompt()
        llamar = crear_cliente(proveedor, clave, modelo)
        casos = cargar_conjunto()[: a.limite] if a.limite else cargar_conjunto()
        print(f"Proveedor: {proveedor} · modelo: {modelo} · ejemplos en el prompt: {contar_ejemplos(plantilla)} · "
              f"oraciones: {len(casos)}")
        respuestas = ejecutar(casos, llamar, sistema, plantilla)
    except ErrorConfiguracion as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    except ImportError as e:
        print(f"ERROR: falta el SDK del proveedor ({e}). Instálalo con: pip install -r requirements-fase2.txt",
              file=sys.stderr)
        return 2
    os.makedirs(DESTINO, exist_ok=True)
    nombre = f"respuestas_{proveedor}_{re.sub(r'[^A-Za-z0-9.-]+', '-', modelo)}_{datetime.now():%Y%m%d-%H%M%S}.md"
    ruta = escribir_md(respuestas, proveedor, modelo, sistema, plantilla, os.path.join(DESTINO, nombre))
    cuenta = Counter(r.resultado for r in respuestas)
    print(f"\nCoincide con la gramática: {cuenta['coincide']}/{len(respuestas)} · "
          f"desviación hacia el español: {cuenta['desviación hacia el español']} · "
          f"aceptó agramatical: {cuenta['aceptó una agramatical']} · sobre-rechazo: {cuenta['sobre-rechazo']} · "
          f"sin respuesta válida: {cuenta['sin respuesta válida']}")
    print("Respuestas en:", ruta)
    return 0


if __name__ == "__main__":
    sys.exit(main())
