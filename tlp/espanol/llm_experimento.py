"""tlp/espanol/llm_experimento.py - Fase 2 (punto 6): ¿sigue un LLM las reglas de la gramática formal?

Le da a un LLM (Claude, ChatGPT o Gemini) las reglas de producción y el léxico de la gramática y le pide analizar las
oraciones del conjunto de prueba. Hay cuatro variantes de prompt, cada una en casos/espanol/prompts/<variante>.txt:
  sin_ejemplos   reglas + léxico + formato de respuesta                    (sin instrucciones de sistema, sin ejemplos)
  zero_shot      lo anterior + instrucciones de sistema («aplica ÚNICAMENTE estas reglas»)          (sin ejemplos)
  few_shot       lo anterior sin instrucciones de sistema + 6 ejemplos resueltos
  combinado      instrucciones de sistema + 6 ejemplos resueltos

Configuración: archivo .env en la raíz del proyecto (plantilla: .env.ejemplo)
  ANTHROPIC_API_KEY (Claude) | OPENAI_API_KEY (ChatGPT) | GEMINI_API_KEY (Gemini)   llena SOLO la que vas a usar
  LLM_MODELO                                                                      nombre del modelo de ese proveedor

Uso:  python -m tlp.espanol.llm_experimento --variante zero_shot              # una variante, todas las oraciones
      python -m tlp.espanol.llm_experimento --variante todas                  # las cuatro variantes
      python -m tlp.espanol.llm_experimento --variante few_shot --limite 5    # solo las 5 primeras (prueba barata)
Salidas de cada variante (una corrida nueva reemplaza la anterior de esa variante):
  resultados/fase2/logs/llm_<variante>.jsonl      log bruto: una línea JSON por llamada al LLM, con su timestamp,
                                                  el modelo, los parámetros, el prompt enviado y la respuesta cruda
  resultados/fase2/llm/respuestas_<variante>.md   lo mismo en forma legible, con un resumen
Las métricas de todos los enfoques, contra las dos referencias, las calcula:  python -m tlp.espanol.evaluar

Resumen del .md (referencia = lo que acepta la gramática, es decir, el veredicto del parser propio):
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
from importlib import metadata

from .conjunto import RAIZ, Caso, cargar_conjunto
from .gramatica_es import REGLAS_BNF, ParserEspanol, lexico_para_prompt

RUTA_ENV = os.path.join(RAIZ, ".env")
DIR_PROMPTS = os.path.join(RAIZ, "casos", "espanol", "prompts")
VARIANTES = ("sin_ejemplos", "zero_shot", "few_shot", "combinado")
DIR_LOGS = os.path.join(RAIZ, "resultados", "fase2", "logs")
DESTINO = os.path.join(RAIZ, "resultados", "fase2", "llm")
PROVEEDORES = {"ANTHROPIC_API_KEY": "claude", "OPENAI_API_KEY": "chatgpt", "GEMINI_API_KEY": "gemini"}
SDK = {"claude": "anthropic", "chatgpt": "openai", "gemini": "google-genai"}
MAX_TOKENS = 4096                 # holgado: en los modelos de razonamiento, lo que "piensan" también cuenta
ESPERAS_LIMITE = (10, 20, 40)     # segundos de espera si el proveedor responde "límite de peticiones" o "saturado"
LIMITE_PETICIONES = ("429", "rate limit", "rate_limit", "too many requests", "quota", "resource_exhausted")
SERVIDOR_SATURADO = ("503", "unavailable", "overloaded", "high demand")
ERRORES_TEMPORALES = LIMITE_PETICIONES + SERVIDOR_SATURADO


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


def ruta_prompt(variante: str) -> str:
    return os.path.join(DIR_PROMPTS, f"{variante}.txt")


def leer_prompt(ruta: str) -> tuple[str, str]:
    """(instrucciones de sistema, plantilla del mensaje). Quita los comentarios '#' y separa las dos secciones.
    La sección SISTEMA puede quedar vacía: entonces no se envía mensaje de sistema."""
    if not os.path.exists(ruta):
        raise ErrorConfiguracion(f"No existe el archivo de prompt {ruta}.")
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


def version_sdk(proveedor: str) -> str:
    paquete = SDK[proveedor]
    try:
        return f"{paquete} {metadata.version(paquete)}"
    except metadata.PackageNotFoundError:
        return f"{paquete} (no instalado)"


# ------------------------------------------------------------------ llamada al LLM
@dataclass
class Llamada:
    """Lo que devuelve una llamada al LLM."""
    texto: str                          # respuesta cruda
    temperature: float | None           # temperatura usada; None = la del modelo por defecto
    modelo_respuesta: str | None        # modelo que reporta la API en su respuesta
    nota: str = ""


def es_temporal(texto_error: str) -> bool:
    """True si el error es pasajero (límite de peticiones o servidor saturado): conviene esperar y reintentar."""
    texto_error = texto_error.lower()
    return any(s in texto_error for s in ERRORES_TEMPORALES)


def crear_cliente(proveedor: str, clave: str, modelo: str):
    """Devuelve llamar(sistema, mensaje) -> Llamada para el proveedor elegido.
    Si `sistema` está vacío no se envía mensaje de sistema."""
    if proveedor == "claude":
        import anthropic
        cliente = anthropic.Anthropic(api_key=clave)

        def pedir(sistema, mensaje, **extra):
            kw = {"system": sistema} if sistema else {}
            r = cliente.messages.create(model=modelo, max_tokens=MAX_TOKENS,
                                        messages=[{"role": "user", "content": mensaje}], **kw, **extra)
            return "".join(b.text for b in r.content if getattr(b, "type", "") == "text"), getattr(r, "model", None)
    elif proveedor == "chatgpt":
        import openai
        cliente = openai.OpenAI(api_key=clave)

        def pedir(sistema, mensaje, **extra):
            mensajes = ([{"role": "system", "content": sistema}] if sistema else []) + \
                       [{"role": "user", "content": mensaje}]
            r = cliente.chat.completions.create(model=modelo, max_completion_tokens=MAX_TOKENS, messages=mensajes,
                                                **extra)
            return r.choices[0].message.content or "", getattr(r, "model", None)
    else:
        from google import genai
        from google.genai import types
        cliente = genai.Client(api_key=clave)

        def pedir(sistema, mensaje, **extra):
            config = types.GenerateContentConfig(system_instruction=sistema or None, max_output_tokens=MAX_TOKENS,
                                                 **extra)
            r = cliente.models.generate_content(model=modelo, contents=mensaje, config=config)
            return r.text or "", getattr(r, "model_version", None)

    estado = {"extra": {"temperature": 0}, "nota": ""}      # si el modelo no acepta temperature=0, se recuerda

    def llamar(sistema: str, mensaje: str) -> Llamada:
        for espera in (*ESPERAS_LIMITE, None):
            try:
                texto, modelo_respuesta = pedir(sistema, mensaje, **estado["extra"])
                return Llamada(texto, estado["extra"].get("temperature"), modelo_respuesta, estado["nota"])
            except Exception as e:                                       # noqa: BLE001 (cada SDK tiene sus clases)
                texto = str(e).lower()
                if "temperature" in texto and estado["extra"]:           # modelos que no aceptan temperature=0
                    estado["extra"], estado["nota"] = {}, ("el modelo no acepta temperature=0; "
                                                           "se usó su temperatura por defecto")
                    continue
                if espera is not None and es_temporal(texto):
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


def veredicto(j: dict | None) -> bool | None:
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
    timestamp: str = ""            # momento de la llamada (ISO 8601, hora local con zona horaria)
    duracion_ms: float = 0.0
    temperature: float | None = None
    modelo_respuesta: str | None = None

    @property
    def llm(self) -> bool | None:
        return veredicto(extraer_json(self.texto))

    @property
    def resultado(self) -> str:
        if self.llm is None:
            return "sin respuesta válida"
        if self.llm == self.esperado:
            return "coincide"
        if self.llm:
            return "desviación hacia el español" if self.caso.gramatical_es else "aceptó una agramatical"
        return "sobre-rechazo"


def _ahora() -> str:
    return datetime.now().astimezone().isoformat(timespec="milliseconds")


def ejecutar(casos: list[Caso], llamar, sistema: str, plantilla: str, progreso=print,
             ruta_log: str | None = None, meta: dict | None = None) -> list[Respuesta]:
    """Hace una llamada al LLM por oración. Si se da `ruta_log`, escribe en él una línea JSON por llamada
    (en cuanto termina cada una, para no perder nada si la corrida se interrumpe)."""
    parser, respuestas, meta = ParserEspanol(), [], meta or {}
    log = None
    if ruta_log:
        os.makedirs(os.path.dirname(ruta_log), exist_ok=True)
        log = open(ruta_log, "w", encoding="utf-8")
    try:
        for i, c in enumerate(casos, 1):
            esperado = parser.parse(c.oracion)[0] is not None
            mensaje = completar(plantilla, c.oracion)
            llamada, error = Llamada("", None, None), ""
            timestamp, t0 = _ahora(), time.perf_counter()
            try:
                llamada = llamar(sistema, mensaje)
            except Exception as e:                                       # noqa: BLE001
                error = f"{type(e).__name__}: {e}"
                if i == 1 and es_temporal(error):                        # proveedor saturado: no es la configuración
                    raise ErrorConfiguracion(f"La primera llamada al LLM falló ({error}). El proveedor está saturado "
                                             "o llegó al límite de peticiones, aun después de reintentar; "
                                             "vuelve a intentarlo en unos minutos.") from e
                if i == 1:                                               # clave o modelo mal escritos: no seguir
                    raise ErrorConfiguracion(f"La primera llamada al LLM falló ({error}). "
                                             "Revisa la clave y LLM_MODELO en .env.") from e
            duracion = round(1000 * (time.perf_counter() - t0), 1)
            r = Respuesta(c, esperado, llamada.texto, llamada.nota, error, timestamp, duracion,
                          llamada.temperature, llamada.modelo_respuesta)
            respuestas.append(r)
            if log:
                registro = {"variante": meta.get("variante", ""), "id": c.id, "nivel": c.nivel, "oracion": c.oracion,
                            "timestamp": timestamp, "duracion_ms": duracion,
                            "proveedor": meta.get("proveedor", ""), "modelo": meta.get("modelo", ""),
                            "modelo_respuesta": llamada.modelo_respuesta, "sdk": meta.get("sdk", ""),
                            "parametros": {"temperature": llamada.temperature if not error else None,
                                           "max_tokens": MAX_TOKENS},
                            "prompt_archivo": meta.get("prompt_archivo", ""),
                            "prompt_sistema": sistema, "prompt_usuario": mensaje,
                            "respuesta": llamada.texto, "nota": llamada.nota, "error": error}
                log.write(json.dumps(registro, ensure_ascii=False) + "\n")
                log.flush()
            progreso(f"[{i}/{len(casos)}] {c.oracion} -> {r.resultado}")
    finally:
        if log:
            log.close()
    return respuestas


def _veredicto_txt(v: bool | None) -> str:
    return "—" if v is None else ("ACEPTA" if v else "RECHAZA")


def _temperaturas(respuestas: list[Respuesta]) -> str:
    usadas = {r.temperature for r in respuestas if not r.error}
    if not usadas:
        return "—"
    return " / ".join("la del modelo por defecto (no acepta 0)" if t is None else str(t)
                      for t in sorted(usadas, key=lambda t: (t is None, t or 0)))


def escribir_md(respuestas: list[Respuesta], meta: dict, sistema: str, plantilla: str, ruta: str) -> str:
    n, cuenta = len(respuestas), Counter(r.resultado for r in respuestas)
    reportados = sorted({r.modelo_respuesta for r in respuestas if r.modelo_respuesta})
    marcas = [r.timestamp for r in respuestas if r.timestamp]
    L = [f"# Respuestas del LLM — variante {meta.get('variante', '')}", "",
         f"- Proveedor: {meta.get('proveedor', '')} · modelo: {meta.get('modelo', '')}"
         + (f" (la API reporta: {', '.join(reportados)})" if reportados else ""),
         f"- SDK: {meta.get('sdk', '')}",
         f"- Parámetros: temperature = {_temperaturas(respuestas)} · max_tokens = {MAX_TOKENS}",
         f"- Prompt: `{meta.get('prompt_archivo', '')}` · instrucciones de sistema: {'sí' if sistema else 'no'} · "
         f"ejemplos resueltos: {contar_ejemplos(plantilla)}",
         f"- Primera llamada: {marcas[0] if marcas else '—'} · última llamada: {marcas[-1] if marcas else '—'}",
         f"- Oraciones analizadas: {n}",
         f"- Log bruto (una línea JSON por llamada): `{meta.get('log', '')}`", "",
         "## Resumen", "",
         "Referencia: lo que acepta la gramática (veredicto del parser propio).", "",
         "| Resultado | Oraciones |", "|---|---|",
         f"| Coincide con la gramática | {cuenta['coincide']}/{n} |",
         f"| Desviación hacia el español (acepta lo que la gramática rechaza, pero es español correcto) | "
         f"{cuenta['desviación hacia el español']} |",
         f"| Aceptó una oración agramatical | {cuenta['aceptó una agramatical']} |",
         f"| Sobre-rechazo (rechaza lo que la gramática deriva) | {cuenta['sobre-rechazo']} |",
         f"| Sin respuesta válida | {cuenta['sin respuesta válida']} |", "",
         "## Prompt usado", "", "### Sistema", "", "````text", sistema or "(sin mensaje de sistema)", "````", "",
         "### Usuario (la marca {oracion} se reemplaza por cada oración)", "",
         "````text", plantilla.replace("{gramatica}", REGLAS_BNF).replace("{lexico}", lexico_para_prompt()), "````",
         "", "## Respuestas", ""]
    for r in respuestas:
        c = r.caso
        L += [f"### [{c.id:02d}] {c.oracion}", "",
              f"- Nivel {c.nivel} · español correcto: {'sí' if c.gramatical_es else 'no'} · fenómeno: {c.fenomeno}",
              f"- Llamada: {r.timestamp} · {r.duracion_ms:.0f} ms",
              f"- Esperado (gramática): **{_veredicto_txt(r.esperado)}** · LLM: **{_veredicto_txt(r.llm)}** · "
              f"resultado: **{r.resultado}**"]
        if r.nota:
            L.append(f"- Nota: {r.nota}")
        if r.error:
            L.append(f"- Error: `{r.error}`")
        L += ["", "Respuesta del LLM:", "", "````text", r.texto.strip() or "(vacía)", "````", ""]
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    return ruta


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m tlp.espanol.llm_experimento",
                                 description="Pide a un LLM analizar el conjunto de prueba con las reglas de la gramática.")
    ap.add_argument("--variante", required=True, choices=[*VARIANTES, "todas"],
                    help="prompt a usar (casos/espanol/prompts/<variante>.txt); 'todas' corre las cuatro")
    ap.add_argument("--limite", type=int, default=0, help="analizar solo las N primeras oraciones (prueba barata)")
    a = ap.parse_args(argv)
    variantes = VARIANTES if a.variante == "todas" else (a.variante,)
    try:
        proveedor, clave, modelo = elegir_proveedor(leer_env())
        prompts = {v: leer_prompt(ruta_prompt(v)) for v in variantes}       # se validan todos antes de llamar
        llamar = crear_cliente(proveedor, clave, modelo)
        casos = cargar_conjunto()[: a.limite] if a.limite else cargar_conjunto()
        for v in variantes:
            sistema, plantilla = prompts[v]
            ruta_log = os.path.join(DIR_LOGS, f"llm_{v}.jsonl")
            meta = {"variante": v, "proveedor": proveedor, "modelo": modelo, "sdk": version_sdk(proveedor),
                    "prompt_archivo": os.path.relpath(ruta_prompt(v), RAIZ),
                    "log": os.path.relpath(ruta_log, RAIZ)}
            print(f"\nVariante: {v} · proveedor: {proveedor} · modelo: {modelo} · instrucciones de sistema: "
                  f"{'sí' if sistema else 'no'} · ejemplos: {contar_ejemplos(plantilla)} · oraciones: {len(casos)}")
            respuestas = ejecutar(casos, llamar, sistema, plantilla, ruta_log=ruta_log, meta=meta)
            ruta_md = escribir_md(respuestas, meta, sistema, plantilla, os.path.join(DESTINO, f"respuestas_{v}.md"))
            cuenta = Counter(r.resultado for r in respuestas)
            print(f"Coincide con la gramática: {cuenta['coincide']}/{len(respuestas)} · "
                  f"desviación hacia el español: {cuenta['desviación hacia el español']} · "
                  f"aceptó agramatical: {cuenta['aceptó una agramatical']} · sobre-rechazo: {cuenta['sobre-rechazo']} · "
                  f"sin respuesta válida: {cuenta['sin respuesta válida']}")
            print("Log bruto:", ruta_log, "\nRespuestas:", ruta_md)
    except ErrorConfiguracion as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    except ImportError as e:
        print(f"ERROR: falta el SDK del proveedor ({e}). Instálalo con: pip install -r requirements-fase2.txt",
              file=sys.stderr)
        return 2
    print("\nPara calcular las métricas de todos los enfoques:  python -m tlp.espanol.evaluar")
    return 0


if __name__ == "__main__":
    sys.exit(main())
