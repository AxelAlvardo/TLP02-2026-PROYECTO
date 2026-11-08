# Fase 1 — Contraste: parser propio (CFG) vs NLTK vs spaCy

## 1. Parser propio vs NLTK (siempre reproducible, sin descargar modelos)

NLTK actúa como motor CFG independiente sobre la gramática expandida sin rasgos. Lo que muestra: (a) que la concordancia con rasgos finitos sigue siendo libre de contexto (ambos aceptan exactamente lo mismo) y (b) TODAS las lecturas de una oración ambigua. Lo que NO muestra: capacidad de análisis estadístico; NLTK aquí tampoco puede analizar nada que la CFG no cubra.

| # | Oración | Fenómeno (clase) | Parser propio | NLTK (CFG pura) |
|---|---|---|---|---|
| 1 | `el gato la persigue` | pronombre clítico (A) | RECHAZA | RECHAZA |
| 2 | `come el pan` | sujeto tácito (pro-drop) (A) | RECHAZA | RECHAZA |
| 3 | `Juan y María leen un libro` | coordinación nominal (A) | RECHAZA | RECHAZA |
| 4 | `la niña que el gato persigue corre` | relativa de objeto (hueco) (A) | RECHAZA | RECHAZA |
| 5 | `¿dónde está el gato?` | interrogativa y verbo copulativo (A) | RECHAZA | RECHAZA |
| 6 | `el hombre ve al gato con el telescopio` | ambigüedad por adjunción de FP (B) | ACEPTA | ACEPTA (2 árbol/es) |
| 7 | `el gato que corre persiguen al ratón` | concordancia a distancia (relativa intercalada) (E) | RECHAZA | RECHAZA |
| 8 | `los niños de la escuela duerme` | concordancia con atractor (E) | RECHAZA | RECHAZA |
| 9 | `Juan y María son rubio y morena respectivamente` | dependencias cruzadas (respectivamente) (C) | RECHAZA | RECHAZA |
| 10 | `el libro come la casa` | anomalía semántica (D) | ACEPTA | ACEPTA (1 árbol/es) |

## 2. spaCy (opcional)

Ejecutado con spaCy 3.8.18, modelo es_core_news_sm 3.8.0. spaCy siempre produce un análisis; la columna de discordancia compara el rasgo Number del sujeto y del verbo raíz y es una heurística PROPIA, no una función de spaCy.

| # | Oración | spaCy: raíz / sujeto / objeto | ¿Discordancia (heurística)? |
|---|---|---|---|
| 1 | `el gato la persigue` | persigue/NOUN / gato / — | no |
| 2 | `come el pan` | come/VERB / — / pan | no |
| 3 | `Juan y María leen un libro` | leen/VERB / Juan / libro | no |
| 4 | `la niña que el gato persigue corre` | corre/VERB / niña / que | no |
| 5 | `¿dónde está el gato?` | está/VERB / gato / — | no |
| 6 | `el hombre ve al gato con el telescopio` | ve/VERB / hombre / gato | no |
| 7 | `el gato que corre persiguen al ratón` | persiguen/VERB / gato / — | SÍ |
| 8 | `los niños de la escuela duerme` | duerme/VERB / niños / — | SÍ |
| 9 | `Juan y María son rubio y morena respectivamente` | rubio/ADJ / Juan / — | no |
| 10 | `el libro come la casa` | come/VERB / libro / casa | no |

**Lectura** (sobre estas 10 oraciones y este modelo, sin generalizar). Donde el parser propio rechaza por alcance (clítico, pro-drop, coordinación, relativa de objeto, interrogativa), spaCy igualmente entrega una estructura: no existe la noción de «fuera del lenguaje». En `el gato la persigue` esa estructura es incorrecta (*persigue* etiquetado como NOUN); en la relativa de objeto es correcta. Ante la ambigüedad de adjunción spaCy elige una sola lectura sin indicarlo. Las discordancias (filas 7 y 8) la gramática las rechaza por construcción; spaCy las analiza como si fueran gramaticales.
