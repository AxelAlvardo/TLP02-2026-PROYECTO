"""nlp_demo.py - Demo en vivo: la misma oración con el parser propio y con spaCy (Fase 1, última actividad).

Uso:  python nlp_demo.py                       # oraciones representativas
      python nlp_demo.py "la niña que el gato persigue corre"
"""
import sys

from spanish_cfg import ParserEspanol, extraer_svo

DEFECTO = [
    "el gato negro persigue al ratón",              # dentro de la gramática
    "los niños duerme",                             # error de concordancia
    "come el pan",                                  # sujeto tácito
    "la niña que el gato persigue corre",           # relativa de objeto
    "el hombre ve al gato con el telescopio",       # ambigüedad
]


def main():
    import spacy
    nlp = spacy.load("es_core_news_md")
    parser = ParserEspanol()
    for o in (sys.argv[1:] and [" ".join(sys.argv[1:])]) or DEFECTO:
        print("=" * 78, f"\nORACIÓN: {o}")
        arbol, diag = parser.parse(o)
        print("PARSER PROPIO (CFG):", f"ACEPTA {extraer_svo(arbol)}" if arbol else f"RECHAZA — {diag}")
        doc = nlp(o)
        print("spaCy es_core_news_md:")
        for t in doc:
            print(f"   {t.text:10} POS={t.pos_:6} DEP={t.dep_:10} padre={t.head.text:10} {t.morph}")


if __name__ == "__main__":
    main()
