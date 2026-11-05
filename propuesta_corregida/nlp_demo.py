"""
Módulo 6: Comparación de la CFG propia con herramientas de NLP sobre el MISMO corpus.

Columnas del resumen:
  * CFG propia            : acepta (nº de derivaciones) / rechaza (tipo de fallo)
  * NLTK chart (CFG con concordancia)  : nº de árboles que enumera un chart parser sobre la
                            CFG explícita generada por build_cfg(True) (verificación independiente)
  * NLTK chart (sin concordancia)      : idem sobre build_cfg(False): muestra la sobre-generación
  * spaCy                 : raíz y relación del sujeto del análisis de dependencias
                            (modelo estadístico: SIEMPRE devuelve un árbol, nunca rechaza)

Uso:
    python nlp_demo.py            # tabla resumen + árboles de dependencias spaCy
    python nlp_demo.py --table    # solo la tabla
"""

import sys
from typing import List

from spanish_parser import CORPUS, SpanishCFGParser, SpanishGrammarError, build_cfg, cfg_stats, to_nltk_text


def own_result(text: str) -> str:
    try:
        n = SpanishCFGParser(text).count_parses()
        if n:
            return f"ACEPTA ({n} árbol{'es' if n != 1 else ''})"
        SpanishCFGParser(text).parse()
    except SpanishGrammarError as exc:
        return f"RECHAZA [{exc.kind}]"
    return "RECHAZA"


def _chart(split: bool):
    from nltk import CFG, ChartParser
    return ChartParser(CFG.fromstring(to_nltk_text(build_cfg(split))))


def nltk_count(parser, text: str) -> str:
    try:
        return str(len(list(parser.parse(text.lower().split()))))
    except ValueError:
        return "OOV"


def format_spacy_tree(token, level: int = 0) -> str:
    indent = "  " * level
    morph = f" [{token.morph}]" if str(token.morph) else ""
    line = f"{indent}└── {token.text} (POS: {token.pos_}, Dep: {token.dep_}){morph}\n"
    for child in token.children:
        line += format_spacy_tree(child, level + 1)
    return line


def load_spacy():
    try:
        import spacy
        return spacy.load("es_core_news_sm")
    except (ImportError, OSError):
        return None


def spacy_summary(nlp, text: str) -> str:
    doc = nlp(text)
    root = next(t for t in doc if t.head == t)
    subj = next((t for t in doc if t.dep_ in ("nsubj", "nsubj:pass")), None)
    return f"raíz={root.text}/{root.pos_}, sujeto={subj.text if subj else '—'}"


def run_table(nlp) -> None:
    split, unsplit = _chart(True), _chart(False)
    s, u = cfg_stats(build_cfg(True)), cfg_stats(build_cfg(False))
    print("=== Comparación sobre el mismo corpus ===\n")
    print(f"CFG con concordancia : {s['no_terminales']} no terminales, {s['producciones_estructurales']} reglas "
          f"estructurales + {s['producciones_lexicas']} léxicas")
    print(f"CFG sin concordancia : {u['no_terminales']} no terminales, {u['producciones_estructurales']} reglas "
          f"estructurales + {u['producciones_lexicas']} léxicas\n")
    head = f"{'ID':<3} {'CFG propia':<22} {'NLTK c/conc.':<13} {'NLTK s/conc.':<13} spaCy   |  oración"
    print(head)
    print("-" * 110)
    for e in CORPUS:
        t = e["text"]
        sp = spacy_summary(nlp, t) if nlp else "(spaCy no instalado)"
        print(f"{e['id']:<3} {own_result(t):<22} {nltk_count(split, t):<13} {nltk_count(unsplit, t):<13} {sp}  |  {t}")
    print("\nNota: spaCy es un modelo estadístico de dependencias; no valida gramaticalidad, así que"
          " acepta también B1-B3.\nTampoco es infalible: revise a mano los árboles (--trees).")


def run_trees(nlp) -> None:
    print("\n=== Árboles de dependencias spaCy (es_core_news_sm) ===\n")
    for e in CORPUS:
        print(f"[{e['id']}] {e['text']}")
        doc = nlp(e["text"])
        for root in [t for t in doc if t.head == t]:
            print(format_spacy_tree(root, level=1))


if __name__ == "__main__":
    try:
        import nltk  # noqa: F401
    except ImportError:
        sys.exit("Falta NLTK: pip install -r requirements.txt")
    spacy_model = load_spacy()
    if spacy_model is None:
        print("[!] spaCy o el modelo es_core_news_sm no está instalado: python -m spacy download es_core_news_sm\n")
    run_table(spacy_model)
    if spacy_model and "--table" not in sys.argv:
        run_trees(spacy_model)
