# Fase 1 — Puntos de falla de la CFG al extenderla al español

## 1. Catálogo de fallas

| # | Oración | Fenómeno | Clase | Nivel | ¿Parser acepta? | Diagnóstico del parser (regla que falla) |
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

## 2. Análisis formal por fenómeno

**1. pronombre clítico** (`el gato la persigue`) — Clase A, Tipo 2.  
Regla/rasgo implicado: SV → V Obj (no hay Cl antes de V).  
Añadir SV → Cl V con rasgos (género, número, caso) mantiene la gramática libre de contexto.

**2. sujeto tácito (pro-drop)** (`come el pan`) — Clase A, Tipo 2.  
Regla/rasgo implicado: O → SN SV (el sujeto es obligatorio).  
Basta O → SV. Lo que se pierde es el SN que fijaba el número; se recupera con el rasgo del verbo. No es un límite de las CFG (el proyecto original lo afirmaba por error).

**3. coordinación nominal** (`Juan y María leen un libro`) — Clase A, Tipo 2.  
Regla/rasgo implicado: SN → PN (no existe SN → SN y SN).  
SN → SN 'y' SN con rasgo número=pl en el resultado: CF con rasgos finitos. Introduce ambigüedad.

**4. relativa de objeto (hueco)** (`la niña que el gato persigue corre`) — Clase A, Tipo 2.  
Regla/rasgo implicado: Rel → Que SV (solo hueco en el sujeto).  
Exige categorías con hueco (SV/SN, estilo GPSG): CF mientras la profundidad de huecos sea acotada.

**5. interrogativa y verbo copulativo** (`¿dónde está el gato?`) — Clase A, Tipo 2.  
Regla/rasgo implicado: 'dónde', 'está' fuera del léxico; sin regla de inversión.  
Reglas adicionales y léxico; sin dependencias no acotadas.

**6. ambigüedad por adjunción de FP** (`el hombre ve al gato con el telescopio`) — Clase B, Tipo 2 (ambigua).  
Regla/rasgo implicado: SN → Det N Adj* SP* y SV → V Obj SP*  (la FP puede colgar de SN o de SV).  
La gramática es ambigua: FIRST(SP) aparece en dos alternativas ⇒ conflicto FIRST/FOLLOW ⇒ NO es LL(1). El número de árboles crece como los números de Catalan (ver tabla).

**7. concordancia a distancia (relativa intercalada)** (`el gato que corre persiguen al ratón`) — Clase E, Tipo 2.  
Regla/rasgo implicado: concordancia sujeto–verbo.  
El parser SÍ rechaza correctamente: el rasgo número se propaga por la estructura (anidada, no cruzada). Con rasgos finitos sigue siendo libre de contexto aunque la distancia sea arbitraria.

**8. concordancia con atractor** (`los niños de la escuela duerme`) — Clase E, Tipo 2.  
Regla/rasgo implicado: concordancia sujeto–verbo.  
Rechazada correctamente: el núcleo del SN sujeto es 'niños' (pl). Un modelo puramente estadístico puede dejarse atraer por 'escuela' (sg).

**9. dependencias cruzadas (respectivamente)** (`Juan y María son rubio y morena respectivamente`) — Clase C, Tipo 1 / suavemente sensible al contexto.  
Regla/rasgo implicado: no existe una CFG que lo capture para k arbitrario.  
Patrón x1…xk y1…yk con xi~yi (copia, como {ww}). Interceptado con un lenguaje regular produce {ww}, que no es libre de contexto (lema de bombeo) ⇒ el fenómeno no es CF. Es un argumento análogo al del alemán suizo (Shieber, 1985); para el español se apoya en una idealización (k no acotado) y es discutible como hecho empírico.

**10. anomalía semántica** (`el libro come la casa`) — Clase D, —.  
Regla/rasgo implicado: ninguna (la gramática la ACEPTA).  
Las restricciones de selección ('comer' pide sujeto animado) son semánticas. Una CFG no debe resolverlas; spaCy tampoco las rechaza.

## 3. La concordancia con rasgos finitos NO sale de Tipo 2

La gramática compacta tiene 10 reglas con rasgos. Expandida a una CFG pura (cada combinación género×número×animacidad×… pasa a ser un no terminal) tiene **338 producciones**. La concordancia cuesta tamaño de gramática, no poder expresivo: por eso ‘concordancia de género y número’ no es el punto donde la CFG se rompe. El parser recursivo descendente y el ChartParser de NLTK sobre esa CFG pura aceptan las mismas oraciones (verificado en `tests/test_suite.py`).

## 4. Ambigüedad estructural (adjunción de frases preposicionales)

| Palabras | Árboles (parser propio) | Árboles (NLTK, CFG pura) |
|---|---|---|
| 8 | 2 | 2 |
| 11 | 5 | 5 |
| 14 | 14 | 14 |

Secuencia 2, 5, 14: números de Catalan. Una CFG da todas las lecturas pero no elige entre ellas; elegir exige información semántica o estadística (lo que aportan los modelos de NLP).

## 5. Conexión con el lenguaje formal

La gramática de Mini-C es LL(1) (conflictos encontrados: 0). Los paréntesis anidados exigen una pila: el lenguaje no es regular (Tipo 3) pero sí libre de contexto (Tipo 2). 
Prueba: 40 niveles de paréntesis anidados se analizan correctamente: True. El español con rasgos finitos queda también en Tipo 2; solo las dependencias cruzadas no acotadas lo exceden.
