# Compiladores (LL1) vs. NLP en Español (Versión Simplificada)

Demostración minimalista de cómo un parser **LL(1)** analiza lenguajes de programación sin ambigüedad, pero falla al intentar procesar el idioma español en comparación con **spaCy**.

## Instalación

```bash
pip install spacy
python -m spacy download es_core_news_sm