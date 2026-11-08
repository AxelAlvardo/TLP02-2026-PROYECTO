# Fase 1 — Contraste: parser propio (CFG) vs NLTK vs spaCy

Modelo spaCy: `es_core_news_sm`. La columna «spaCy» siempre produce un análisis; la heurística de discordancia compara el rasgo Number del sujeto y del verbo raíz (es una verificación propia, no una función de spaCy).

| # | Oración | Fenómeno (clase) | Parser propio | NLTK (CFG pura) | spaCy: raíz / sujeto / objeto | ¿Detecta discordancia? |
|---|---|---|---|---|---|---|
| 1 | `el gato la persigue` | pronombre clítico (A) | RECHAZA | RECHAZA | persigue/NOUN / gato / — | no |
| 2 | `come el pan` | sujeto tácito (pro-drop) (A) | RECHAZA | RECHAZA | come/VERB / — / pan | no |
| 3 | `Juan y María leen un libro` | coordinación nominal (A) | RECHAZA | RECHAZA | leen/VERB / Juan / libro | no |
| 4 | `la niña que el gato persigue corre` | relativa de objeto (hueco) (A) | RECHAZA | RECHAZA | corre/VERB / niña / que | no |
| 5 | `¿dónde está el gato?` | interrogativa y verbo copulativo (A) | RECHAZA | RECHAZA | está/VERB / gato / — | no |
| 6 | `el hombre ve al gato con el telescopio` | ambigüedad por adjunción de FP (B) | ACEPTA | ACEPTA (2 árbol/es) | ve/VERB / hombre / gato | no |
| 7 | `el gato que corre persiguen al ratón` | concordancia a distancia (relativa intercalada) (E) | RECHAZA | RECHAZA | persiguen/VERB / gato / — | SÍ |
| 8 | `los niños de la escuela duerme` | concordancia con atractor (E) | RECHAZA | RECHAZA | duerme/VERB / niños / — | SÍ |
| 9 | `Juan y María son rubio y morena respectivamente` | dependencias cruzadas (respectivamente) (C) | RECHAZA | RECHAZA | rubio/ADJ / Juan / — | no |
| 10 | `el libro come la casa` | anomalía semántica (D) | ACEPTA | ACEPTA (1 árbol/es) | come/VERB / libro / casa | no |

**Lectura.** Donde el parser propio RECHAZA (clítico, pro-drop, coordinación, relativa de objeto, interrogativa, dependencias cruzadas) spaCy igualmente entrega una estructura: no hay noción de «fuera del lenguaje», solo la mejor estimación. A la inversa, donde la CFG acepta con ambigüedad (PP-attachment) devuelve todas las lecturas sin elegir, mientras spaCy elige una sola. Las discordancias (filas 7 y 8) las rechaza la gramática por construcción; spaCy las analiza como si fueran gramaticales salvo que se añada una verificación externa.
