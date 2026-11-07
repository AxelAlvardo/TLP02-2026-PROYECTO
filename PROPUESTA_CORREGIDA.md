# Proyecto TLP02-2026 — Propuesta corregida
**Gramáticas formales y lenguaje natural: experimentando los límites de la jerarquía de Chomsky**

> Estado al 7-nov-2026. Todas las cifras de este documento salen de ejecuciones reales del código incluido
> (`python comparacion_nlp.py`, `python -m unittest discover -s tests`). Lo que NO se ha podido ejecutar está marcado como **PENDIENTE**.

## 0. Resumen ejecutivo

El proyecto estudia dónde una gramática libre de contexto (CFG) deja de bastar para el español. Se construyen
(1) un parser LL(1)/descendente recursivo para *Mini-C* (Fase 1) y (2) un parser con retroceso para un fragmento controlado del
español que genera árboles visuales (Fases 1 y 2), y se mide cuantitativamente contra spaCy y un LLM.

Hallazgo central, respaldado por datos y por análisis formal: **la concordancia de género y número no es lo que rompe la CFG**.
Con rasgos finitos es libre de contexto (la CFG pura equivalente tiene 338 producciones frente a 11 reglas compactas) y el parser la
resuelve con precisión 100 % y rechazo correcto 100 %. Lo que le cuesta a la CFG es (a) la **ambigüedad estructural** (2, 5 y 14 árboles para
1, 2 y 3 frases preposicionales: números de Catalan), (b) la **cobertura** (66,1 % global; 9,5 % en el nivel 3) porque cada fenómeno nuevo exige reglas
nuevas, y (c) las **dependencias cruzadas** (*respectivamente*), que no son libres de contexto en el caso general.

## 1. Objetivos y alcance

| Fase | Peso | Qué se entrega |
|---|---|---|
| 1 (40 %) | vencimiento 2-nov | Parser Mini-C, extensión al español, análisis formal de fallas, demo con spaCy, informe 5–7 pp |
| 2 (60 %) | vencimiento 17-nov | Gramática del español, parser con árboles visuales, set de 71 oraciones, métricas, spaCy/HuggingFace, experimento con LLM, informe 7–10 pp |

## 2. Marco teórico

- **Jerarquía de Chomsky.** Tipo 3 (regulares, autómatas finitos) ⊂ Tipo 2 (libres de contexto, autómatas de pila) ⊂ Tipo 1 (sensibles al contexto) ⊂ Tipo 0.
  Los paréntesis anidados de un lenguaje de programación exigen una pila: Tipo 2. El parser lo demuestra (200 niveles de anidamiento en `tests/test_suite.py`).
- **LL(1).** Una gramática es LL(1) si para cada no terminal los conjuntos FIRST de sus alternativas son disjuntos y, si alguna es anulable, no chocan con FOLLOW.
  `formal_parser.verificar_ll1()` lo calcula sobre la gramática real y devuelve 0 conflictos.
- **Formal vs natural.** Estructura (CF en lenguajes de programación, no determinista en español), **ambigüedad** (ausente por diseño en C; sistemática en español),
  **recursividad** (relativas, completivas), **dependencias de contexto** (concordancia), **concordancia** (finita ⇒ CF; cruzada y no acotada ⇒ no CF).
- **Rasgos finitos y CFG.** Un rasgo con dominio finito (género×número) se elimina multiplicando no terminales (`SN_f_pl`). Cuesta tamaño, no poder expresivo.
  `spanish_cfg.cfg_nltk()` hace esa expansión y los tests comprueban que el ChartParser de NLTK sobre la CFG pura acepta exactamente lo mismo que el parser recursivo.

## 3. Fase 1 — Parser formal (Mini-C)

Gramática BNF completa en `formal_parser.GRAMATICA` (13 no terminales). Cubre declaraciones, asignaciones, `if/else`, `while`, `print`, bloques, `+ - * /`, negación,
paréntesis y comparaciones. Llaves obligatorias ⇒ no existe el *else* colgante. Las cadenas `ExprR/TermR` se pliegan en nodos binarios asociativos por la izquierda
(se conserva la jerarquía de precedencia `Expr → Term → Factor`).

- **Árbol:** clase `Node` (`bracket()`, `indentado()`, `to_nltk()`, PNG con `arbol.dibujar_arbol`).
- **Errores:** `ErrorSintactico(línea, columna)`; un carácter ilegal es error (antes se descartaba en silencio); modo recuperación en pánico que informa varios errores.
- **Pruebas:** 12 programas válidos y 13 inválidos, precedencia, asociatividad, estructura `if/else`, recuperación, error en línea 2 columna 8, anidamiento de 200 niveles.

## 4. Fase 1 — Extensión al español y puntos de falla

Se extiende la CFG con concordancia Det–N, N–Adj y sujeto–verbo, relativas de sujeto, completivas y modificadores. El análisis distingue **cinco clases** de falla
(A fragmento, B técnica, C clase, D semántica, E bien manejada). Catálogo generado por `fase1_limites.py`:

| | Oración | Fenómeno | Clase | Nivel | ¿Parser acepta? | Diagnóstico del parser (regla que falla) |
|---|---|---|---|---|---|---|
| 1 | `el gato la persigue` | pronombre clítico | A | Tipo 2 | NO | falla en la posición 2 ('la'), regla «SV → V …»: se esperaba un verbo y llegó 'la' |
| 2 | `come el pan` | sujeto tácito (pro-drop) | A | Tipo 2 | NO | falla en la posición 0 ('come'), regla «SN → Det N | PN»: se esperaba un determinante o nombre propio y llegó 'come' |
| 3 | `Juan y María leen un libro` | coordinación nominal | A | Tipo 2 | NO | palabra(s) fuera del léxico: y |
| 4 | `la niña que el gato persigue corre` | relativa de objeto (hueco) | A | Tipo 2 | NO | falla en la posición 3 ('el'), regla «SV → V …»: se esperaba un verbo y llegó 'el' |
| 5 | `¿dónde está el gato?` | interrogativa y verbo copulativo | A | Tipo 2 | NO | palabra(s) fuera del léxico: dónde, está |
| 6 | `el hombre ve al gato con el telescopio` | ambigüedad por adjunción de FP | B | Tipo 2 (ambigua) | SÍ | 2 derivación(es) |
| 7 | `el gato que corre persiguen al ratón` | concordancia a distancia (relativa intercalada) | E | Tipo 2 | NO | falla en la posición 4 ('persiguen'), regla «concordancia sujeto–verbo»: 'persiguen' es pl pero el sujeto es sg |
| 8 | `los niños de la escuela duerme` | concordancia con atractor | E | Tipo 2 | NO | falla en la posición 5 ('duerme'), regla «concordancia sujeto–verbo»: 'duerme' es sg pero el sujeto es pl |
| 9 | `Juan y María son rubio y morena respectivamente` | dependencias cruzadas (respectivamente) | C | Tipo 1 / suavemente sensible al contexto | NO | palabra(s) fuera del léxico: y, son, rubio, y, morena, respectivamente |
| 10 | `el libro come la casa` | anomalía semántica | D | — | SÍ | 1 derivación(es) |

Clases: A = falla del fragmento (la CFG podría cubrirlo) · B = límite de la técnica (ambigüedad, no LL(1)) · C = límite de la clase (no libre de contexto) · D = fuera de la sintaxis · E = bien manejada: la gramática la resuelve correctamente.

**Lectura formal.**
1. *Clíticos, sujeto tácito, coordinación, relativas de objeto, interrogativas* son **libres de contexto**: fallan por alcance del fragmento, no por la clase de lenguaje.
   El proyecto original afirmaba lo contrario para el sujeto tácito y las subordinadas; ambas afirmaciones eran incorrectas (`O → SV` y `Rel → Que SV` son reglas CF triviales).
2. *Adjunción de frases preposicionales* es CF pero **ambigua** y viola LL(1): `SP*` aparece en `SN` y en `SV`, así que FIRST(SP) ⊆ FOLLOW(SN). Hay que usar retroceso, un parser tabular o preferencias estadísticas.
3. *Concordancia a distancia y con atractor* se resuelve bien con rasgos propagados por la estructura (dependencias anidadas, no cruzadas).
4. *Dependencias cruzadas* (`Juan y María son rubio y morena respectivamente`): el patrón x₁…xₖ y₁…yₖ con xᵢ~yᵢ es una copia; intersectado con un lenguaje regular da {ww}, que no es CF (lema de bombeo).
   Es un argumento análogo al de Shieber (1985) para el alemán suizo; en español depende de idealizar k sin cota, así que es un argumento teórico, no un resultado empírico.
   (En la ejecución, el parser rechaza esa oración por léxico fuera de alcance; la no-CF-idad es argumento formal, no algo que la ejecución demuestre.)
5. *Anomalías semánticas* (`el libro come la casa`) son sintácticamente correctas: la gramática las acepta y está bien que lo haga.

## 5. Fase 2 — Gramática del español

Reglas (idénticas a las que recibe el LLM, `spanish_cfg.REGLAS_BNF`):

```
\
O    -> SN SV                       [el número de SN y de V deben coincidir]
SN   -> PN
SN   -> Det N Adj* SP* Rel?         [Det y N concuerdan en género y número; cada Adj concuerda con N]
SP   -> P SN
Rel  -> Que SV                      [relativa de sujeto; el verbo concuerda en número con el SN antecedente]
SV   -> V Adv? SP*                  [V intransitivo (intr)]
SV   -> V Adv? Obj Adv? SP*         [V transitivo (tr); los dos Adv son opcionales]
SV   -> V Que O                     [V de tipo "comp" (decir, pensar)]
Obj  -> SN                          [solo si el núcleo de SN es no animado (n) o animal (a)]
Obj  -> A SN                        [A = la palabra "a"; solo si el núcleo es humano (h), animal (a) o PN; un objeto humano EXIGE esta forma]
Reglas de léxico: Det, N, PN, Adj, V, Adv, P, Que se reescriben en las palabras del léxico.
Restricciones: solo 3.ª persona; tiempos presente y pretérito; sujeto SIEMPRE explícito;
"al" = "a el" y "del" = "de el" (se separan antes de analizar); no hay coordinación, clíticos, negación,
interrogativas, pasivas, ni verbos copulativos.
```

Léxico: 181 formas (sustantivos con género/número/animacidad, nombres propios, adjetivos de 4 y 2 terminaciones, 15 verbos × 2 tiempos × 2 números con
subcategoría `tr/intr/comp`, adverbios, preposiciones). La *a personal* se modela con el rasgo de animacidad del núcleo del objeto.
Implementación: descendente recursivo con retroceso mediante generadores, que entrega **todas** las derivaciones (así se mide la ambigüedad). Árboles visuales en `resultados/arboles/`.

## 6. Conjunto de prueba

71 oraciones en `dataset/test_set.csv`: **20 de nivel 1** (simples, deben aceptarse), **25 de nivel 2** (15 con modificadores/relativas/completivas/ambigüedad y 10 agramaticales por concordancia u orden),
**26 de nivel 3** (fenómenos que exceden el fragmento: sujeto tácito, clíticos, coordinación, pasivas, subjuntivo, comparativas, dependencias cruzadas, dos anomalías semánticas, y 5 agramaticales con discordancia a distancia).
Cada fila lleva `gramatical_es` (juicio lingüístico), `esperado_gramatica` (salida esperada del parser), fenómeno y tripleta esperada (sujeto, verbo, objeto).

## 7. Metodología de comparación

Referencia: `gramatical_es`. Positivo = "oración gramatical aceptada". Precisión = TP/(TP+FP); cobertura = TP/(TP+FN); rechazo correcto = TN/(TN+FP);
exactitud estructural = tripleta (S,V,O) correcta sobre las 44 oraciones evaluables (una oración rechazada cuenta como error); error de etiquetado = aceptada con tripleta incorrecta;
exactitud UPOS = etiqueta gramatical correcta frente al léxico en las oraciones del fragmento. Lemas normalizados con el léxico propio para igualar criterios.
spaCy nunca rechaza, por eso se evalúa en dos modos: **crudo** (acepta siempre) y **+concordancia** (rechaza si la raíz no es verbo o falla el número/género que el propio modelo predice; es una heurística nuestra, no una función de spaCy).

## 8. Resultados (ejecución real)

### Métricas globales (71 oraciones)

| Sistema | TP | FP | FN | TN | Precisión | Cobertura | F1 | Rechazo correcto | Exactitud estructural (S,V,O) | Err. etiquetado | UPOS | ms/oración |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Parser propio (CFG) | 37 | 0 | 19 | 15 | 100.0% | 66.1% | 79.6% | 100.0% | 84.1% | 0 | — | 0.02 |
| spaCy sm (crudo) | 56 | 15 | 0 | 0 | 78.9% | 100.0% | 88.2% | 0.0% | 93.2% | 3 | 99.0% | 3.43 |
| spaCy sm + concordancia | 48 | 3 | 8 | 12 | 94.1% | 85.7% | 89.7% | 80.0% | 90.9% | 1 | 99.0% | 3.43 |
| spaCy md (crudo) | 56 | 15 | 0 | 0 | 78.9% | 100.0% | 88.2% | 0.0% | 95.5% | 2 | 99.5% | 3.75 |
| spaCy md + concordancia | 51 | 2 | 5 | 13 | 96.2% | 91.1% | 93.6% | 86.7% | 95.5% | 0 | 99.5% | 3.75 |

### Por nivel de complejidad

| Sistema | Nivel | TP | FP | FN | TN | Cobertura | Rechazo correcto |
|---|---|---|---|---|---|---|---|
| Parser propio (CFG) | 1 | 20 | 0 | 0 | 0 | 100.0% | — |
| Parser propio (CFG) | 2 | 15 | 0 | 0 | 10 | 100.0% | 100.0% |
| Parser propio (CFG) | 3 | 2 | 0 | 19 | 5 | 9.5% | 100.0% |
| spaCy sm (crudo) | 1 | 20 | 0 | 0 | 0 | 100.0% | — |
| spaCy sm (crudo) | 2 | 15 | 10 | 0 | 0 | 100.0% | 0.0% |
| spaCy sm (crudo) | 3 | 21 | 5 | 0 | 0 | 100.0% | 0.0% |
| spaCy sm + concordancia | 1 | 20 | 0 | 0 | 0 | 100.0% | — |
| spaCy sm + concordancia | 2 | 14 | 1 | 1 | 9 | 93.3% | 90.0% |
| spaCy sm + concordancia | 3 | 14 | 2 | 7 | 3 | 66.7% | 60.0% |
| spaCy md (crudo) | 1 | 20 | 0 | 0 | 0 | 100.0% | — |
| spaCy md (crudo) | 2 | 15 | 10 | 0 | 0 | 100.0% | 0.0% |
| spaCy md (crudo) | 3 | 21 | 5 | 0 | 0 | 100.0% | 0.0% |
| spaCy md + concordancia | 1 | 20 | 0 | 0 | 0 | 100.0% | — |
| spaCy md + concordancia | 2 | 14 | 0 | 1 | 10 | 93.3% | 100.0% |
| spaCy md + concordancia | 3 | 17 | 2 | 4 | 3 | 81.0% | 60.0% |

Gráficas: `resultados/grafica_metricas.png`, `resultados/grafica_por_nivel.png`. Detalle de cada error: `resultados/errores_detalle.csv`.

## 9. Análisis

- **Rigor frente a cobertura.** El parser propio no tiene falsos positivos (precisión y rechazo correcto de 100 %), pero su cobertura es de 66,1 %: acepta 20/20 en nivel 1, 15/15 de las válidas del nivel 2 y solo 2/21 del nivel 3.
  Es el compromiso esperable de una gramática cerrada. Parte de ese 100 % de rechazo es por construcción (las oraciones agramaticales usan solo errores que la gramática modela): es una cota, no una garantía.
- **Robustez.** spaCy cubre el 100 % pero, en modo crudo, acepta las 15 oraciones agramaticales (rechazo 0 %). Con la heurística de concordancia sube el rechazo a 80 % (sm) y 86,7 % (md), a costa de falsos negativos: su raíz es un adjetivo en las copulativas (convención de UD) y un sustantivo en dos relativas mal analizadas.
  Los dos modelos de spaCy fallaron la tripleta en `la gata que duerme come el pan` y `el gato que duerme en la casa que Juan compró come el pan` (tomaron el sustantivo como raíz): el parser formal acierta ambas.
  spaCy md no rechaza `los niños que duerme corren` ni `el gato persigue al ratón con con`.
- **Ambigüedad.** El parser enumera 2, 5 y 14 derivaciones (números de Catalan); spaCy devuelve una sola lectura sin avisar de las demás. La gramática por sí sola no puede desambiguar.
- **Escalabilidad.** La CFG pura equivalente tiene 338 producciones frente a 11 compactas; añadir persona (1.ª/2.ª/3.ª), modo y clíticos multiplica ese número. Los modelos estadísticos incorporan léxico nuevo sin reescribir reglas.
- **Costo computacional.** Parser propio ≈ 0,02 ms/oración; spaCy ≈ 3,4–3,8 ms/oración (CPU, sin GPU, medido en este entorno; sirve para el orden de magnitud, no como benchmark). El parser propio necesita un léxico escrito a mano; spaCy necesita descargar un modelo.
- **Aplicabilidad.** CFG: lenguajes de programación y dominios controlados (validación estricta, explicaciones por regla). Modelos estadísticos: texto libre. Un diseño híbrido es razonable.

## 10. Experimento con LLM (diseño listo, ejecución PENDIENTE)

`llm_experimento.py` entrega al LLM las reglas BNF y el léxico, y le pide analizar cada oración "siguiendo estrictamente esas reglas" (zero-shot) y con 6 ejemplos resueltos (few-shot; los ejemplos no están en el set de prueba).
Se registra prompt y respuesta cruda de cada llamada en `resultados/llm_logs.jsonl` y se calcula: (a) acuerdo con el parser (oráculo de la gramática), **desviación hacia el español** (acepta lo que la gramática rechaza pero es español correcto), (b) aciertos/fallos por nivel y (c) mejora few-shot vs zero-shot.
Requiere `ANTHROPIC_API_KEY`; **no se ejecutó contra una API real** (no había credenciales en el entorno de desarrollo): el pipeline de construcción de prompts y análisis está probado con un LLM simulado en `tests/test_suite.py` (ese resultado simulado no debe citarse).
Hipótesis a contrastar: el nivel 3 concentrará las desviaciones (19 oraciones de nivel 3 son correctas en español y la gramática las rechaza); few-shot debería reducirlas.

## 11. Amenazas a la validez y limitaciones

- Set pequeño (71 oraciones) y etiquetado por el propio grupo; el nivel 3 está diseñado para exceder la gramática, por lo que la cobertura del parser propio es baja *por diseño*.
- Las dos "herramientas modernas" ejecutadas son dos modelos de **spaCy** (sm y md). La comparación con **HuggingFace** está implementada (`--hf-model`, solo etiquetado UPOS) pero **no se ejecutó**: el entorno de desarrollo no tenía acceso a huggingface.co.
  Ejecútenla localmente antes del informe final o indiquen la limitación.
- "spaCy + concordancia" es una heurística nuestra y condiciona sus cifras de rechazo.
- Tiempos medidos en una sola máquina y una sola corrida.

## 12. Conclusiones respaldadas por los datos

1. Un parser recursivo descendente con rasgos finitos resuelve la concordancia del fragmento sin errores de aceptación (0 FP, 15/15 rechazos), y es equivalente a una CFG pura de 338 reglas.
2. La limitación real de la CFG no es la concordancia sino la **cobertura abierta** (66,1 % global, 9,5 % en nivel 3), la **ambigüedad** (2→5→14 derivaciones) y las **dependencias cruzadas**.
3. Los modelos neuronales dan cobertura total, pero sin noción de agramaticalidad: rechazo 0 % en modo crudo; con una heurística simple llega a 80–86,7 % y aparecen errores propios (relativas).
4. Falta cerrar la evidencia sobre LLMs (sección 10) y HuggingFace (sección 11).

## 13. Cómo reproducir

Ver `README.md`.
