"""contraste_nlp.py - Contrasta, oración por oración, los analizadores sobre las MISMAS oraciones:

  1. Parser propio (CFG con rasgos)               -> ACEPTA / RECHAZA + regla que falla      [siempre]
  2. NLTK ChartParser sobre la CFG pura expandida -> ACEPTA / RECHAZA + nº de árboles        [siempre]
  3. spaCy (modelo estadístico, OPCIONAL)         -> siempre devuelve un análisis; no rechaza [solo si hay modelo]

NLTK se usa aquí como motor CFG independiente (sin descargar corpus): confirma que el parser propio y una CFG sin
rasgos aceptan lo mismo y cuenta TODAS las lecturas. NO es un analizador estadístico: el contraste "reconocedor
formal vs. modelo estadístico" solo existe si spaCy y su modelo están instalados. Si no lo están, el informe lo
dice explícitamente y no incluye ninguna columna de spaCy.

Uso:  python -m tlp.apoyo.contraste_nlp                       # las 10 oraciones del catálogo
      python -m tlp.apoyo.contraste_nlp "los niños duerme"    # una oración (no escribe informe)
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
    """Devuelve el pipeline de spaCy o None si spaCy / el modelo no están instalados (dependencia opcional)."""
    try:
        import spacy
    except ImportError:
        return None
    try:
        return spacy.load(modelo)
    except OSError:                      # paquete spaCy presente pero modelo no descargado
        return None


def version_spacy(nlp) -> str:
    import spacy
    return f"spaCy {spacy.__version__}, modelo {nlp.meta.get('lang', '?')}_{nlp.meta.get('name', '?')} {nlp.meta.get('version', '?')}"


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
            print("  spaCy         : NO EJECUTADO (opcional: pip install -r requirements-spacy.txt && python -m spacy download es_core_news_sm)")
            continue
        print(f"  spaCy         : raíz={s['raiz']} sujeto={s['sujeto']} objeto={s['objeto']}  "
              f"discordancia(heurística)={'SÍ' if s['discordancia_heuristica'] else 'no'}")
        for t in s["tokens"]:
            print(f"      {t[0]:12} POS={t[1]:6} DEP={t[2]:10} padre={t[3]:10} {t[4]}")


def escribir_informe(filas: list[dict], modelo: str) -> str:
    clase = {c[0]: (c[1], c[2]) for c in CATALOGO}
    hay_spacy = all(f["spacy"] is not None for f in filas)
    out = ["# Fase 1 — Contraste: parser propio (CFG) vs NLTK" + (" vs spaCy" if hay_spacy else ""), "",
           "## 1. Parser propio vs NLTK (siempre reproducible, sin descargar modelos)", "",
           "NLTK actúa como motor CFG independiente sobre la gramática expandida sin rasgos. Lo que muestra: (a) que la "
           "concordancia con rasgos finitos sigue siendo libre de contexto (ambos aceptan exactamente lo mismo) y (b) "
           "TODAS las lecturas de una oración ambigua. Lo que NO muestra: capacidad de análisis estadístico; NLTK aquí "
           "tampoco puede analizar nada que la CFG no cubra.", "",
           "| # | Oración | Fenómeno (clase) | Parser propio | NLTK (CFG pura) |", "|---|---|---|---|---|"]
    for i, f in enumerate(filas, 1):
        fen, cl = clase.get(f["oracion"], ("—", "—"))
        out.append(f"| {i} | `{f['oracion']}` | {fen} ({cl}) | {f['propio']} | {f['nltk']} |")
    out += ["", "## 2. spaCy (opcional)", ""]
    if not hay_spacy:
        out += [f"**No generada**: spaCy o el modelo `{modelo}` no están instalados en el entorno que produjo este informe, "
                "así que no se ejecutó ninguna comparación con spaCy. Para generarla: "
                f"`pip install -r requirements-spacy.txt` y `python -m spacy download {modelo}`, y volver a ejecutar "
                "`python -m tlp.apoyo.contraste_nlp`.", ""]
    else:
        import spacy
        nlp = spacy.load(modelo)
        out += [f"Ejecutado con {version_spacy(nlp)}. spaCy siempre produce un análisis; la columna de discordancia "
                "compara el rasgo Number del sujeto y del verbo raíz y es una heurística PROPIA, no una función de spaCy.", "",
                "| # | Oración | spaCy: raíz / sujeto / objeto | ¿Discordancia (heurística)? |", "|---|---|---|---|"]
        for i, f in enumerate(filas, 1):
            s = f["spacy"]
            out.append(f"| {i} | `{f['oracion']}` | {s['raiz']} / {s['sujeto']} / {s['objeto']} | "
                       f"{'SÍ' if s['discordancia_heuristica'] else 'no'} |")
        out += ["", "**Lectura** (sobre estas 10 oraciones y este modelo, sin generalizar). Donde el parser propio rechaza por "
                "alcance (clítico, pro-drop, coordinación, relativa de objeto, interrogativa), spaCy igualmente entrega una "
                "estructura: no existe la noción de «fuera del lenguaje». En `el gato la persigue` esa estructura es "
                "incorrecta (*persigue* etiquetado como NOUN); en la relativa de objeto es correcta. Ante la ambigüedad "
                "de adjunción spaCy elige una sola lectura sin indicarlo. Las discordancias (filas 7 y 8) la gramática "
                "las rechaza por construcción; spaCy las analiza como si fueran gramaticales.", ""]
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
