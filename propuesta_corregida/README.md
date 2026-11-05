# TLP02-2026 · Fase 1 — Parser LL(1) y los límites de las CFG frente al español

Proyecto de Teoría de Lenguajes de Programación (UCA). Implementa un parser LL(1) para un
subconjunto tipo C, intenta extender la CFG al español y documenta con precisión formal dónde y
por qué falla, comparando con NLTK y spaCy.

## Estructura

| Archivo | Qué hace | Requisito del enunciado |
|---|---|---|
| `formal_parser.py` | Lexer + parser descendente recursivo LL(1) → AST. Errores con línea/columna y recuperación en modo pánico | Parser formal que produce árbol y maneja errores |
| `ll1_analysis.py` | Calcula anulables, FIRST, FOLLOW y la tabla M[A,a]; verifica que no hay conflictos | Gramática bien definida / conexión con teoría |
| `ll1_table_parser.py` | Parser LL(1) dirigido por tabla → árbol de derivación concreto (+ export Graphviz) | Árbol de análisis sintáctico |
| `spanish_parser.py` | CFG del español (concordancia, relativa y completiva, adjetivos, adverbios, PP); enumera **todas** las derivaciones; genera la CFG explícita y el corpus etiquetado | Extensión de la CFG al español + puntos de falla |
| `chomsky_limits.py` | Demostración ejecutable: dependencias anidadas (CFG) vs cruzadas (fuera de CFG) | Conexión con la jerarquía de Chomsky |
| `nlp_demo.py` | Tabla comparativa CFG propia vs NLTK (chart parser) vs spaCy sobre el mismo corpus | Demo con NLTK/spaCy |
| `spanish_ll1_conflicts.py` | Prueba que la CFG del español NO es LL(1): 5 conflictos, 3 genuinos tras factorizar (adjunción de PP/adverbio) | Análisis formal de los puntos de falla |
| `test.py` | 31 pruebas: válidas, inválidas, LL(1), equivalencia de parsers, corpus del español, verificación cruzada con NLTK | Conjunto de pruebas |

## Instalación

Requiere Python 3.9 o superior.

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows

pip install -r requirements.txt
python -m spacy download es_core_news_sm
```

NLTK no necesita descargar corpus: solo se usa su `ChartParser`.

## Cómo ejecutar

```bash
python formal_parser.py          # entrada válida (AST) + entrada inválida (varios errores)
python ll1_analysis.py           # FIRST / FOLLOW / tabla y veredicto LL(1)
python ll1_table_parser.py       # árbol de derivación concreto de "int x = 2 + 3 * 4;"
python spanish_parser.py         # corpus de 17 oraciones: aciertos, rechazos y ambigüedad
python spanish_ll1_conflicts.py  # conflictos LL(1) de la gramática del español
python chomsky_limits.py         # límite CFG: concordancia cruzada
python nlp_demo.py               # tabla comparativa + árboles de dependencias de spaCy
python nlp_demo.py --table       # solo la tabla
python -m unittest test -v       # suite completa
```

Para dibujar el árbol de derivación: `ll1_parse(src).to_dot()` y luego `dot -Tpng arbol.dot -o arbol.png`
(requiere Graphviz instalado).

## Resultados de referencia (para verificar tu instalación)

* `python -m unittest test` → `Ran 31 tests ... OK`.
* `python ll1_analysis.py` → `Conflictos: 0  =>  la gramática ES LL(1).` (70 celdas en la tabla).
* `python nlp_demo.py --table`: CFG con concordancia = 41 no terminales / 63 reglas estructurales / 72 léxicas;
  sin concordancia = 16 / 21 / 70. Oraciones D1, D2, D3 → 2, 2 y 4 derivaciones.

Probado con Python 3.13, NLTK 3.10, spaCy 3.8 y `es_core_news_sm` 3.8.0.

## Corpus de Fase 1 (`spanish_parser.CORPUS`)

* **A (6)**: aceptadas correctamente.  **B (3)**: agramaticales rechazadas correctamente.
* **C (5)**: español válido que la CFG rechaza (falsos negativos): sujeto tácito, adjetivo antepuesto,
  inversión V-S, coordinación, vocabulario abierto.
* **D (3)**: aceptadas pero con más de una derivación (ambigüedad de adjunción de PP).

## Limitaciones conocidas

* El léxico es finito (72 palabras) y solo hay verbos en 3.ª persona; es deliberado para aislar los fenómenos.
* El `ChartParser` de NLTK se usa como verificador independiente de la CFG propia, no como "NLP moderno"; el
  componente estadístico de la comparación es spaCy.
* `es_core_news_sm` es un modelo pequeño: comete errores visibles (p. ej. etiqueta `veloz` como sujeto en C2).
