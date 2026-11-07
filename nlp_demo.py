import spacy
from spanish_parser import ORACIONES

nlp = spacy.load("es_core_news_sm")

print("=== Análisis con NLP Moderno (spaCy) ===")
for oracion in ORACIONES:
    doc = nlp(oracion)
    print(f"\nOración: '{oracion}'")
    for token in doc:
        # Muestra: Palabra -> Categoría Gramatical (Función Sintáctica) <- Palabra Padre
        print(f"  {token.text:10} | POS: {token.pos_:6} | Dep: {token.dep_:8} | Padre: {token.head.text}")