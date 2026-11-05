"""
Módulo 3: Procesamiento de Lenguaje Natural Moderno (spaCy / NLTK).
Procesa las mismas oraciones que hacen colapsar a la CFG rígida, resolviendo
ambigüedades, sujeto tácito, vocabulario abierto y adjunción preposicional.
"""

from typing import List
from spanish_parser import TEST_SENTENCES


def format_spacy_tree(token, level: int = 0) -> str:
    """Construye una representación jerárquica del árbol de dependencias de spaCy."""
    indent = "  " * level
    morph = f" [{token.morph}]" if str(token.morph) else ""
    line = f"{indent}└── {token.text} (POS: {token.pos_}, Dep: {token.dep_}){morph}\n"
    for child in token.children:
        line += format_spacy_tree(child, level + 1)
    return line


def run_spacy_pipeline(sentences: List[str]) -> bool:
    """Intenta ejecutar el análisis sintáctico utilizando spaCy."""
    try:
        import spacy
        nlp = spacy.load("es_core_news_sm")
    except (ImportError, OSError):
        return False

    print("=== Análisis Sintáctico de Dependencias con spaCy (es_core_news_sm) ===\n")
    for idx, sent in enumerate(sentences, 1):
        print(f"Oración {idx}: '{sent}'")
        doc = nlp(sent)
        roots = [token for token in doc if token.head == token]
        for root in roots:
            print(format_spacy_tree(root, level=1))
    return True


def run_nltk_fallback(sentences: List[str]):
    """
    Mecanismo de respaldo con NLTK (ChartParser probabilístico/tolerante a ambigüedad)
    en caso de que el entorno local no tenga instalado el modelo es_core_news_sm de spaCy.
    """
    import nltk
    from nltk import CFG, ChartParser

    print("=== Análisis Sintáctico con NLTK ChartParser (Modo Respaldo) ===\n")
    print("Nota: Usando gramática flexible con soporte para recursión, PP-attachment múltiple y pro-drop.\n")

    grammar_str = """
    S -> NP VP | VP
    NP -> DET N | DET N ADJ | DET ADJ N | DET N PP | DET N RC | N
    VP -> V | V NP | V PP | V NP PP
    PP -> PREP NP
    RC -> REL VP | REL NP V
    DET -> 'el' | 'la' | 'los' | 'las' | 'un' | 'una'
    N -> 'gato' | 'gatos' | 'ratón' | 'parque' | 'perro' | 'aves' | 'colina' | 'niña' | 'telescopio'
    ADJ -> 'negro' | 'negros' | 'veloz'
    V -> 'persigue' | 'observa' | 've' | 'corre'
    PREP -> 'a' | 'en' | 'desde' | 'con'
    REL -> 'que'
    """
    grammar = CFG.fromstring(grammar_str)
    parser = ChartParser(grammar)

    for idx, sent in enumerate(sentences, 1):
        print(f"Oración {idx}: '{sent}'")
        words = [w.lower() for w in sent.split()]
        trees = list(parser.parse(words))
        if trees:
            print(f"  [ÉXITO NLP] Se encontraron {len(trees)} árbol(es) sintáctico(s) válido(s) (manejo de ambigüedad):")
            for t in trees[:2]:  # Mostrar hasta 2 interpretaciones en caso de ambigüedad estructural
                print(t.pformat(margin=70))
            print()
        else:
            print("  [Aviso] Oración requiere análisis de dependencias neuronales (instale spaCy).\n")


def analyze_sentences(sentences: List[str] = TEST_SENTENCES):
    if not run_spacy_pipeline(sentences):
        print("[!] spaCy o el modelo 'es_core_news_sm' no detectado. Ejecutando motor NLTK...\n")
        run_nltk_fallback(sentences)


if __name__ == "__main__":
    analyze_sentences()