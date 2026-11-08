# Informe técnico — Fase 1
## Gramáticas formales y lenguaje natural: los límites de la CFG frente al español

**Curso:** Teoría de Lenguajes de Programación (TLP02-2026) · **Proyecto:** Fase 1 · **Integrantes:** _por completar por el grupo_

> **Resumen.** Se implementó un parser descendente recursivo LL(1) para *Mini-C*, un subconjunto de C, con árbol de análisis y errores con línea y columna, y se verificó con 25 programas de prueba más pruebas unitarias. Luego se intentó extender la misma técnica a un fragmento controlado del español (concordancia, subordinación, modificadores) y se documentó cada punto de falla distinguiendo cuatro cosas: la regla que no se escribió, el vocabulario ausente, la ambigüedad y el límite de clase. La conclusión central es que **la concordancia de género y número no es el punto de ruptura de las CFG** (cuesta tamaño de gramática, no poder expresivo); los límites reales son la cobertura abierta, la ambigüedad —que una CFG enumera pero no resuelve— y, solo como argumento teórico, las dependencias cruzadas no acotadas.

---

## 1. Marco teórico

### 1.1 La jerarquía de Chomsky
| Tipo | Gramática | Reconocedor | Ejemplo relevante |
|---|---|---|---|
| 3 | Regular | Autómata finito | Identificadores, números, palabras reservadas (el lexer de Mini-C) |
| 2 | Libre de contexto (CFG) | Autómata de pila | Paréntesis anidados, expresiones, bloques `{ }` (el parser de Mini-C) |
| 1 | Sensible al contexto | Autómata linealmente acotado | {ww}, {aⁿbⁿcⁿ}, copia/concordancia cruzada |
| 0 | Sin restricciones | Máquina de Turing | Cualquier lenguaje recursivamente enumerable |

Cada clase contiene estrictamente a la anterior (Chomsky, 1956, 1959). Un compilador usa Tipo 3 para el análisis léxico y Tipo 2 para el sintáctico; las restricciones de contexto (declarar antes de usar, tipos) se verifican en la fase semántica, no en la gramática.

### 1.2 Lenguajes formales frente a lenguaje natural
| Dimensión | Lenguaje de programación | Español |
|---|---|---|
| Estructura | Definida por una gramática única y cerrada | Descrita *a posteriori*; léxico abierto y en cambio |
| Ambigüedad | Se elimina por diseño (precedencia, llaves obligatorias) | Estructural y léxica; es normal, no un defecto |
| Recursividad | Anidamiento explícito (paréntesis, bloques) | Subordinación y modificación recursivas (*dice que ana piensa que…*) |
| Dependencias de contexto | Fuera de la gramática (fase semántica) | Concordancia género/número, concordancia a distancia, correferencia |
| Gramaticalidad | Binaria: la entrada pertenece o no al lenguaje | Graduada y dependiente del contexto y del hablante |

### 1.3 Qué sí y qué no pueden hacer las CFG
- **La concordancia con rasgos finitos sigue siendo libre de contexto.** Si género ∈ {m, f} y número ∈ {sg, pl} son rasgos finitos, cada combinación se puede convertir en un no terminal distinto; la gramática crece, pero no sale de Tipo 2.
- **La ambigüedad** no excede a las CFG, pero las vuelve no LL(1) y obliga a retroceso o a algoritmos tabulares (CYK, Earley, `ChartParser`).
- **Las dependencias cruzadas no acotadas** sí excederían a las CFG. El lenguaje de copia {ww} no es libre de contexto; intersectado con el regular a\*b\*a\*b\* da {aⁱbʲaⁱbʲ}, que tampoco lo es por el lema de bombeo, y las CFG se cierran bajo intersección con regulares. Shieber (1985) usó este tipo de argumento con el alemán suizo; Bresnan et al. (1982) lo discutieron para el neerlandés. Joshi (1985) propuso que el lenguaje natural es «suavemente sensible al contexto», un nivel entre Tipo 2 y Tipo 1.

**Hipótesis de trabajo:** un fragmento controlado y finito del español cabe en una CFG con rasgos finitos; los obstáculos prácticos son cobertura y ambigüedad, y el obstáculo de clase es teórico y requiere idealizar (k ilimitado).

---

## 2. Parser formal: Mini-C

**Subconjunto.** Declaraciones (`int x;`, `int x = e;`), asignación, `if / else`, `while`, `print(e);`, bloques, expresiones con `+ - * /`, paréntesis y negación unaria, comparaciones y comentarios `//`. Las llaves son obligatorias en `if` y `while`, lo que elimina el «else colgante».

**Gramática.** La BNF completa, la forma EBNF y la tabla FIRST/FOLLOW están en el [Anexo A](01_gramatica_minic.md). Se escribió sin recursión izquierda y factorizada (`Expr → Term ExprR`, `ExprR → + Term ExprR | − Term ExprR | ε`, …). `verificar_ll1()` calcula FIRST y FOLLOW sobre el mismo diccionario que usa el parser y confirma **0 conflictos**, de modo que la gramática documentada y la implementada no pueden divergir.

**Implementación** (`tlp/formal/`). Lexer por expresiones regulares donde un carácter ilegal es un error, nunca se descarta; parser con una función por no terminal y lookahead de un token; los bucles `ExprR`/`TermR` se colapsan en nodos binarios asociativos por la izquierda, de modo que `8 − 3 − 2` produce `(8 − 3) − 2`.

**Árbol y errores.** `analizar(código)` devuelve un árbol de análisis (`Node`: bracket, indentado, diccionario, PNG). Los errores indican línea y columna, por ejemplo `Línea 2, col 8: se esperaba número, variable, '(' o '-' pero llegó ';'`. Con `recuperar=True` hay recuperación en modo pánico (sincroniza en `;` o `}`) y se reportan varios errores a la vez.

**Pruebas.** (i) 12 programas válidos y 13 inválidos, almacenados como archivos en `casos/formal/`; cada inválido declara el fragmento de mensaje esperado. (ii) Pruebas unitarias de precedencia, asociatividad izquierda, pertenencia del `else` al `if` más cercano, anidamiento de 200 niveles de paréntesis, posición de errores multilínea, carácter ilegal y recuperación. Todas pasan.

**Relación con Chomsky.** Los paréntesis anidados exigen memoria de pila; Mini-C no es regular pero sí libre de contexto (Tipo 2). Por eso el parser es un autómata de pila implícito (la pila de llamadas).

---

## 3. Intento de extensión al español

Se aplicó la **misma técnica** (CFG + descenso recursivo, aquí con retroceso mediante generadores para obtener todas las derivaciones) a un fragmento controlado (`tlp/espanol/gramatica_es.py`): léxico de **181 formas**, tercera persona, presente y pretérito perfecto simple, sujeto explícito. La gramática compacta tiene **10 reglas**.

| Fenómeno exigido | Cómo se modela | Resultado |
|---|---|---|
| Concordancia género/número (Det–N–Adj; sujeto–verbo) | Rasgos finitos `gen`, `num` comprobados al reducir; un Adj concuerda con su N | Funciona, incluida la concordancia a distancia y con atractor |
| Cláusula subordinada | `SV → V Que O` (completiva: *Pedro dice que Ana piensa que el gato duerme*) y `Rel → Que SV` (relativa de sujeto) | Funciona para sujeto; no cubre la relativa de objeto |
| Modificadores | `Adj*` pospuestos, `Adv`, `SP*` (frases preposicionales) | Funciona, pero genera ambigüedad de adjunción |

**Una CFG pura equivalente.** Expandiendo los rasgos a no terminales se obtiene una CFG sin rasgos de **338 producciones**. El `ChartParser` de NLTK sobre ella acepta exactamente las mismas oraciones que el parser con rasgos (`tests/test_espanol_extension.py`) y, en las tres oraciones de §4.1, da el mismo número de árboles. Esto sustenta la hipótesis de trabajo: la concordancia cuesta *tamaño* (10 reglas frente a 338), no *poder expresivo*.

---

## 4. Análisis formal de los puntos de falla

Un parser que rechaza una oración puede hacerlo por razones muy distintas. Para no confundir «mi gramática es pequeña» con «las CFG no pueden» se clasifica cada fenómeno (catálogo ejecutable: `python -m tlp.espanol.catalogo_fallas`):

- **A — falla del fragmento.** La regla no está escrita o falta vocabulario; añadirla mantiene Tipo 2.
- **B — límite de la técnica.** Sigue siendo Tipo 2 pero ambigua; no LL(1).
- **C — límite de la clase.** No libre de contexto (solo como argumento teórico).
- **D — fuera de la sintaxis.** Anomalía semántica.
- **E — bien manejada.** La gramática resuelve el fenómeno.

| # | Oración | Fenómeno | Clase | Regla / rasgo implicado | Qué demuestra **la ejecución** |
|---|---|---|---|---|---|
| 1 | `el gato la persigue` | pronombre clítico | A | `SV → V Obj` (falta `SV → Cl V`) | Rechazo por regla ausente |
| 2 | `come el pan` | sujeto tácito | A | `O → SN SV` (basta `O → SV`) | Rechazo por regla ausente |
| 3 | `Juan y María leen un libro` | coordinación nominal | A | `SN → SN y SN` no existe | Rechazo por **léxico** («y» ausente): no prueba nada sobre CFG |
| 4 | `la niña que el gato persigue corre` | relativa de objeto | A | `Rel → Que SV` (falta categoría con hueco) | Rechazo por regla ausente |
| 5 | `¿dónde está el gato?` | interrogativa | A | sin inversión ni copulativo | Rechazo por **léxico**: no prueba nada sobre CFG |
| 6 | `el hombre ve al gato con el telescopio` | adjunción de FP | B | `SN → Det N Adj* SP*` y `SV → V Obj SP*` | Acepta con **2 árboles**: la ambigüedad sí se observa |
| 7 | `el gato que corre persiguen al ratón` | concordancia a distancia | E | concordancia sujeto–verbo | Rechazo correcto por la regla de concordancia |
| 8 | `los niños de la escuela duerme` | concordancia con atractor | E | concordancia sujeto–verbo | Rechazo correcto por la regla de concordancia |
| 9 | `Juan y María son rubio y morena respectivamente` | dependencias cruzadas | C (teórico) | ninguna regla llega a aplicarse | Rechazo por **léxico** (6 palabras fuera del léxico) |
| 10 | `el libro come la casa` | anomalía semántica | D | restricción de selección (semántica) | Acepta con 1 árbol |

**Lo que demuestra la ejecución, y lo que no.** Un rechazo por vocabulario ausente (3, 5, 9) o por una regla que simplemente no se escribió (1, 2, 4) **no** demuestra que una CFG sea insuficiente: todos esos casos son ampliables dentro de Tipo 2. Las filas 6, 7, 8 y 10 sí muestran un comportamiento de la gramática ejecutada que sustenta una afirmación.

### 4.1 Ambigüedad estructural (clase B, ejecutable)
La oración de la fila 6 admite dos lecturas (*con el telescopio* modifica a *ve* o a *gato*). Al encadenar frases preposicionales el número de árboles es 2, 5 y 14 para 8, 11 y 14 palabras —números de Catalan—, y el parser propio y NLTK coinciden en los tres casos. Con `SN → Det N Adj* SP*` y `SV → V Obj SP*`, `FIRST(SP)` aparece en dos alternativas que compiten, lo cual es un conflicto LL(1) por construcción de la gramática (argumento sobre las reglas; el parser español usa retroceso y no una tabla LL(1)). Una CFG entrega *todas* las lecturas pero no elige: elegir exige información semántica o estadística.

### 4.2 Dependencias cruzadas: «respectivamente» (clase C, **argumento teórico**)
**Qué hizo la ejecución.** Rechazar la oración de la fila 9 por seis palabras ausentes del léxico. Eso no tiene valor probatorio: añadiendo `y`, `son`, `rubio`, `morena` y `respectivamente` y la regla correspondiente, una CFG puede aceptar esa oración concreta.

**Qué sostiene el argumento teórico.** Con k pares el patrón es x₁…xₖ y₁…yₖ con cada xᵢ concordando con yᵢ, estructura cruzada análoga a la copia {ww}. Como {ww} ∩ a\*b\*a\*b\* = {aⁱbʲaⁱbʲ} no es libre de contexto (lema de bombeo) y las CFG se cierran bajo intersección con regulares, el fenómeno **para k ilimitado** no sería libre de contexto. Dos salvedades: (1) para k acotado (p. ej. k ≤ 2) basta una CFG con reglas explícitas; ninguna oración corta de prueba puede refutar a las CFG; (2) que el español natural requiera k ilimitado es una idealización, no un hecho empírico establecido. La relación con la jerarquía es, por tanto: *si* se acepta la idealización, el fenómeno exige más que Tipo 2 (en la propuesta de Joshi, suave sensibilidad al contexto); con k acotado permanece en Tipo 2.

### 4.3 Resumen de los puntos de falla
La CFG con rasgos del proyecto falla *prácticamente* por **cobertura** (clase A) y **ambigüedad** (B); resuelve la **concordancia** (E); y la **única** fuente de insuficiencia de clase (C) es un argumento teórico que depende de una idealización.

---

## 5. Contraste con NLTK y spaCy

Las mismas diez oraciones se procesaron con tres analizadores (`python -m tlp.apoyo.contraste_nlp`, resultados en `resultados/contraste_nlp.md`).

**5.1 NLTK (reproducible sin descargar modelos).** NLTK se usó como motor CFG independiente sobre la gramática expandida sin rasgos. Coincide con el parser propio en las diez oraciones (acepta las filas 6 y 10, rechaza las otras ocho) y da el mismo número de árboles. Esto contrasta *dos formulaciones de la misma clase de gramática*; **no** es un analizador estadístico, y NLTK no puede analizar aquí nada que la CFG no cubra.

**5.2 spaCy (opcional; ejecutado el 7-nov-2026 con spaCy 3.8.18 y `es_core_news_sm` 3.8.0).** Es la comparación frente a un modelo estadístico; se genera solo si el modelo está instalado (de lo contrario el informe de resultados lo declara «no generada»).

| # | Oración | Parser propio | spaCy: raíz / sujeto / objeto |
|---|---|---|---|
| 1 | `el gato la persigue` | RECHAZA | persigue/**NOUN** / gato / — |
| 2 | `come el pan` | RECHAZA | come/VERB / — / pan |
| 3 | `Juan y María leen un libro` | RECHAZA | leen/VERB / Juan / libro |
| 4 | `la niña que el gato persigue corre` | RECHAZA | corre/VERB / niña / que |
| 5 | `¿dónde está el gato?` | RECHAZA | está/VERB / gato / — |
| 6 | `el hombre ve al gato con el telescopio` | ACEPTA (2 árboles) | ve/VERB / hombre / gato |
| 7 | `el gato que corre persiguen al ratón` | RECHAZA | persiguen/VERB / gato / — |
| 8 | `los niños de la escuela duerme` | RECHAZA | duerme/VERB / niños / — |
| 9 | `Juan y María son rubio y morena respectivamente` | RECHAZA | rubio/ADJ / Juan / — |
| 10 | `el libro come la casa` | ACEPTA (1 árbol) | come/VERB / libro / casa |

Observaciones, **limitadas a estas 10 oraciones y a este modelo pequeño**:
1. spaCy no rechaza ninguna oración; analiza incluso las agramaticales de las filas 7 y 8. Para spaCy no existe «fuera del lenguaje», solo la mejor estimación. Una heurística propia (comparar el rasgo `Number` de sujeto y verbo raíz) sí marca la discordancia de las filas 7 y 8; no es una función de spaCy.
2. Donde el parser propio falla por alcance (filas 2–5) spaCy entrega una estructura plausible; en la fila 4 el análisis es correcto (*que* es objeto de *persigue*), con lo que supera a la gramática del proyecto.
3. spaCy también puede equivocarse sin avisar: en la fila 1 etiqueta *persigue* como sustantivo. Un reconocedor formal rechaza; un modelo estadístico adivina.
4. Ante la ambigüedad de la fila 6 la CFG devuelve las dos lecturas; spaCy elige una sin indicar que había otra.

---

## 6. Conclusiones y limitaciones

1. Una CFG LL(1) basta para un subconjunto de un lenguaje de programación, y su rechazo de entradas inválidas es total y localizable (línea y columna).
2. La concordancia de género y número no es el límite: se resuelve con rasgos finitos dentro de Tipo 2, a costa de tamaño (10 reglas frente a 338 producciones).
3. Los obstáculos observables son la cobertura abierta y la ambigüedad; la insuficiencia de clase depende del argumento de dependencias cruzadas con k ilimitado, que es teórico.
4. Un modelo estadístico y una CFG responden preguntas distintas: reconocer pertenencia frente a producir la mejor estructura.

**Limitaciones declaradas.** El español cubre un fragmento controlado (181 formas, tercera persona), no es un parser general; parte del rechazo de lo que queda fuera es por construcción. La comparación con spaCy usa un único modelo pequeño y diez oraciones. No se evaluó rendimiento cuantitativo (eso corresponde a la Fase 2). Queda pendiente la presentación oral con demostración en vivo.

---

## 7. Reproducibilidad y formato

Instalación y ejecución: ver `README.md`. Todos los números de este informe salen de `python run_fase1.py` (pruebas, catálogo, contraste, árboles). **Formato:** el documento está en Markdown, que no tiene paginación propia. Medición realizada el 7-nov-2026: convertido con `pandoc informe.md -o informe.docx` y exportado a PDF con LibreOffice tras fijar A4, Calibri 11 pt, márgenes de 2,5 cm y tablas a 9 pt, resultó en **6 páginas** (referencias incluidas, sin contar el Anexo A). Con otras fuentes o márgenes el resultado varía; el grupo debe revisar la paginación en su exportación final y ajustar para quedar entre 5 y 7 páginas.

### Referencias
- Chomsky, N. (1956). *Three models for the description of language*. IRE Transactions on Information Theory, 2(3).
- Chomsky, N. (1959). *On certain formal properties of grammars*. Information and Control, 2(2).
- Bresnan, J., Kaplan, R., Peters, S. y Zaenen, A. (1982). *Cross-serial dependencies in Dutch*. Linguistic Inquiry, 13(4).
- Shieber, S. (1985). *Evidence against the context-freeness of natural language*. Linguistics and Philosophy, 8.
- Joshi, A. (1985). *Tree adjoining grammars: how much context-sensitivity is required to provide reasonable structural descriptions?* En Dowty, Karttunen y Zwicky (eds.), Natural Language Parsing. Cambridge University Press.
- Aho, A., Lam, M., Sethi, R. y Ullman, J. (2006). *Compilers: Principles, Techniques, and Tools* (2.ª ed.). Addison-Wesley.
- Bird, S., Klein, E. y Loper, E. (2009). *Natural Language Processing with Python*. O'Reilly (NLTK).
- Honnibal, M. et al. spaCy: industrial-strength NLP in Python (software, spacy.io).
