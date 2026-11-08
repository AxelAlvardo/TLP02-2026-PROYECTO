"""contraste_nlp.py - Contrasta, oración por oración, tres analizadores:

  1. Parser propio (CFG con rasgos)              -> ACEPTA / RECHAZA + regla que falla
  2. NLTK ChartParser sobre la CFG pura expandida -> ACEPTA / RECHAZA + nº de árboles
  3. spaCy (modelo estadístico)                   -> SIEMPRE devuelve un análisis; nunca "rechaza"

Idea central de la Fase 1: la CFG es un RECONOCEDOR (decide pertenencia al lenguaje); spaCy es un
ANALIZADOR ESTADÍSTICO ROBUSTO (siempre produce la mejor estructura, sin garantía de gramaticalidad).

Uso:  python -m tlp.apoyo.contraste_nlp                       # las 10 oraciones del catálogo
      python -m tlp.apoyo.contraste_nlp "los niños duerme"    # una oración
      python -m tlp.apoyo.contraste_nlp --modelo es_core_news_md
Escribe resultados/contraste_nlp.md (solo con el catálogo completo).
"""
from __future__ import annotations

import os
import sys

from ..espanol import ParserEspanol, acepta_nltk, cfg_nltk, extraer_svo
from ..espanol.catalogo_fallas import CATALOGO

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def cargar_spacy(modelo: str = "es_core_news_sm"):
    try:
        import spacy
        return spacy.load(modelo)
    except (ImportError, OSError):
        return None


def _numero(tok) -> str:
    n = tok.morph.get("Number")
    return n[0] if n else "?"


def resumen_spacy(nlp, oracion: str) -> dict:
    """Raíz, sujeto, objeto y una heurística de discordancia sujeto-verbo (propia, NO es una función de spaCy)."""
    doc = nlp(oracion)
    raiz = next((t for t in doc if t.dep_ == "ROOT"), doc[0])
    suj = next((t for t in doc if t.dep_ in ("nsubj", "nsubj:pass")), None)
    obj = next((t for t in doc if t.dep_ in ("obj", "iobj")), None)
    discordancia = bool(suj is not None and raiz.pos_ in ("VERB", "AUX")
                        and _numero(suj) != "?" and _numero(raiz) != "?" and _numero(suj) != _numero(raiz))
    return {"raiz": f"{raiz.text}/{raiz.pos_}", "sujeto": suj.text if suj is not None else "—",
            "objeto": obj.text if obj is not None else "—", "discordancia_heuristica": discordancia,
            "tokens": [(t.text, t.pos_, t.dep_, t.head.text, str(t.morph)) for t in doc]}


def contrastar(oraciones: list[str], modelo: str = "es_core_news_sm") -> list[dict]:
    parser, (g, _) = ParserEspanol(), cfg_nltk()
    nlp = cargar_spacy(modelo)
    filas = []
    for o in oraciones:
        arbol, diag = parser.parse(o)
        acepta_cfg, n_arboles = acepta_nltk(g, o)
        fila = {"oracion": o, "propio": "ACEPTA" if arbol else "RECHAZA", "diagnostico": diag,
                "svo_propio": extraer_svo(arbol) if arbol else None,
                "nltk": f"ACEPTA ({n_arboles} árbol/es)" if acepta_cfg else "RECHAZA",
                "spacy": resumen_spacy(nlp, o) if nlp else None}
        filas.append(fila)
    return filas


def imprimir(filas: list[dict]) -> None:
    for f in filas:
        print("=" * 78, f"\nORACIÓN: {f['oracion']}")
        print("  parser propio :", f["propio"], "—", f["svo_propio"] if f["svo_propio"] else f["diagnostico"])
        print("  NLTK (CFG pura):", f["nltk"])
        s = f["spacy"]
        if s is None:
            print("  spaCy         : modelo no instalado (python -m spacy download es_core_news_sm)")
            continue
        print(f"  spaCy         : raíz={s['raiz']} sujeto={s['sujeto']} objeto={s['objeto']}  "
              f"discordancia(heurística)={'SÍ' if s['discordancia_heuristica'] else 'no'}")
        for t in s["tokens"]:
            print(f"      {t[0]:12} POS={t[1]:6} DEP={t[2]:10} padre={t[3]:10} {t[4]}")


def escribir_informe(filas: list[dict], modelo: str) -> str:
    clase = {c[0]: (c[1], c[2]) for c in CATALOGO}
    out = ["# Fase 1 — Contraste: parser propio (CFG) vs NLTK vs spaCy", "",
           f"Modelo spaCy: `{modelo}`. La columna «spaCy» siempre produce un análisis; la heurística de discordancia "
           "compara el rasgo Number del sujeto y del verbo raíz (es una verificación propia, no una función de spaCy).", "",
           "| # | Oración | Fenómeno (clase) | Parser propio | NLTK (CFG pura) | spaCy: raíz / sujeto / objeto | ¿Detecta discordancia? |",
           "|---|---|---|---|---|---|---|"]
    for i, f in enumerate(filas, 1):
        fen, cl = clase.get(f["oracion"], ("—", "—"))
        s = f["spacy"]
        sp = f"{s['raiz']} / {s['sujeto']} / {s['objeto']}" if s else "n/d"
        disc = ("SÍ" if s and s["discordancia_heuristica"] else "no") if s else "n/d"
        out.append(f"| {i} | `{f['oracion']}` | {fen} ({cl}) | {f['propio']} | {f['nltk']} | {sp} | {disc} |")
    out += ["", "**Lectura.** Donde el parser propio RECHAZA (clítico, pro-drop, coordinación, relativa de objeto, "
            "interrogativa, dependencias cruzadas) spaCy igualmente entrega una estructura: no hay noción de "
            "«fuera del lenguaje», solo la mejor estimación. A la inversa, donde la CFG acepta con ambigüedad "
            "(PP-attachment) devuelve todas las lecturas sin elegir, mientras spaCy elige una sola. "
            "Las discordancias (filas 7 y 8) las rechaza la gramática por construcción; spaCy las analiza como "
            "si fueran gramaticales salvo que se añada una verificación externa.", ""]
    ruta = os.path.join(RAIZ, "resultados", "contraste_nlp.md")
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out))
    return ruta


def main(argv: list[str]) -> int:
    modelo = "es_core_news_sm"
    if "--modelo" in argv:
        k = argv.index("--modelo")
        modelo = argv[k + 1]
        argv = argv[:k] + argv[k + 2:]
    if argv:
        imprimir(contrastar([" ".join(argv)], modelo))
        return 0
    filas = contrastar([c[0] for c in CATALOGO], modelo)
    imprimir(filas)
    print("\nInforme:", escribir_informe(filas, modelo))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
