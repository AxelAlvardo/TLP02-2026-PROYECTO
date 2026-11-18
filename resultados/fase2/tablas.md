# Fase 2 — Parser propio vs spaCy vs HuggingFace

Conjunto de prueba: 71 oraciones (56 gramaticales y 15 agramaticales según `gramatical_es`). Entre corchetes, intervalo de confianza del 95 % (Wilson). «—» = el sistema no produce ese dato (las categorías del parser propio salen del léxico, que es la referencia).

- spaCy 3.8.18, modelo es_core_news_sm 3.8.0
- HuggingFace transformers 5.23.0 (torch 2.15.0), modelo wietsedv/xlm-roberta-base-ft-udpos28-es

## Aceptación y rechazo

| Sistema | TP | FP | FN | TN | Precisión | Cobertura | F1 | Rechazo correcto |
|---|---|---|---|---|---|---|---|---|
| Parser propio (CFG) | 37 | 0 | 19 | 15 | 100.0% [90.6–100.0] | 66.1% [53.0–77.1] | 79.6% | 100.0% [79.6–100.0] |
| spaCy sm (crudo) | 56 | 15 | 0 | 0 | 78.9% [68.0–86.8] | 100.0% [93.6–100.0] | 88.2% | 0.0% [0.0–20.4] |
| spaCy sm + concordancia | 48 | 3 | 8 | 12 | 94.1% [84.1–98.0] | 85.7% [74.3–92.6] | 89.7% | 80.0% [54.8–93.0] |
| HuggingFace + reglas | 54 | 12 | 2 | 3 | 81.8% [70.9–89.3] | 96.4% [87.9–99.0] | 88.5% | 20.0% [7.0–45.2] |

## Clasificación de errores y etiquetado

| Sistema | Falsos positivos | Falsos negativos | Errores de etiquetado S-V-O | Errores de etiquetado de categorías | Exactitud S-V-O | Exactitud de categorías | ms/oración |
|---|---|---|---|---|---|---|---|
| Parser propio (CFG) | 0 | 19 | 0 | — | 84.1% | — | 0.01 |
| spaCy sm (crudo) | 15 | 0 | 3 | 3 | 93.2% | 98.7% (41 oraciones) | 1.28 |
| spaCy sm + concordancia | 3 | 8 | 1 | 1 | 90.9% | 98.7% (41 oraciones) | 1.28 |
| HuggingFace + reglas | 12 | 2 | — | 0 | — | 98.7% (41 oraciones) | 22.61 |
