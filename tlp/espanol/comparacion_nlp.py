"""tlp/espanol/comparacion_nlp.py - Fase 2 (puntos 4 y 5): el parser propio frente a spaCy y HuggingFace.

Procesa el conjunto de prueba (casos/espanol/conjunto_prueba.csv) con cada sistema, decide si ACEPTA o RECHAZA
cada oración y calcula las métricas. Escribe en resultados/fase2/:
  tablas.md               tablas de aceptación/rechazo y de clasificación de errores
  metricas_globales.csv   las mismas métricas, con sus intervalos de confianza
  errores_detalle.csv     cada falso positivo, falso negativo y error de etiquetado, con su motivo
  grafica_metricas.png    precisión, cobertura y rechazo correcto por sistema (con IC 95 %)
  grafica_errores.png     falsos positivos, falsos negativos y errores de etiquetado por sistema

Uso:  python -m tlp.espanol.comparacion_nlp
      python -m tlp.espanol.comparacion_nlp --modelos sm md     # modelos es_core_news_* (los no instalados se omiten)
      python -m tlp.espanol.comparacion_nlp --hf-modelo <id>    # otro etiquetador UPOS de HuggingFace

Criterio de aceptación de cada sistema:
  Parser propio           acepta si la gramática da al menos una derivación.
  spaCy (crudo)           acepta siempre: un modelo estadístico nunca rechaza (línea base).
  spaCy + concordancia    rechaza si la raíz no es verbo, si no coincide el número sujeto-verbo o si no coinciden
                          género/número entre determinante o adjetivo y sustantivo, según los rasgos que predice el
                          propio spaCy (heurística propia, no es una función de spaCy).
  HuggingFace + reglas    etiqueta cada palabra (UPOS, sin signos de puntuación) y rechaza si:
                          R1 no hay verbo (VERB/AUX);  R2 alguna palabra es X (categoría desconocida);
                          R3 tras un determinante no viene NOUN/PROPN/ADJ/NUM/DET, o el determinante queda al final;
                          R4 tras una preposición no viene DET/NOUN/PROPN/PRON/NUM/ADJ/VERB, o queda al final.

Métricas. Referencia = la columna gramatical_es (¿es español correcto?), NO lo que acepta la gramática.
Positivo = la oración es gramatical y el sistema la acepta:
  TP gramatical y aceptada    FP agramatical y aceptada    FN gramatical y rechazada    TN agramatical y rechazada
  Precisión = TP/(TP+FP)    Cobertura (recall) = TP/(TP+FN)    Rechazo correcto = TN/(TN+FP)    F1 = 2PC/(P+C)
  Cada proporción lleva su intervalo de confianza del 95 % (método de Wilson).
Errores de etiquetado (oraciones gramaticales que el sistema acepta):
  S-V-O        la tripleta (sujeto, verbo, objeto) no es la esperada                [parser propio, spaCy]
  categorías   alguna palabra recibe una categoría UPOS distinta de la del léxico    [spaCy, HuggingFace]
               (solo oraciones con todas sus palabras en el léxico; «al» y «del» valen ADP o DET)
"""
from __future__ import annotations

import argparse
import csv
import math
import os
import re
import sys
import time
import unicodedata
from dataclasses import dataclass

from .conjunto import RAIZ, Caso, cargar_conjunto
from .gramatica_es import LEMA_DE_FORMA, LEXICO, ParserEspanol, extraer_svo

DESTINO = os.path.join(RAIZ, "resultados", "fase2")
HF_MODELO = "wietsedv/xlm-roberta-base-ft-udpos28-es"

CAT2UPOS = {"DET": {"DET"}, "N": {"NOUN"}, "PN": {"PROPN"}, "ADJ": {"ADJ"}, "V": {"VERB", "AUX"},
            "ADV": {"ADV"}, "P": {"ADP"}, "QUE": {"PRON", "SCONJ"}}
CONTRACCIONES = {"al": {"ADP", "DET"}, "del": {"ADP", "DET"}}
TRAS_DET = {"NOUN", "PROPN", "ADJ", "NUM", "DET"}                       # regla R3
TRAS_ADP = {"DET", "NOUN", "PROPN", "PRON", "NUM", "ADJ", "VERB"}       # regla R4


@dataclass
class Analisis:
    """Lo que respondió un sistema para una oración."""
    acepta: bool
    motivo: str = ""                                    # por qué la rechaza (vacío si la acepta)
    svo: tuple[str, str, str] | None = None             # None si el sistema no da sujeto-verbo-objeto
    categorias: tuple[int, int] | None = None           # (palabras bien etiquetadas, palabras); None = no se evalúa
    mal_etiquetadas: str = ""


@dataclass
class Sistema:
    nombre: str
    analisis: list[Analisis]                            # uno por oración, en el orden del conjunto
    ms_por_oracion: float
    da_svo: bool
    da_categorias: bool


# ------------------------------------------------------------------ categorías (UPOS) esperadas
def _palabras(oracion: str) -> list[str]:
    """Palabras de la oración, sin signos de puntuación y sin separar «al»/«del»."""
    return re.findall(r"\w+", unicodedata.normalize("NFC", oracion))


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


def comparar_categorias(caso: Caso, palabras: list[str], etiquetas: list[str]) -> tuple[tuple[int, int] | None, str]:
    """((bien etiquetadas, total), palabras mal etiquetadas); (None, '') si la oración no se puede evaluar."""
    oro = _categorias_esperadas(palabras) if caso.gramatical_es else None
    if oro is None or len(etiquetas) != len(oro):
        return None, ""
    malas = [f"{p}={e}" for p, e, o in zip(palabras, etiquetas, oro) if e not in o]
    return (len(oro) - len(malas), len(oro)), ", ".join(malas)


# ------------------------------------------------------------------ parser propio
def analizar_propio(casos: list[Caso]) -> Sistema:
    parser, out = ParserEspanol(), []
    t0 = time.perf_counter()
    for c in casos:
        arbol, diagnostico = parser.parse(c.oracion)
        out.append(Analisis(acepta=arbol is not None, motivo="" if arbol else diagnostico,
                            svo=extraer_svo(arbol) if arbol else None))
    ms = 1000 * (time.perf_counter() - t0) / len(casos)
    return Sistema("Parser propio (CFG)", out, ms, da_svo=True, da_categorias=False)


# ------------------------------------------------------------------ spaCy
def _lema(tok) -> str:
    return LEMA_DE_FORMA.get(tok.text.lower()) or tok.lemma_.lower()


def _svo_spacy(doc) -> tuple[str, str, str] | None:
    raiz = next((t for t in doc if t.dep_ == "ROOT"), None)
    if raiz is None:
        return None
    sujeto = next((_lema(c) for c in raiz.children if c.dep_.startswith(("nsubj", "csubj"))), "-")
    objeto = next((_lema(c) for c in raiz.children if c.dep_ in ("obj", "dobj")), "-")
    return sujeto, _lema(raiz), objeto


def _rasgo(tok, k: str) -> str | None:
    v = tok.morph.get(k)
    return v[0] if v else None


def concordancia_spacy(doc) -> str:
    """Criterio «+ concordancia»: '' si no encuentra discordancias; si no, el motivo del rechazo."""
    raiz = next((t for t in doc if t.dep_ == "ROOT"), None)
    if raiz is None or raiz.pos_ not in ("VERB", "AUX"):
        return "la raíz no es un verbo"
    for t in doc:
        if t.dep_.startswith("nsubj") and t.head.pos_ in ("VERB", "AUX"):
            a, b = _rasgo(t, "Number"), _rasgo(t.head, "Number")
            if a and b and a != b:
                return f"número sujeto-verbo: {t.text} ({a}) vs {t.head.text} ({b})"
        if t.dep_ in ("det", "amod") and t.head.pos_ in ("NOUN", "PROPN"):
            for k, rasgo in (("Number", "número"), ("Gender", "género")):
                a, b = _rasgo(t, k), _rasgo(t.head, k)
                if a and b and a != b:
                    return f"{rasgo}: {t.text} ({a}) vs {t.head.text} ({b})"
    return ""


def analizar_spacy(casos: list[Caso], sufijo: str = "sm") -> tuple[list[Sistema], str]:
    """Dos sistemas con el mismo análisis de spaCy: crudo (acepta todo) y + concordancia."""
    import spacy
    nlp = spacy.load(f"es_core_news_{sufijo}")
    crudo, conc, dur = [], [], 0.0
    for c in casos:
        t0 = time.perf_counter()
        doc = nlp(c.oracion)
        dur += time.perf_counter() - t0
        svo = _svo_spacy(doc)
        toks = [t for t in doc if not t.is_punct]
        palabras = _palabras(c.oracion)
        if [t.text.lower() for t in toks] == [p.lower() for p in palabras]:
            cats, malas = comparar_categorias(c, palabras, [t.pos_ for t in toks])
        else:                                                   # spaCy tokenizó distinto: no se evalúa
            cats, malas = None, ""
        motivo = concordancia_spacy(doc)
        crudo.append(Analisis(True, "", svo, cats, malas))
        conc.append(Analisis(motivo == "", motivo, svo, cats, malas))
    ms = 1000 * dur / len(casos)
    version = f"spaCy {spacy.__version__}, modelo es_core_news_{sufijo} {nlp.meta.get('version', '?')}"
    return [Sistema(f"spaCy {sufijo} (crudo)", crudo, ms, da_svo=True, da_categorias=True),
            Sistema(f"spaCy {sufijo} + concordancia", conc, ms, da_svo=True, da_categorias=True)], version


# ------------------------------------------------------------------ HuggingFace
class EtiquetadorHF:
    """Etiquetador UPOS de HuggingFace: una etiqueta por palabra (la de su primer subtoken)."""

    def __init__(self, modelo: str = HF_MODELO):
        import torch
        from transformers import AutoModelForTokenClassification, AutoTokenizer
        self._torch = torch
        self.tokenizador = AutoTokenizer.from_pretrained(modelo)
        self.modelo = AutoModelForTokenClassification.from_pretrained(modelo).eval()

    def etiquetar(self, palabras: list[str]) -> list[str]:
        enc = self.tokenizador(palabras, is_split_into_words=True, return_tensors="pt")
        with self._torch.no_grad():
            pred = self.modelo(**enc).logits[0].argmax(-1).tolist()
        etiquetas = [""] * len(palabras)
        for i, w in enumerate(enc.word_ids()):
            if w is not None and not etiquetas[w]:
                etiquetas[w] = self.modelo.config.id2label[pred[i]]
        return etiquetas


def reglas_upos(palabras: list[str], etiquetas: list[str]) -> str:
    """Criterio «+ reglas» de HuggingFace: '' si la secuencia de categorías es aceptable; si no, la regla que falla."""
    if not any(e in ("VERB", "AUX") for e in etiquetas):
        return "R1: no hay ningún verbo"
    for p, e in zip(palabras, etiquetas):
        if e == "X":
            return f"R2: '{p}' tiene categoría desconocida (X)"
    for i, (p, e) in enumerate(zip(palabras, etiquetas)):
        sig = etiquetas[i + 1] if i + 1 < len(etiquetas) else "fin de oración"
        if e == "DET" and sig not in TRAS_DET:
            return f"R3: tras el determinante '{p}' viene {sig}"
        if e == "ADP" and sig not in TRAS_ADP:
            return f"R4: tras la preposición '{p}' viene {sig}"
    return ""


def analizar_hf(casos: list[Caso], modelo: str = HF_MODELO) -> tuple[Sistema, str]:
    import torch
    import transformers
    etiquetador = EtiquetadorHF(modelo)
    out, dur = [], 0.0
    for c in casos:
        palabras = _palabras(c.oracion)
        t0 = time.perf_counter()
        etiquetas = etiquetador.etiquetar(palabras)
        dur += time.perf_counter() - t0
        motivo = reglas_upos(palabras, etiquetas)
        cats, malas = comparar_categorias(c, palabras, etiquetas)
        out.append(Analisis(motivo == "", motivo, None, cats, malas))
    version = f"HuggingFace transformers {transformers.__version__} (torch {torch.__version__}), modelo {modelo}"
    return Sistema("HuggingFace + reglas", out, 1000 * dur / len(casos), da_svo=False, da_categorias=True), version


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


def _svo_correcta(pred, oro) -> bool:
    return pred is not None and all(g == "*" or g == p for g, p in zip(oro, pred))


def metricas(casos: list[Caso], sistema: Sistema) -> tuple[dict, list[dict]]:
    """(métricas, errores) de un sistema frente a la referencia gramatical_es."""
    m = dict(TP=0, FP=0, FN=0, TN=0, err_svo=0, err_cat=0)
    errores = []
    svo_total = svo_bien = cat_bien = cat_total = cat_oraciones = 0
    for c, a in zip(casos, sistema.analisis):
        clave = ("TP" if a.acepta else "FN") if c.gramatical_es else ("FP" if a.acepta else "TN")
        m[clave] += 1
        if clave in ("FP", "FN"):
            errores.append(dict(caso=c, tipo="falso positivo" if clave == "FP" else "falso negativo",
                                detalle=a.motivo or c.fenomeno))
        if sistema.da_svo and c.gramatical_es and c.svo and any(x != "*" for x in c.svo):
            svo_total += 1
            bien = a.acepta and _svo_correcta(a.svo, c.svo)
            svo_bien += bien
            if a.acepta and not bien:
                m["err_svo"] += 1
                errores.append(dict(caso=c, tipo="error de etiquetado (S-V-O)",
                                    detalle=f"esperado {c.svo}, obtenido {a.svo}"))
        if sistema.da_categorias and a.categorias:
            bien_cat, total = a.categorias
            cat_bien, cat_total, cat_oraciones = cat_bien + bien_cat, cat_total + total, cat_oraciones + 1
            if a.acepta and bien_cat < total:
                m["err_cat"] += 1
                errores.append(dict(caso=c, tipo="error de etiquetado (categorías)",
                                    detalle=f"mal etiquetadas: {a.mal_etiquetadas}"))
    tp, fp, fn, tn = m["TP"], m["FP"], m["FN"], m["TN"]
    m["precision"], m["cobertura"] = _proporcion(tp, tp + fp), _proporcion(tp, tp + fn)
    m["rechazo_correcto"] = _proporcion(tn, tn + fp)
    p, r = m["precision"][0], m["cobertura"][0]
    m["f1"] = 2 * p * r / (p + r) if p + r else math.nan
    m["exactitud_svo"] = svo_bien / svo_total if sistema.da_svo and svo_total else math.nan
    m["exactitud_categorias"] = cat_bien / cat_total if cat_total else math.nan
    m["oraciones_categorias"] = cat_oraciones
    m["ms_por_oracion"] = sistema.ms_por_oracion
    return m, errores


# ------------------------------------------------------------------ salidas: CSV y Markdown
def _r(v: float):
    return "" if v != v else round(v, 4)


def _pct(v: float) -> str:
    return "—" if v != v else f"{100 * v:.1f}%"


def _pct_ic(t: tuple[float, float, float]) -> str:
    v, lo, hi = t
    return "—" if v != v else f"{100 * v:.1f}% [{100 * lo:.1f}–{100 * hi:.1f}]"


def escribir_metricas_csv(resultados, ruta: str) -> str:
    campos = ["sistema", "TP", "FP", "FN", "TN",
              "precision", "precision_ic95_inf", "precision_ic95_sup",
              "cobertura", "cobertura_ic95_inf", "cobertura_ic95_sup", "f1",
              "rechazo_correcto", "rechazo_correcto_ic95_inf", "rechazo_correcto_ic95_sup",
              "errores_etiquetado_svo", "errores_etiquetado_categorias", "exactitud_svo", "exactitud_categorias",
              "oraciones_categorias", "ms_por_oracion"]
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(campos)
        for s, m, _ in resultados:
            fila = [s.nombre, m["TP"], m["FP"], m["FN"], m["TN"]]
            fila += [_r(x) for x in m["precision"]] + [_r(x) for x in m["cobertura"]] + [_r(m["f1"])]
            fila += [_r(x) for x in m["rechazo_correcto"]]
            fila += [m["err_svo"] if s.da_svo else "", m["err_cat"] if s.da_categorias else "",
                     _r(m["exactitud_svo"]), _r(m["exactitud_categorias"]),
                     m["oraciones_categorias"] if s.da_categorias else "", _r(m["ms_por_oracion"])]
            w.writerow(fila)
    return ruta


def escribir_errores_csv(resultados, ruta: str) -> str:
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["sistema", "id", "nivel", "oracion", "tipo", "detalle"])
        for s, _, errores in resultados:
            for e in errores:
                c = e["caso"]
                w.writerow([s.nombre, c.id, c.nivel, c.oracion, e["tipo"], e["detalle"]])
    return ruta


def tablas_md(casos: list[Caso], resultados, herramientas: list[str]) -> str:
    n_si = sum(c.gramatical_es for c in casos)
    L = ["# Fase 2 — Parser propio vs spaCy vs HuggingFace", "",
         f"Conjunto de prueba: {len(casos)} oraciones ({n_si} gramaticales y {len(casos) - n_si} agramaticales según "
         "`gramatical_es`). Entre corchetes, intervalo de confianza del 95 % (Wilson). «—» = el sistema no produce "
         "ese dato (las categorías del parser propio salen del léxico, que es la referencia).", ""]
    L += [f"- {h}" for h in herramientas] + [""]
    L += ["## Aceptación y rechazo", "",
          "| Sistema | TP | FP | FN | TN | Precisión | Cobertura | F1 | Rechazo correcto |",
          "|---|---|---|---|---|---|---|---|---|"]
    for s, m, _ in resultados:
        L.append(f"| {s.nombre} | {m['TP']} | {m['FP']} | {m['FN']} | {m['TN']} | {_pct_ic(m['precision'])} | "
                 f"{_pct_ic(m['cobertura'])} | {_pct(m['f1'])} | {_pct_ic(m['rechazo_correcto'])} |")
    L += ["", "## Clasificación de errores y etiquetado", "",
          "| Sistema | Falsos positivos | Falsos negativos | Errores de etiquetado S-V-O | "
          "Errores de etiquetado de categorías | Exactitud S-V-O | Exactitud de categorías | ms/oración |",
          "|---|---|---|---|---|---|---|---|"]
    for s, m, _ in resultados:
        err_svo = str(m["err_svo"]) if s.da_svo else "—"
        err_cat = str(m["err_cat"]) if s.da_categorias else "—"
        exact_cat = (f"{_pct(m['exactitud_categorias'])} ({m['oraciones_categorias']} oraciones)"
                     if s.da_categorias else "—")
        L.append(f"| {s.nombre} | {m['FP']} | {m['FN']} | {err_svo} | {err_cat} | {_pct(m['exactitud_svo'])} | "
                 f"{exact_cat} | {m['ms_por_oracion']:.2f} |")
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------ gráficas
SUPERFICIE, TINTA, TINTA_2, TINTA_SUAVE = "#fcfcfb", "#0b0b0b", "#52514e", "#898781"
REJILLA, EJE = "#e1e0d9", "#c3c2b7"
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]          # azul, naranja, aguamarina, amarillo


def _nombre_corto(nombre: str) -> str:
    return nombre.replace(" + ", "\n+ ").replace(" (", "\n(")


def _preparar(plt, titulo: str):
    fig, ax = plt.subplots(figsize=(9, 4.8), facecolor=SUPERFICIE)
    ax.set_facecolor(SUPERFICIE)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        ax.spines[lado].set_color(EJE)
    ax.tick_params(colors=EJE, labelcolor=TINTA_2, labelsize=8)
    ax.grid(axis="y", color=REJILLA, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.set_title(titulo, loc="left", fontsize=10, color=TINTA, pad=30)
    return fig, ax


def _leyenda(ax, etiquetas: list[str]):
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=SERIES[j], label=e) for j, e in enumerate(etiquetas)], ncol=len(etiquetas),
              frameon=False, fontsize=8, labelcolor=TINTA_2, loc="lower left", bbox_to_anchor=(0, 1.0))


def graficar_metricas(resultados, ruta: str) -> str:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    claves = [("precision", "Precisión"), ("cobertura", "Cobertura (recall)"), ("rechazo_correcto", "Rechazo correcto")]
    fig, ax = _preparar(plt, "Precisión, cobertura y rechazo correcto por sistema (barras: IC 95 %, Wilson)")
    ancho = 0.26
    for j, (k, _) in enumerate(claves):
        for i, (_, m, _) in enumerate(resultados):
            v, lo, hi = m[k]
            x = i + (j - 1) * ancho
            if v != v:
                ax.text(x, 1, "n/a", ha="center", va="bottom", fontsize=7, color=TINTA_SUAVE)
                continue
            ax.bar(x, 100 * v, ancho * 0.85, color=SERIES[j], zorder=2)
            ax.errorbar(x, 100 * v, yerr=[[100 * (v - lo)], [100 * (hi - v)]], fmt="none", ecolor=TINTA_2,
                        elinewidth=1, capsize=2.5, zorder=3)
            ax.text(x, 100 * hi + 1.5, f"{100 * v:.0f}", ha="center", va="bottom", fontsize=7, color=TINTA_2)
    ax.set_xticks(range(len(resultados)))
    ax.set_xticklabels([_nombre_corto(s.nombre) for s, _, _ in resultados], fontsize=8, color=TINTA)
    ax.set_ylim(0, 110)
    ax.set_yticks(range(0, 101, 20))
    ax.set_ylabel("%", color=TINTA_2)
    _leyenda(ax, [e for _, e in claves])
    fig.tight_layout()
    fig.savefig(ruta, dpi=150, facecolor=SUPERFICIE)
    plt.close(fig)
    return ruta


def graficar_errores(resultados, ruta: str) -> str:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator
    claves = [("FP", "Falsos positivos"), ("FN", "Falsos negativos"),
              ("err_svo", "Errores de etiquetado S-V-O"), ("err_cat", "Errores de etiquetado de categorías")]
    fig, ax = _preparar(plt, "Clasificación de errores por sistema (número de oraciones)")
    ancho = 0.2
    tope = max(max(m[k] for k, _ in claves) for _, m, _ in resultados)
    for j, (k, _) in enumerate(claves):
        for i, (s, m, _) in enumerate(resultados):
            x = i + (j - 1.5) * ancho
            if (k == "err_svo" and not s.da_svo) or (k == "err_cat" and not s.da_categorias):
                ax.text(x, 0.2, "n/a", ha="center", va="bottom", fontsize=6.5, color=TINTA_SUAVE, rotation=90)
                continue
            ax.bar(x, m[k], ancho * 0.85, color=SERIES[j], zorder=2)
            ax.text(x, m[k] + tope * 0.015, str(m[k]), ha="center", va="bottom", fontsize=7, color=TINTA_2)
    ax.set_xticks(range(len(resultados)))
    ax.set_xticklabels([_nombre_corto(s.nombre) for s, _, _ in resultados], fontsize=8, color=TINTA)
    ax.set_ylim(0, tope * 1.15 + 1)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_ylabel("oraciones", color=TINTA_2)
    _leyenda(ax, [e for _, e in claves])
    fig.tight_layout()
    fig.savefig(ruta, dpi=150, facecolor=SUPERFICIE)
    plt.close(fig)
    return ruta


# ------------------------------------------------------------------ programa
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m tlp.espanol.comparacion_nlp",
                                 description="Parser propio vs spaCy vs HuggingFace sobre el conjunto de prueba.")
    ap.add_argument("--modelos", nargs="+", default=["sm"], help="sufijos de es_core_news_* (por defecto: sm)")
    ap.add_argument("--hf-modelo", default=HF_MODELO, help=f"etiquetador UPOS de HuggingFace (por defecto: {HF_MODELO})")
    ap.add_argument("--salida", default=DESTINO, help="carpeta de resultados (por defecto: resultados/fase2)")
    a = ap.parse_args(argv)

    casos = cargar_conjunto()
    sistemas, herramientas = [analizar_propio(casos)], []
    for sufijo in a.modelos:
        try:
            sis, version = analizar_spacy(casos, sufijo)
            sistemas += sis
            herramientas.append(version)
        except (ImportError, OSError) as e:
            print(f"[aviso] se omite spaCy es_core_news_{sufijo}: {e}", file=sys.stderr)
    try:
        sis, version = analizar_hf(casos, a.hf_modelo)
        sistemas.append(sis)
        herramientas.append(version)
    except (ImportError, OSError) as e:
        print(f"[aviso] se omite HuggingFace {a.hf_modelo}: {e}", file=sys.stderr)

    resultados = [(s, *metricas(casos, s)) for s in sistemas]
    os.makedirs(a.salida, exist_ok=True)
    texto = tablas_md(casos, resultados, herramientas)
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
