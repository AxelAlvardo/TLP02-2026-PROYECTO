# Fase 2 — Comparación de los enfoques sobre el corpus de prueba

Generado por `python -m tlp.espanol.evaluar` a partir de los logs de `resultados/fase2/logs/` (no vuelve a correr ningún sistema). Corpus: 71 oraciones; 56 son español correcto (`gramatical_es`) y 37 las deriva la gramática (`esperado_gramatica`). Entre corchetes, intervalo de confianza del 95 % (Wilson). «—» = el sistema no produce ese dato.

## Enfoques, versiones y parámetros

| Sistema | Log | Versión y parámetros |
|---|---|---|
| Parser propio (CFG) | `parser.jsonl` | parser propio (tlp/espanol/gramatica_es.py) |
| spaCy sm (crudo) | `spacy_sm_crudo.jsonl` | spaCy 3.8.18, modelo es_core_news_sm 3.8.0 |
| spaCy sm + concordancia | `spacy_sm_concordancia.jsonl` | spaCy 3.8.18, modelo es_core_news_sm 3.8.0 |
| HuggingFace + reglas | `huggingface.jsonl` | HuggingFace transformers 5.23.0 (torch 2.15.0), modelo wietsedv/xlm-roberta-base-ft-udpos28-es |
| LLM sin ejemplos | `llm_sin_ejemplos.jsonl` | gemini · modelo gemini-3.5-flash-lite (la API reporta: gemini-3.5-flash-lite) · SDK google-genai 3.4.0 · temperature = 0 · max_tokens = 4096 · prompt `casos/espanol/prompts/sin_ejemplos.txt` · 71 llamadas entre 2026-11-18T10:26:37.128-06:00 y 2026-11-18T10:35:17.386-06:00 |
| LLM zero-shot | `llm_zero_shot.jsonl` | gemini · modelo gemini-3.5-flash-lite (la API reporta: gemini-3.5-flash-lite) · SDK google-genai 3.4.0 · temperature = 0 · max_tokens = 4096 · prompt `casos/espanol/prompts/zero_shot.txt` · 71 llamadas entre 2026-11-18T10:45:20.656-06:00 y 2026-11-18T10:52:18.634-06:00 |
| LLM few-shot | `llm_few_shot.jsonl` | gemini · modelo gemini-3.5-flash-lite (la API reporta: gemini-3.5-flash-lite) · SDK google-genai 3.4.0 · temperature = 0 · max_tokens = 4096 · prompt `casos/espanol/prompts/few_shot.txt` · 71 llamadas entre 2026-11-18T10:52:59.507-06:00 y 2026-11-18T11:00:00.688-06:00 |
| LLM combinado | `llm_combinado.jsonl` | gemini · modelo gemini-3.5-flash-lite (la API reporta: gemini-3.5-flash-lite) · SDK google-genai 3.4.0 · temperature = 0 · max_tokens = 4096 · prompt `casos/espanol/prompts/combinado.txt` · 71 llamadas entre 2026-11-18T11:49:19.241-06:00 y 2026-11-18T11:54:36.279-06:00 |

## Aceptación y rechazo — referencia: español correcto (`gramatical_es`)

Positivo = la oración es español correcto. Mide qué tan lejos llega cada enfoque frente al español real.

| Sistema | Oraciones | TP | FP | FN | TN | Sin respuesta | Precisión | Cobertura | F1 | Rechazo correcto |
|---|---|---|---|---|---|---|---|---|---|---|
| Parser propio (CFG) | 71 | 37 | 0 | 19 | 15 | — | 100.0% [90.6–100.0] | 66.1% [53.0–77.1] | 79.6% | 100.0% [79.6–100.0] |
| spaCy sm (crudo) | 71 | 56 | 15 | 0 | 0 | — | 78.9% [68.0–86.8] | 100.0% [93.6–100.0] | 88.2% | 0.0% [0.0–20.4] |
| spaCy sm + concordancia | 71 | 48 | 3 | 8 | 12 | — | 94.1% [84.1–98.0] | 85.7% [74.3–92.6] | 89.7% | 80.0% [54.8–93.0] |
| HuggingFace + reglas | 71 | 54 | 12 | 2 | 3 | — | 81.8% [70.9–89.3] | 96.4% [87.9–99.0] | 88.5% | 20.0% [7.0–45.2] |
| LLM sin ejemplos | 71 | 37 | 0 | 19 | 15 | 0 | 100.0% [90.6–100.0] | 66.1% [53.0–77.1] | 79.6% | 100.0% [79.6–100.0] |
| LLM zero-shot | 71 | 37 | 0 | 19 | 15 | 0 | 100.0% [90.6–100.0] | 66.1% [53.0–77.1] | 79.6% | 100.0% [79.6–100.0] |
| LLM few-shot | 71 | 37 | 0 | 19 | 15 | 0 | 100.0% [90.6–100.0] | 66.1% [53.0–77.1] | 79.6% | 100.0% [79.6–100.0] |
| LLM combinado | 71 | 37 | 0 | 19 | 15 | 0 | 100.0% [90.6–100.0] | 66.1% [53.0–77.1] | 79.6% | 100.0% [79.6–100.0] |

## Aceptación y rechazo — referencia: gramática (`esperado_gramatica`)

Positivo = la gramática deriva la oración. Mide si el enfoque respeta las reglas formales (el parser propio coincide con esta referencia por construcción).

| Sistema | Oraciones | TP | FP | FN | TN | Sin respuesta | Precisión | Cobertura | F1 | Rechazo correcto |
|---|---|---|---|---|---|---|---|---|---|---|
| Parser propio (CFG) | 71 | 37 | 0 | 0 | 34 | — | 100.0% [90.6–100.0] | 100.0% [90.6–100.0] | 100.0% | 100.0% [89.8–100.0] |
| spaCy sm (crudo) | 71 | 37 | 34 | 0 | 0 | — | 52.1% [40.7–63.3] | 100.0% [90.6–100.0] | 68.5% | 0.0% [0.0–10.2] |
| spaCy sm + concordancia | 71 | 36 | 15 | 1 | 19 | — | 70.6% [57.0–81.3] | 97.3% [86.2–99.5] | 81.8% | 55.9% [39.5–71.1] |
| HuggingFace + reglas | 71 | 36 | 30 | 1 | 4 | — | 54.5% [42.6–66.0] | 97.3% [86.2–99.5] | 69.9% | 11.8% [4.7–26.6] |
| LLM sin ejemplos | 71 | 35 | 2 | 2 | 32 | 0 | 94.6% [82.3–98.5] | 94.6% [82.3–98.5] | 94.6% | 94.1% [80.9–98.4] |
| LLM zero-shot | 71 | 35 | 2 | 2 | 32 | 0 | 94.6% [82.3–98.5] | 94.6% [82.3–98.5] | 94.6% | 94.1% [80.9–98.4] |
| LLM few-shot | 71 | 35 | 2 | 2 | 32 | 0 | 94.6% [82.3–98.5] | 94.6% [82.3–98.5] | 94.6% | 94.1% [80.9–98.4] |
| LLM combinado | 71 | 35 | 2 | 2 | 32 | 0 | 94.6% [82.3–98.5] | 94.6% [82.3–98.5] | 94.6% | 94.1% [80.9–98.4] |

## Desviación de las reglas formales — referencia: gramática

Qué hace cada enfoque con lo que la gramática rechaza: si lo acepta siendo español correcto, se desvía hacia el conocimiento general del español; si lo acepta siendo agramatical, acepta algo que ni la gramática ni el español admiten.

| Sistema | Coincide con la gramática | Acepta lo que la gramática rechaza: español correcto (desviación hacia el español) | Acepta lo que la gramática rechaza: agramatical | Rechaza lo que la gramática deriva (sobre-rechazo) | Sin respuesta |
|---|---|---|---|---|---|
| Parser propio (CFG) | 71/71 | 0 | 0 | 0 | — |
| spaCy sm (crudo) | 37/71 | 19 | 15 | 0 | — |
| spaCy sm + concordancia | 55/71 | 12 | 3 | 1 | — |
| HuggingFace + reglas | 40/71 | 18 | 12 | 1 | — |
| LLM sin ejemplos | 67/71 | 2 | 0 | 2 | 0 |
| LLM zero-shot | 67/71 | 2 | 0 | 2 | 0 |
| LLM few-shot | 67/71 | 2 | 0 | 2 | 0 |
| LLM combinado | 67/71 | 2 | 0 | 2 | 0 |

## Clasificación de errores

Los errores de etiquetado se cuentan en las oraciones que son español correcto y que el sistema acepta.

| Sistema | FP (español) | FN (español) | FP (gramática) | FN (gramática) | Errores de etiquetado S-V-O | Errores de etiquetado de categorías | Exactitud S-V-O | Exactitud de categorías | ms/oración |
|---|---|---|---|---|---|---|---|---|---|
| Parser propio (CFG) | 0 | 19 | 0 | 0 | 0 | — | 84.1% | — | 0.01 |
| spaCy sm (crudo) | 15 | 0 | 34 | 0 | 3 | 3 | 93.2% | 98.7% (41 oraciones) | 1.27 |
| spaCy sm + concordancia | 3 | 8 | 15 | 1 | 1 | 1 | 90.9% | 98.7% (41 oraciones) | 1.27 |
| HuggingFace + reglas | 12 | 2 | 30 | 1 | — | 0 | — | 98.7% (41 oraciones) | 24.54 |
| LLM sin ejemplos | 0 | 19 | 2 | 2 | 4 | — | 75.0% | — | 7419.82 |
| LLM zero-shot | 0 | 19 | 2 | 2 | 3 | — | 77.3% | — | 5956.41 |
| LLM few-shot | 0 | 19 | 2 | 2 | 0 | — | 84.1% | — | 5948.87 |
| LLM combinado | 0 | 19 | 2 | 2 | 0 | — | 84.1% | — | 4550.47 |
