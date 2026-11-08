# Extensión de la gramática al español: planteamiento y puntos de falla (Fase 1)

## 1. Qué se intenta
Pasar del lenguaje formal a un fragmento controlado del español **con la misma técnica** (CFG + descenso recursivo)
y observar dónde deja de bastar. Archivo: `tlp/espanol/gramatica_es.py`.

| Fenómeno | Cómo se modela | Resultado |
|---|---|---|
| **Concordancia** género/número (Det–N–Adj, sujeto–verbo) | Rasgos finitos (`gen`, `num`) comprobados al reducir | Funciona. Con rasgos finitos sigue siendo Tipo 2 |
| **Subordinación** | `SV → V Que O` (completiva: «Pedro dice que…») y `Rel → Que SV` (relativa de sujeto) | Funciona para sujeto; falla con relativa de objeto (hueco) |
| **Modificadores** | `Adj*` pospuestos, `Adv`, `SP*` (frases preposicionales) | Funciona, pero produce **ambigüedad** (PP-attachment) |
| **Sujeto explícito** | `O → SN SV` | Falla con sujeto tácito, clíticos, coordinación |

Léxico controlado: 181 formas, 3.ª persona, presente y pretérito. El léxico cerrado es una *decisión de alcance*, no una propiedad de las CFG.

## 2. Dónde colapsa (regla exacta y clase)
Se distinguen cinco clases para no confundir «mi gramática es pequeña» con «las CFG no pueden»:

- **A — falla del fragmento**: añadiendo reglas/rasgos la CFG lo cubre. Clíticos (`SV → Cl V`), pro-drop (`O → SV`), coordinación (`SN → SN y SN`), relativa de objeto (categorías con hueco), interrogativas.
- **B — límite de la técnica**: sigue siendo Tipo 2 pero ambigua ⇒ **no LL(1)** (`FIRST(SP)` en dos alternativas) y exige retroceso; árboles crecen como Catalan (2, 5, 14).
- **C — límite de la clase**: dependencias cruzadas («Juan y María son rubio y morena *respectivamente*») ≈ `{ww}`, no libre de contexto (lema de bombeo) ⇒ requiere Tipo 1 / suavemente sensible al contexto. *Es un argumento teórico (análogo a Shieber 1985 para el alemán suizo), no una demostración empírica para el español.*
- **D — fuera de la sintaxis**: «el libro come la casa» es gramatical; la anomalía es semántica.
- **E — bien manejada**: concordancia a distancia y con atractor («los niños de la escuela duerme») se rechaza correctamente.

El catálogo completo con la regla que falla en cada oración se genera con
`python -m tlp.espanol.catalogo_fallas` → `resultados/fase1_fallas.md`.

## 3. Hallazgo clave: la concordancia NO es el límite
Expandir los rasgos a una CFG pura (cada combinación género×número×animacidad×… es un no terminal) da
**338 producciones frente a 11 reglas compactas**, y el `ChartParser` de NLTK sobre esa CFG acepta exactamente lo
mismo que el parser con rasgos (`tests/test_espanol_extension.py`). La concordancia cuesta *tamaño*, no *poder expresivo*.

## 4. Script de apoyo (NLTK / spaCy) — `tlp/apoyo/contraste_nlp.py`
Para cada oración del catálogo muestra en paralelo: veredicto del parser propio, veredicto de NLTK sobre la CFG pura, y el análisis de
spaCy (raíz, sujeto, objeto, POS, dependencias, rasgos morfológicos). Observaciones del contraste:

1. **spaCy nunca rechaza**: analiza incluso `los niños de la escuela duerme`; la gramática la rechaza por la regla de concordancia.
2. **Donde la CFG falla por alcance, spaCy casi siempre da una estructura plausible** (pro-drop, coordinación, interrogativa)…
3. **…pero también puede equivocarse en silencio**: en `el gato la persigue` etiqueta *persigue* como NOUN (error real: es el verbo y `la` es un clítico). En la relativa de objeto (`la niña que el gato persigue corre`) el análisis es correcto (*que* es objeto de *persigue*, *persigue* modifica a *niña*): aquí el modelo supera a la gramática del proyecto, que no tiene categorías con hueco. Un reconocedor formal nunca produce el primer tipo de error (rechaza); un modelo estadístico sí.
4. Ante la ambigüedad de PP-attachment la CFG devuelve **todas** las lecturas; spaCy elige **una** sin indicarlo.
5. La «detección de discordancia» del script es una heurística propia (compara `Number` de sujeto y verbo), no una función de spaCy.

Limitación declarada: se usó `es_core_news_sm`; los resultados con modelos mayores pueden variar.
