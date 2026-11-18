"""tlp/espanol/evaluar.py - Fase 2 (punto 5): script de evaluación. Lee SOLO los logs y calcula las métricas.

Entradas:
  casos/espanol/conjunto_prueba.csv   corpus con la salida esperada de cada oración
  resultados/fase2/logs/*.jsonl       salida bruta de cada enfoque sobre el corpus
                                      (la escriben comparacion_nlp.py y llm_experimento.py; aquí no se corre nada)
Salidas en resultados/fase2/:
  tablas.md               enfoques (versiones y parámetros) y tablas comparativas
  metricas_globales.csv   las métricas de cada sistema contra cada referencia, con sus intervalos de confianza
  errores_detalle.csv     cada falso positivo, falso negativo, respuesta inválida y error de etiquetado
  grafica_metricas.png    precisión, cobertura y rechazo correcto por sistema (un panel por referencia)
  grafica_errores.png     falsos positivos, falsos negativos y errores de etiquetado (un panel por referencia)
Reproducible: no usa la fecha ni mide tiempos (los ms/oración salen de los logs); con los mismos logs produce
exactamente los mismos archivos.

Uso:  python -m tlp.espanol.evaluar
      python -m tlp.espanol.evaluar --logs <carpeta> --salida <carpeta>

Dos referencias (columnas del corpus):
  español    gramatical_es        ¿es español correcto?   -> qué tan lejos llega cada enfoque frente al español real
  gramática  esperado_gramatica   ¿la deriva la gramática? -> si el enfoque respeta las reglas formales
Positivo = la referencia dice SÍ y el sistema acepta:
  TP referencia SÍ y aceptada    FP referencia NO y aceptada    FN referencia SÍ y rechazada    TN referencia NO y rechazada
  Precisión = TP/(TP+FP)    Cobertura (recall) = TP/(TP+FN)    Rechazo correcto = TN/(TN+FP)    F1 = 2PC/(P+C)
  Cada proporción lleva su intervalo de confianza del 95 % (método de Wilson).
  LLM: una respuesta sin un JSON con "acepta" cuenta como «sin respuesta»: no entra en TP/FP/FN/TN y se reporta aparte.
Errores de etiquetado (oraciones que son español correcto y que el sistema acepta; no dependen de la referencia):
  S-V-O        la tripleta (sujeto, verbo, objeto) no es la esperada        [parser propio, spaCy, LLM (de su árbol)]
  categorías   alguna palabra recibe una categoría UPOS distinta de la del léxico            [spaCy, HuggingFace]
               (solo oraciones con todas sus palabras en el léxico; «al» y «del» valen ADP o DET)
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import sys
from dataclasses import dataclass, field

from ..arbol import Node
from .conjunto import RAIZ, Caso, cargar_conjunto
from .gramatica_es import LEMA_DE_FORMA, LEXICO
from .llm_experimento import VARIANTES, extraer_json, veredicto

DIR_LOGS = os.path.join(RAIZ, "resultados", "fase2", "logs")
DESTINO = os.path.join(RAIZ, "resultados", "fase2")
REFERENCIAS = {"español": "español correcto (`gramatical_es`)", "gramática": "gramática (`esperado_gramatica`)"}
NOMBRE_VARIANTE = {"sin_ejemplos": "sin ejemplos", "zero_shot": "zero-shot", "few_shot": "few-shot",
                   "combinado": "combinado"}
TAMANOS_SPACY = ("sm", "md", "lg", "trf")

CAT2UPOS = {"DET": {"DET"}, "N": {"NOUN"}, "PN": {"PROPN"}, "ADJ": {"ADJ"}, "V": {"VERB", "AUX"},
            "ADV": {"ADV"}, "P": {"ADP"}, "QUE": {"PRON", "SCONJ"}}
CONTRACCIONES = {"al": {"ADP", "DET"}, "del": {"ADP", "DET"}}


# ------------------------------------------------------------------ S-V-O del árbol que devuelve el LLM
def leer_arbol(texto: str | None) -> Node | None:
    """Árbol en notación de paréntesis -> Node; None si el texto no es un árbol bien formado."""
    fichas = re.findall(r"\(|\)|[^\s()]+", texto or "")
    pos = 0

    def nodo() -> Node:
        nonlocal pos
        if fichas[pos] != "(":
            pos += 1
            return Node(fichas[pos - 1])
        pos += 1
        etiqueta, pos = fichas[pos], pos + 1
        if etiqueta in ("(", ")"):
            raise ValueError("falta la etiqueta")
        hijos = []
        while fichas[pos] != ")":
            hijos.append(nodo())
        pos += 1
        return Node(etiqueta, hijos)

    try:
        arbol = nodo()
    except (IndexError, ValueError):
        return None
    return arbol if pos == len(fichas) and not arbol.es_hoja else None


def _cat(n: Node) -> str:
    return n.label.split("[", 1)[0]


def _lema(n: Node) -> str:
    while n.children:
        n = n.children[0]
    return LEMA_DE_FORMA.get(n.label.lower(), n.label.lower())


def _nucleo(sn: Node) -> str:
    return next((_lema(h) for h in sn.children if _cat(h) in ("N", "PN")), "?")


def svo_de_arbol(texto: str | None) -> tuple[str, str, str] | None:
    """(sujeto, verbo, objeto) de un árbol en notación de paréntesis, con los mismos criterios que extraer_svo del
    parser: objeto = '-' si no hay, '*' si es una cláusula completiva (V Que O). Admite el objeto directo como
    SN o envuelto en Obj (Obj → SN | A SN). None si el árbol no se puede leer o no tiene SN y SV."""
    arbol = leer_arbol(texto)
    if arbol is None:
        return None
    sn = next((h for h in arbol.children if _cat(h) == "SN"), None)
    sv = next((h for h in arbol.children if _cat(h) == "SV"), None)
    verbo = next((h for h in sv.children if _cat(h) == "V"), None) if sv else None
    if sn is None or verbo is None:
        return None
    if any(_cat(h) == "O" for h in sv.children):
        objeto = "*"
    else:
        objs = [x for h in sv.children
                for x in ([h] if _cat(h) == "SN" else [y for y in h.children if _cat(y) == "SN"] if _cat(h) == "Obj"
                          else [])]
        objeto = _nucleo(objs[0]) if objs else "-"
    return _nucleo(sn), _lema(verbo), objeto


# ------------------------------------------------------------------ lectura de los logs
@dataclass
class Salida:
    """Lo que respondió un sistema para una oración, según su log."""
    acepta: bool | None                                 # None = sin respuesta válida (solo LLM)
    motivo: str = ""
    svo: tuple[str, str, str] | None = None
    palabras: list[str] | None = None
    etiquetas: list[str] | None = None                  # categoría UPOS de cada palabra
    ms: float = 0.0


@dataclass
class Sistema:
    nombre: str
    archivo: str
    descripcion: str                                    # versiones y parámetros, leídos del log
    salidas: dict[int, Salida]                          # id de la oración -> salida
    da_svo: bool
    da_categorias: bool
    da_sin_respuesta: bool = False


def _leer_jsonl(ruta: str) -> list[dict]:
    with open(ruta, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def _orden(nombre: str) -> tuple:
    base = nombre[: -len(".jsonl")]
    if base == "parser":
        return (0,)
    if base.startswith("spacy_"):
        partes = base.split("_")
        tam = TAMANOS_SPACY.index(partes[1]) if partes[1] in TAMANOS_SPACY else len(TAMANOS_SPACY)
        return (1, tam, partes[1], 0 if partes[-1] == "crudo" else 1)
    if base == "huggingface":
        return (2,)
    if base.startswith("llm_") and base[4:] in VARIANTES:
        return (3, VARIANTES.index(base[4:]))
    return (4, base)


def _unicos(valores) -> str:
    vistos = []
    for v in valores:
        if v not in vistos:
            vistos.append(v)
    return ", ".join("—" if v is None else str(v) for v in vistos)


def sistema_llm(archivo: str, registros: list[dict]) -> Sistema:
    variante = registros[0].get("variante", archivo[4:-6])
    salidas = {}
    for r in registros:
        j = extraer_json(r.get("respuesta", ""))
        acepta = veredicto(j)
        motivo = r.get("error") or str((j or {}).get("regla_que_falla") or (j or {}).get("razon") or "")
        if acepta is None and not r.get("error"):
            motivo = "la respuesta no trae un JSON con \"acepta\""
        salidas[r["id"]] = Salida(acepta, motivo, svo_de_arbol((j or {}).get("arbol")) if acepta else None,
                                  ms=float(r.get("duracion_ms", 0.0)))
    marcas = [r["timestamp"] for r in registros if r.get("timestamp")]
    temperaturas = [r.get("parametros", {}).get("temperature") for r in registros if not r.get("error")]
    descripcion = (f"{_unicos(r.get('proveedor') for r in registros)} · modelo {_unicos(r.get('modelo') for r in registros)}"
                   f" (la API reporta: {_unicos(r.get('modelo_respuesta') for r in registros)}) · "
                   f"SDK {_unicos(r.get('sdk') for r in registros)} · temperature = "
                   f"{_unicos('por defecto' if t is None else t for t in temperaturas)} · max_tokens = "
                   f"{_unicos(r.get('parametros', {}).get('max_tokens') for r in registros)} · prompt "
                   f"`{_unicos(r.get('prompt_archivo') for r in registros)}` · {len(registros)} llamadas"
                   + (f" entre {marcas[0]} y {marcas[-1]}" if marcas else ""))
    return Sistema(f"LLM {NOMBRE_VARIANTE.get(variante, variante)}", archivo, descripcion, salidas,
                   da_svo=True, da_categorias=False, da_sin_respuesta=True)


def sistema_nlp(archivo: str, registros: list[dict]) -> Sistema:
    salidas = {r["id"]: Salida(bool(r["acepta"]), r.get("motivo", ""), tuple(r["svo"]) if r.get("svo") else None,
                               r.get("palabras"), r.get("etiquetas"), float(r.get("ms", 0.0)))
               for r in registros}
    tipo = archivo.split("_")[0].split(".")[0]
    return Sistema(registros[0]["sistema"], archivo, _unicos(r.get("version") for r in registros), salidas,
                   da_svo=tipo in ("parser", "spacy"), da_categorias=tipo in ("spacy", "huggingface"))


def cargar_sistemas(dir_logs: str = DIR_LOGS) -> list[Sistema]:
    if not os.path.isdir(dir_logs):
        return []
    sistemas = []
    for archivo in sorted((a for a in os.listdir(dir_logs) if a.endswith(".jsonl")), key=_orden):
        registros = _leer_jsonl(os.path.join(dir_logs, archivo))
        if registros:
            sistemas.append((sistema_llm if archivo.startswith("llm_") else sistema_nlp)(archivo, registros))
    return sistemas


# ------------------------------------------------------------------ métricas
def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Intervalo de confianza de Wilson para la proporción k/n (95 % con z = 1.96)."""
    if n == 0:
        return math.nan, math.nan
    p, d = k / n, 1 + z * z / n
    centro = (p + z * z / (2 * n)) / d
    margen = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, centro - margen), min(1.0, centro + margen)


def _proporcion(k: int, n: int) -> tuple[float, float, float]:
    """(k/n, extremo inferior, extremo superior)."""
    return (k / n if n else math.nan, *wilson(k, n))


def positivo(caso: Caso, referencia: str) -> bool:
    return caso.gramatical_es if referencia == "español" else caso.esperado == "ACEPTA"


def _error(caso: Caso, tipo: str, detalle: str, referencia: str = "—") -> dict:
    return dict(caso=caso, tipo=tipo, detalle=detalle, referencia=referencia)


def metricas(casos: list[Caso], sistema: Sistema, referencia: str) -> tuple[dict, list[dict]]:
    """(métricas, errores) de aceptación y rechazo de un sistema frente a una referencia."""
    m = dict(n=0, TP=0, FP=0, FN=0, TN=0, sin_respuesta=0, desviacion_es=0, acepta_agramatical=0)
    errores = []
    for c in casos:
        s = sistema.salidas.get(c.id)
        if s is None:
            continue
        m["n"] += 1
        if s.acepta is None:
            m["sin_respuesta"] += 1
            if referencia == "español":                       # se reporta una sola vez
                errores.append(_error(c, "sin respuesta válida", s.motivo))
            continue
        clave = ("TP" if s.acepta else "FN") if positivo(c, referencia) else ("FP" if s.acepta else "TN")
        m[clave] += 1
        if clave == "FP" and referencia == "gramática":
            m["desviacion_es" if c.gramatical_es else "acepta_agramatical"] += 1
        if clave in ("FP", "FN"):
            errores.append(_error(c, "falso positivo" if clave == "FP" else "falso negativo",
                                  s.motivo or c.fenomeno, referencia))
    tp, fp, fn, tn = m["TP"], m["FP"], m["FN"], m["TN"]
    m["precision"], m["cobertura"] = _proporcion(tp, tp + fp), _proporcion(tp, tp + fn)
    m["rechazo_correcto"] = _proporcion(tn, tn + fp)
    p, r = m["precision"][0], m["cobertura"][0]
    m["f1"] = 2 * p * r / (p + r) if p + r else math.nan
    return m, errores


def _categorias_esperadas(palabras: list[str]) -> list[set[str]] | None:
    """Categorías UPOS válidas de cada palabra según el léxico; None si alguna palabra no está en el léxico."""
    oro = []
    for w in (p.lower() for p in palabras):
        if w in CONTRACCIONES:
            oro.append(CONTRACCIONES[w])
        elif w in LEXICO:
            oro.append(set().union(*(CAT2UPOS[e.cat] for e in LEXICO[w])))
        else:
            return None
    return oro


def _svo_correcta(pred, oro) -> bool:
    return pred is not None and all(g == "*" or g == p for g, p in zip(oro, pred))


def etiquetado(casos: list[Caso], sistema: Sistema) -> tuple[dict, list[dict]]:
    """Errores de etiquetado (S-V-O y categorías) en las oraciones que son español correcto y el sistema acepta."""
    m = dict(err_svo=0, err_cat=0)
    errores = []
    svo_total = svo_bien = cat_bien = cat_total = cat_oraciones = 0
    ms = [s.ms for s in sistema.salidas.values()]
    for c in casos:
        s = sistema.salidas.get(c.id)
        if s is None or s.acepta is None or not c.gramatical_es:
            continue
        if sistema.da_svo and c.svo and any(x != "*" for x in c.svo):
            svo_total += 1
            bien = s.acepta and _svo_correcta(s.svo, c.svo)
            svo_bien += bien
            if s.acepta and not bien:
                m["err_svo"] += 1
                obtenido = tuple(s.svo) if s.svo else "sin S-V-O (árbol ilegible o incompleto)"
                errores.append(_error(c, "error de etiquetado (S-V-O)", f"esperado {c.svo}, obtenido {obtenido}"))
        if sistema.da_categorias and s.palabras and s.etiquetas:
            oro = _categorias_esperadas(s.palabras)
            if oro is None or len(oro) != len(s.etiquetas):
                continue
            malas = [f"{p}={e}" for p, e, o in zip(s.palabras, s.etiquetas, oro) if e not in o]
            cat_bien, cat_total, cat_oraciones = cat_bien + len(oro) - len(malas), cat_total + len(oro), cat_oraciones + 1
            if s.acepta and malas:
                m["err_cat"] += 1
                errores.append(_error(c, "error de etiquetado (categorías)", f"mal etiquetadas: {', '.join(malas)}"))
    m["exactitud_svo"] = svo_bien / svo_total if sistema.da_svo and svo_total else math.nan
    m["exactitud_categorias"] = cat_bien / cat_total if cat_total else math.nan
    m["oraciones_categorias"] = cat_oraciones
    m["ms_por_oracion"] = sum(ms) / len(ms) if ms else math.nan
    return m, errores


@dataclass
class Resultado:
    sistema: Sistema
    por_referencia: dict[str, dict] = field(default_factory=dict)
    etiquetado: dict = field(default_factory=dict)
    errores: list[dict] = field(default_factory=list)


def evaluar(casos: list[Caso], sistemas: list[Sistema]) -> list[Resultado]:
    resultados = []
    for s in sistemas:
        r = Resultado(s)
        for ref in REFERENCIAS:
            r.por_referencia[ref], errores = metricas(casos, s, ref)
            r.errores += errores
        r.etiquetado, errores = etiquetado(casos, s)
        r.errores += errores
        resultados.append(r)
    return resultados


# ------------------------------------------------------------------ salidas: CSV y Markdown
def _r(v: float):
    return "" if v != v else round(v, 4)


def _pct(v: float) -> str:
    return "—" if v != v else f"{100 * v:.1f}%"


def _pct_ic(t: tuple[float, float, float]) -> str:
    v, lo, hi = t
    return "—" if v != v else f"{100 * v:.1f}% [{100 * lo:.1f}–{100 * hi:.1f}]"


def escribir_metricas_csv(resultados: list[Resultado], ruta: str) -> str:
    campos = ["referencia", "sistema", "oraciones", "TP", "FP", "FN", "TN", "sin_respuesta",
              "precision", "precision_ic95_inf", "precision_ic95_sup",
              "cobertura", "cobertura_ic95_inf", "cobertura_ic95_sup", "f1",
              "rechazo_correcto", "rechazo_correcto_ic95_inf", "rechazo_correcto_ic95_sup",
              "errores_etiquetado_svo", "errores_etiquetado_categorias", "exactitud_svo", "exactitud_categorias",
              "oraciones_categorias", "ms_por_oracion"]
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(campos)
        for ref in REFERENCIAS:
            for r in resultados:
                s, m, e = r.sistema, r.por_referencia[ref], r.etiquetado
                fila = [ref, s.nombre, m["n"], m["TP"], m["FP"], m["FN"], m["TN"],
                        m["sin_respuesta"] if s.da_sin_respuesta else ""]
                fila += [_r(x) for x in m["precision"]] + [_r(x) for x in m["cobertura"]] + [_r(m["f1"])]
                fila += [_r(x) for x in m["rechazo_correcto"]]
                fila += [e["err_svo"] if s.da_svo else "", e["err_cat"] if s.da_categorias else "",
                         _r(e["exactitud_svo"]), _r(e["exactitud_categorias"]),
                         e["oraciones_categorias"] if s.da_categorias else "", _r(e["ms_por_oracion"])]
                w.writerow(fila)
    return ruta


def escribir_errores_csv(resultados: list[Resultado], ruta: str) -> str:
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["sistema", "referencia", "id", "nivel", "oracion", "tipo", "detalle"])
        for r in resultados:
            for e in r.errores:
                c = e["caso"]
                w.writerow([r.sistema.nombre, e["referencia"], c.id, c.nivel, c.oracion, e["tipo"], e["detalle"]])
    return ruta


def tablas_md(casos: list[Caso], resultados: list[Resultado], dir_logs: str) -> str:
    n_es = sum(c.gramatical_es for c in casos)
    n_gr = sum(c.esperado == "ACEPTA" for c in casos)
    carpeta = os.path.relpath(dir_logs, RAIZ) if os.path.abspath(dir_logs).startswith(RAIZ) else dir_logs
    L = ["# Fase 2 — Comparación de los enfoques sobre el corpus de prueba", "",
         f"Generado por `python -m tlp.espanol.evaluar` a partir de los logs de `{carpeta}/` (no vuelve a correr "
         f"ningún sistema). Corpus: {len(casos)} oraciones; {n_es} son español correcto (`gramatical_es`) y "
         f"{n_gr} las deriva la gramática (`esperado_gramatica`). Entre corchetes, intervalo de confianza del 95 % "
         "(Wilson). «—» = el sistema no produce ese dato.", "",
         "## Enfoques, versiones y parámetros", "",
         "| Sistema | Log | Versión y parámetros |", "|---|---|---|"]
    for r in resultados:
        L.append(f"| {r.sistema.nombre} | `{r.sistema.archivo}` | {r.sistema.descripcion} |")
    incompletos = [r.sistema.nombre for r in resultados if r.por_referencia["español"]["n"] < len(casos)]
    if incompletos:
        L += ["", f"> **Aviso:** estos logs no cubren las {len(casos)} oraciones del corpus: "
                  f"{', '.join(incompletos)}. Sus métricas se calculan solo sobre las oraciones que sí tienen."]
    explicacion = {
        "español": "Positivo = la oración es español correcto. Mide qué tan lejos llega cada enfoque frente al "
                   "español real.",
        "gramática": "Positivo = la gramática deriva la oración. Mide si el enfoque respeta las reglas formales "
                     "(el parser propio coincide con esta referencia por construcción)."}
    for ref, titulo in REFERENCIAS.items():
        L += ["", f"## Aceptación y rechazo — referencia: {titulo}", "", explicacion[ref], "",
              "| Sistema | Oraciones | TP | FP | FN | TN | Sin respuesta | Precisión | Cobertura | F1 | "
              "Rechazo correcto |", "|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in resultados:
            m = r.por_referencia[ref]
            sin = str(m["sin_respuesta"]) if r.sistema.da_sin_respuesta else "—"
            L.append(f"| {r.sistema.nombre} | {m['n']} | {m['TP']} | {m['FP']} | {m['FN']} | {m['TN']} | {sin} | "
                     f"{_pct_ic(m['precision'])} | {_pct_ic(m['cobertura'])} | {_pct(m['f1'])} | "
                     f"{_pct_ic(m['rechazo_correcto'])} |")
    L += ["", "## Desviación de las reglas formales — referencia: gramática", "",
          "Qué hace cada enfoque con lo que la gramática rechaza: si lo acepta siendo español correcto, se desvía "
          "hacia el conocimiento general del español; si lo acepta siendo agramatical, acepta algo que ni la "
          "gramática ni el español admiten.", "",
          "| Sistema | Coincide con la gramática | Acepta lo que la gramática rechaza: español correcto "
          "(desviación hacia el español) | Acepta lo que la gramática rechaza: agramatical | Rechaza lo que la "
          "gramática deriva (sobre-rechazo) | Sin respuesta |", "|---|---|---|---|---|---|"]
    for r in resultados:
        m = r.por_referencia["gramática"]
        sin = str(m["sin_respuesta"]) if r.sistema.da_sin_respuesta else "—"
        L.append(f"| {r.sistema.nombre} | {m['TP'] + m['TN']}/{m['n']} | {m['desviacion_es']} | "
                 f"{m['acepta_agramatical']} | {m['FN']} | {sin} |")
    L += ["", "## Clasificación de errores", "",
          "Los errores de etiquetado se cuentan en las oraciones que son español correcto y que el sistema acepta.", "",
          "| Sistema | FP (español) | FN (español) | FP (gramática) | FN (gramática) | Errores de etiquetado S-V-O | "
          "Errores de etiquetado de categorías | Exactitud S-V-O | Exactitud de categorías | ms/oración |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for r in resultados:
        s, e = r.sistema, r.etiquetado
        es, gr = r.por_referencia["español"], r.por_referencia["gramática"]
        err_svo = str(e["err_svo"]) if s.da_svo else "—"
        err_cat = str(e["err_cat"]) if s.da_categorias else "—"
        exact_cat = f"{_pct(e['exactitud_categorias'])} ({e['oraciones_categorias']} oraciones)" if s.da_categorias \
            else "—"
        L.append(f"| {s.nombre} | {es['FP']} | {es['FN']} | {gr['FP']} | {gr['FN']} | {err_svo} | {err_cat} | "
                 f"{_pct(e['exactitud_svo'])} | {exact_cat} | {e['ms_por_oracion']:.2f} |")
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------ gráficas
SUPERFICIE, TINTA, TINTA_2, TINTA_SUAVE = "#fcfcfb", "#0b0b0b", "#52514e", "#898781"
REJILLA, EJE = "#e1e0d9", "#c3c2b7"
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]          # azul, naranja, aguamarina, amarillo


def _nombre_corto(nombre: str) -> str:
    return nombre.replace(" + ", "\n+ ").replace(" (", "\n(").replace("LLM ", "LLM\n")


def _figura(plt, titulo: str, n_sistemas: int):
    fig, ejes = plt.subplots(2, 1, figsize=(max(9.0, 1.25 * n_sistemas + 2), 9), facecolor=SUPERFICIE)
    fig.suptitle(titulo, x=0.01, ha="left", fontsize=11, color=TINTA)
    for ax, ref in zip(ejes, REFERENCIAS):
        ax.set_facecolor(SUPERFICIE)
        for lado in ("top", "right"):
            ax.spines[lado].set_visible(False)
        for lado in ("left", "bottom"):
            ax.spines[lado].set_color(EJE)
        ax.tick_params(colors=EJE, labelcolor=TINTA_2, labelsize=8)
        ax.grid(axis="y", color=REJILLA, linewidth=0.8)
        ax.set_axisbelow(True)
        ax.set_title(f"Referencia: {REFERENCIAS[ref].split(' (')[0]}", loc="left", fontsize=9.5, color=TINTA_2,
                     pad=24)
    return fig, ejes


def _leyenda(ax, etiquetas: list[str]):
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=SERIES[j], label=e) for j, e in enumerate(etiquetas)], ncol=len(etiquetas),
              frameon=False, fontsize=8, labelcolor=TINTA_2, loc="lower left", bbox_to_anchor=(0, 1.0))


def _guardar(plt, fig, ruta: str) -> str:
    fig.tight_layout()
    fig.savefig(ruta, dpi=150, facecolor=SUPERFICIE, metadata={"Software": None})
    plt.close(fig)
    return ruta


def graficar_metricas(resultados: list[Resultado], ruta: str) -> str:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    claves = [("precision", "Precisión"), ("cobertura", "Cobertura (recall)"), ("rechazo_correcto", "Rechazo correcto")]
    fig, ejes = _figura(plt, "Precisión, cobertura y rechazo correcto por sistema (barras de error: IC 95 %, Wilson)",
                        len(resultados))
    ancho = 0.26
    for ax, ref in zip(ejes, REFERENCIAS):
        for j, (k, _) in enumerate(claves):
            for i, r in enumerate(resultados):
                v, lo, hi = r.por_referencia[ref][k]
                x = i + (j - 1) * ancho
                if v != v:
                    ax.text(x, 1, "n/a", ha="center", va="bottom", fontsize=7, color=TINTA_SUAVE)
                    continue
                ax.bar(x, 100 * v, ancho * 0.85, color=SERIES[j], zorder=2)
                ax.errorbar(x, 100 * v, yerr=[[100 * (v - lo)], [100 * (hi - v)]], fmt="none", ecolor=TINTA_2,
                            elinewidth=1, capsize=2.5, zorder=3)
                ax.text(x, 100 * hi + 1.5, f"{100 * v:.0f}", ha="center", va="bottom", fontsize=6.5, color=TINTA_2)
        ax.set_xticks(range(len(resultados)))
        ax.set_xticklabels([_nombre_corto(r.sistema.nombre) for r in resultados], fontsize=8, color=TINTA)
        ax.set_ylim(0, 112)
        ax.set_yticks(range(0, 101, 20))
        ax.set_ylabel("%", color=TINTA_2)
        _leyenda(ax, [e for _, e in claves])
    return _guardar(plt, fig, ruta)


def graficar_errores(resultados: list[Resultado], ruta: str) -> str:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator
    claves = [("FP", "Falsos positivos"), ("FN", "Falsos negativos"),
              ("err_svo", "Errores de etiquetado S-V-O"), ("err_cat", "Errores de etiquetado de categorías")]
    fig, ejes = _figura(plt, "Clasificación de errores por sistema (número de oraciones)", len(resultados))
    ancho = 0.2

    def valor(r: Resultado, ref: str, k: str) -> int:
        return r.por_referencia[ref][k] if k in ("FP", "FN") else r.etiquetado[k]

    tope = max(valor(r, ref, k) for r in resultados for ref in REFERENCIAS for k, _ in claves)
    for ax, ref in zip(ejes, REFERENCIAS):
        for j, (k, _) in enumerate(claves):
            for i, r in enumerate(resultados):
                x = i + (j - 1.5) * ancho
                if (k == "err_svo" and not r.sistema.da_svo) or (k == "err_cat" and not r.sistema.da_categorias):
                    ax.text(x, 0.2, "n/a", ha="center", va="bottom", fontsize=6.5, color=TINTA_SUAVE, rotation=90)
                    continue
                v = valor(r, ref, k)
                ax.bar(x, v, ancho * 0.85, color=SERIES[j], zorder=2)
                ax.text(x, v + tope * 0.015, str(v), ha="center", va="bottom", fontsize=6.5, color=TINTA_2)
        ax.set_xticks(range(len(resultados)))
        ax.set_xticklabels([_nombre_corto(r.sistema.nombre) for r in resultados], fontsize=8, color=TINTA)
        ax.set_ylim(0, tope * 1.15 + 1)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.set_ylabel("oraciones", color=TINTA_2)
        _leyenda(ax, [e for _, e in claves])
    return _guardar(plt, fig, ruta)


# ------------------------------------------------------------------ programa
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m tlp.espanol.evaluar",
                                 description="Calcula las métricas de todos los enfoques leyendo solo sus logs.")
    ap.add_argument("--logs", default=DIR_LOGS, help="carpeta de los logs (por defecto: resultados/fase2/logs)")
    ap.add_argument("--salida", default=DESTINO, help="carpeta de resultados (por defecto: resultados/fase2)")
    a = ap.parse_args(argv)
    casos = cargar_conjunto()
    sistemas = cargar_sistemas(a.logs)
    if not sistemas:
        print(f"ERROR: no hay logs en {a.logs}. Corre antes:\n  python -m tlp.espanol.comparacion_nlp\n"
              "  python -m tlp.espanol.llm_experimento --variante todas", file=sys.stderr)
        return 2
    resultados = evaluar(casos, sistemas)
    os.makedirs(a.salida, exist_ok=True)
    texto = tablas_md(casos, resultados, a.logs)
    ruta_md = os.path.join(a.salida, "tablas.md")
    with open(ruta_md, "w", encoding="utf-8") as f:
        f.write(texto)
    rutas = [ruta_md,
             escribir_metricas_csv(resultados, os.path.join(a.salida, "metricas_globales.csv")),
             escribir_errores_csv(resultados, os.path.join(a.salida, "errores_detalle.csv")),
             graficar_metricas(resultados, os.path.join(a.salida, "grafica_metricas.png")),
             graficar_errores(resultados, os.path.join(a.salida, "grafica_errores.png"))]
    print(texto)
    print("Archivos escritos:", *rutas, sep="\n  ")
    return 0


if __name__ == "__main__":
    sys.exit(main())
