# Control de cambios y justificación técnica

Referencia: PDF "Proyecto TLP02-2026" (Fase 1 y Fase 2) y criterios de evaluación (correctitud 35 %, profundidad 30 %, rigor experimental 20 %, presentación 15 %).
"Original" = el repositorio `TLP02-2026-PROYECTO` tal como estaba (formal_parser.py, spanish_parser.py, nlp_demo.py, test.py, README.md, info.txt).

| # | Dónde | Qué se modificó o agregó | Motivo técnico (deficiencia original → corrección) |
|---|---|---|---|
| 1 | `formal_parser.py` · lexer | `re.findall` → `tokenizar()` con error de carácter ilegal, línea y columna | El original **descartaba en silencio** los caracteres no reconocidos: `x = 2 + $ 3` se aceptaba. Violaba "rechaza correctamente entradas inválidas" (correctitud). |
| 2 | `formal_parser.py` · gramática | Se agregan `int`, `if/else`, `while`, `print`, bloques, `-`, `/`, comparaciones y negación unaria | El original solo parseaba `ID = Expr` con `+ * ( )`. El PDF pide un subconjunto de un lenguaje de programación (p. ej. aritmético "con estructuras de control"). |
| 3 | `formal_parser.py` · árbol | Diccionarios ad hoc → clase `Node` (paréntesis, ASCII, `to_nltk`, PNG) | El PDF exige "producir un árbol de análisis sintáctico"; un dict anidado no es un árbol de derivación visualizable. |
| 4 | `formal_parser.py` · errores | `ErrorSintactico(línea, col)`, mensajes por regla, recuperación en modo pánico | El original lanzaba `SyntaxError` con el token pero sin posición; "manejar errores sintácticos básicos". |
| 5 | `formal_parser.py` · `verificar_ll1()` | Cálculo de FIRST/FOLLOW y detección de conflictos sobre la BNF real | Se afirmaba "LL(1)" sin demostrarlo. Ahora es verificable (0 conflictos). Llaves obligatorias eliminan el *else* colgante. |
| 6 | `spanish_parser.py` → `spanish_cfg.py` · léxico | 14 palabras → 181 formas con género, número, tiempo, subcategoría y animacidad | El original no tenía verbos plurales (cualquier sujeto plural fallaba), adjetivos femeninos ni adverbios; no permitía "vocabulario suficiente" ni un set variado. |
| 7 | `spanish_cfg.py` · gramática | Se agregan adverbios, frases preposicionales, 2 tiempos, intransitivos, *a personal*, relativas de sujeto y completivas | El PDF exige SVO, modificadores (adj, adv, FP), ≥2 tiempos y al menos una subordinada. El original solo tenía `DET N ADJ? V DET N`; `que` estaba en el léxico sin ninguna regla. |
| 8 | `spanish_cfg.py` · parser | Recorrido determinista → descendente recursivo con retroceso (generadores) que devuelve todas las derivaciones | Permite medir la ambigüedad estructural (2, 5, 14 árboles) y reportar la regla exacta que falla, que es lo que pide la actividad "identificar la regla que falla". |
| 9 | `fase1_limites.py`, `PROPUESTA_CORREGIDA.md` §4 | **Corrección conceptual**: sujeto tácito y subordinadas ya no se presentan como límites de la CFG | El original (comentarios en `spanish_parser.py`, `test.py` e `info.txt`) decía que son "inválidos en CFG". Es falso: `O → SV` y `Rel → Que SV` son reglas libres de contexto; fallaba el *alcance del fragmento*. Un docente de TLP lo detectaría (profundidad 30 %). |
| 10 | `fase1_limites.py` | Catálogo de 10 fenómenos clasificados (A fragmento / B técnica / C clase / D semántica / E bien manejada) con nivel de Chomsky | La actividad pide "regla que falla, clase de fenómeno y nivel de la jerarquía de Chomsky". El original no lo documentaba. |
| 11 | `spanish_cfg.cfg_nltk()` + tests | CFG pura expandida (338 producciones) y prueba de equivalencia con el ChartParser de NLTK | Demuestra con datos que la concordancia con rasgos finitos sigue siendo libre de contexto (el punto formal clave); valida el parser contra una implementación independiente. |
| 12 | `arbol.py` | Dibujo de árboles con matplotlib (PNG), sin Graphviz | Fase 2 exige "árboles de análisis sintáctico visuales". El original no visualizaba nada. |
| 13 | `dataset/test_set.csv` | 4 oraciones → 71 oraciones en 3 niveles (20/25/26) con `gramatical_es`, salida esperada, fenómeno y tripleta S-V-O | Fase 2 exige ≥60 oraciones en tres niveles con salida esperada. |
| 14 | `comparacion_nlp.py` | Precisión, cobertura, F1, rechazo correcto, clasificación de errores (FP, FN, etiquetado), exactitud S-V-O, UPOS, ms/oración; tablas y 2 gráficas; spaCy sm y md en modo crudo y +concordancia | Fase 2 exige métricas cuantitativas y "conclusiones respaldadas por datos"; el original solo imprimía tokens de spaCy (rigor experimental 20 %). |
| 15 | `nlp_demo.py` | Imprime parser propio y spaCy lado a lado; modelo `md` | El PDF pide procesar "las mismas oraciones" y evidenciar la diferencia; el original solo mostraba spaCy. |
| 16 | `llm_experimento.py` | Prompts zero-shot y few-shot con reglas y léxico, logs JSONL, métricas de desviación hacia el español | Fase 2 exige el experimento con LLM (a, b, c) y los logs. Ausente en el original. **Ejecución real pendiente** (requiere API key). |
| 17 | `test.py` → `tests/test_suite.py` | 5 → 17 pruebas (12 válidos + 13 inválidos Mini-C, veredicto de las 71 oraciones, concordancias, ambigüedad, equivalencia NLTK, PNG, pipeline LLM simulado) | "Definir un conjunto de pruebas que demuestre que funciona y rechaza"; el original tenía 1 válido y 1 inválido formal. |
| 18 | `README.md`, `requirements.txt` | Instalación completa, cómo correr cada demo/experimento, estructura | El README original solo instalaba spaCy y no decía cómo ejecutar nada; el PDF exige "README que explique cómo ejecutar el código". |
| 19 | `PROPUESTA_CORREGIDA.md` | Informe técnico con marco teórico, gramáticas, análisis formal, metodología, resultados, amenazas a la validez | El PDF exige informe 5–7 pp (F1) y 7–10 pp (F2); el repo solo tenía `info.txt`, un guion de presentación. |
| 20 | `info.txt` | No se modifica (queda como guion); sus afirmaciones sobre sujeto tácito/subordinada deben corregirse con el punto 9 antes de exponer | Evita defender en vivo una afirmación formalmente incorrecta. |

## Pendiente (no resuelto por esta corrección)
- Ejecutar `llm_experimento.py` con API key y volcar los resultados en la sección 10 del informe.
- Ejecutar la comparación con HuggingFace en una máquina con acceso al Hub (opcional según el PDF: "al menos dos herramientas").
- Ajustar el informe al formato/extensión que exija la cátedra y preparar la presentación (15–20 min) con demo en vivo.
- Fase 1 vencía el 2-nov y sus presentaciones fueron el 3 y 5-nov; confirmar con el docente el estado de esa entrega.
