# Respuestas del LLM — gemini / gemini-4-hydrogen

- Fecha: 2026-11-17 20:03
- Prompt: `casos/espanol/prompt_llm.txt` con 6 ejemplos resueltos (0 = zero-shot)
- Oraciones analizadas: 5

## Resumen

Referencia: lo que acepta la gramática (veredicto del parser propio).

| Resultado | Oraciones |
|---|---|
| Coincide con la gramática | 5/5 |
| Desviación hacia el español (acepta lo que la gramática rechaza, pero es español correcto) | 0 |
| Aceptó una oración agramatical | 0 |
| Sobre-rechazo (rechaza lo que la gramática deriva) | 0 |
| Sin respuesta válida | 0 |

## Prompt usado

### Sistema

````text
Eres un analizador sintáctico FORMAL. Aplicas ÚNICAMENTE la gramática y el léxico que se te dan. No uses tu conocimiento general del español: si una oración es correcta en español pero la gramática no puede derivarla, debes RECHAZARLA; si la gramática la deriva aunque suene rara, debes ACEPTARLA. Responde SOLO con un objeto JSON.
````

### Usuario (la marca {oracion} se reemplaza por cada oración)

````text
GRAMÁTICA:
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

LÉXICO (forma:rasgos):
P: a con de en para por sobre
V: abre:pres,sg,tr abren:pres,pl,tr abrieron:pret,pl,tr abrió:pret,sg,tr canta:pres,sg,intr cantan:pres,pl,intr cantaron:pret,pl,intr cantó:pret,sg,intr come:pres,sg,tr comen:pres,pl,tr comieron:pret,pl,tr comió:pret,sg,tr compra:pres,sg,tr compran:pres,pl,tr compraron:pret,pl,tr compró:pret,sg,tr corre:pres,sg,intr corren:pres,pl,intr corrieron:pret,pl,intr corrió:pret,sg,intr dice:pres,sg,comp dicen:pres,pl,comp dijeron:pret,pl,comp dijo:pret,sg,comp duerme:pres,sg,intr duermen:pres,pl,intr durmieron:pret,pl,intr durmió:pret,sg,intr escribe:pres,sg,tr escriben:pres,pl,tr escribieron:pret,pl,tr escribió:pret,sg,tr lee:pres,sg,tr leen:pres,pl,tr leyeron:pret,pl,tr leyó:pret,sg,tr llega:pres,sg,intr llegan:pres,pl,intr llegaron:pret,pl,intr llegó:pret,sg,intr mira:pres,sg,tr miran:pres,pl,tr miraron:pret,pl,tr miró:pret,sg,tr pensaron:pret,pl,comp pensó:pret,sg,comp persigue:pres,sg,tr persiguen:pres,pl,tr persiguieron:pret,pl,tr persiguió:pret,sg,tr piensa:pres,sg,comp piensan:pres,pl,comp trabaja:pres,sg,intr trabajan:pres,pl,intr trabajaron:pret,pl,intr trabajó:pret,sg,intr ve:pres,sg,tr ven:pres,pl,tr vieron:pret,pl,tr vio:pret,sg,tr
PN: ana:f,sg,h juan:m,sg,h maría:f,sg,h pedro:m,sg,h
ADJ: blanca:f,sg blancas:f,pl blanco:m,sg blancos:m,pl cansada:f,sg cansadas:f,pl cansado:m,sg cansados:m,pl felices:mf,pl feliz:mf,sg grande:mf,sg grandes:mf,pl inteligente:mf,sg inteligentes:mf,pl joven:mf,sg jóvenes:mf,pl negra:f,sg negras:f,pl negro:m,sg negros:m,pl nueva:f,sg nuevas:f,pl nuevo:m,sg nuevos:m,pl pequeña:f,sg pequeñas:f,pl pequeño:m,sg pequeños:m,pl rápida:f,sg rápidas:f,pl rápido:m,sg rápidos:m,pl simpática:f,sg simpáticas:f,pl simpático:m,sg simpáticos:m,pl vieja:f,sg viejas:f,pl viejo:m,sg viejos:m,pl
N: carta:f,sg,n cartas:f,pl,n casa:f,sg,n casas:f,pl,n ciudad:f,sg,n ciudades:f,pl,n cocina:f,sg,n cocinas:f,pl,n escuela:f,sg,n escuelas:f,pl,n estudiante:mf,sg,h estudiantes:mf,pl,h gata:f,sg,a gatas:f,pl,a gato:m,sg,a gatos:m,pl,a hombre:m,sg,h hombres:m,pl,h jardines:m,pl,n jardín:m,sg,n libro:m,sg,n libros:m,pl,n manzana:f,sg,n manzanas:f,pl,n mesa:f,sg,n mesas:f,pl,n mujer:f,sg,h mujeres:f,pl,h niña:f,sg,h niñas:f,pl,h niño:m,sg,h niños:m,pl,h pan:m,sg,n panes:m,pl,n parque:m,sg,n parques:m,pl,n perra:f,sg,a perras:f,pl,a perro:m,sg,a perros:m,pl,a profesor:m,sg,h profesora:f,sg,h profesoras:f,pl,h profesores:m,pl,h puerta:f,sg,n puertas:f,pl,n pájaro:m,sg,a pájaros:m,pl,a ratones:m,pl,a ratón:m,sg,a sombrero:m,sg,n sombreros:m,pl,n telescopio:m,sg,n telescopios:m,pl,n ventana:f,sg,n ventanas:f,pl,n
DET: el:m,sg la:f,sg las:f,pl los:m,pl un:m,sg una:f,sg unas:f,pl unos:m,pl
ADV: hoy lentamente rápidamente siempre tranquilamente
QUE: que

Responde con JSON: {"acepta": true|false, "arbol": "<árbol en notación de paréntesis o null>", "regla_que_falla": "<regla o restricción violada, o null>", "razon": "<una frase>"}. Formato del árbol: (O (SN (Det[m,sg] el) (N[m,sg] gato)) (SV (V[pres,sg] corre))) — cada hoja es una palabra; los rasgos van entre corchetes en las categorías léxicas.

EJEMPLOS RESUELTOS:

Oración: el pájaro canta
{"acepta": true, "arbol": "(O (SN (Det[m,sg] el) (N[m,sg] pájaro)) (SV (V[pres,sg] canta)))", "regla_que_falla": null, "razon": "derivable"}

Oración: la gata come una manzana
{"acepta": true, "arbol": "(O (SN (Det[f,sg] la) (N[f,sg] gata)) (SV (V[pres,sg] come) (SN (Det[f,sg] una) (N[f,sg] manzana))))", "regla_que_falla": null, "razon": "derivable"}

Oración: los perros que duermen corren
{"acepta": true, "arbol": "(O (SN (Det[m,pl] los) (N[m,pl] perros) (Rel (Que que) (SV (V[pres,pl] duermen)))) (SV (V[pres,pl] corren)))", "regla_que_falla": null, "razon": "derivable"}

Oración: los pájaro cantan
{"acepta": false, "arbol": null, "regla_que_falla": "falla en la posición 1 ('pájaro'), regla «concordancia Det–N»: 'los' (m,pl) no concuerda con 'pájaro' (m,sg)", "razon": "no derivable con la gramática dada"}

Oración: canta
{"acepta": false, "arbol": null, "regla_que_falla": "falla en la posición 0 ('canta'), regla «SN → Det N | PN»: se esperaba un determinante o nombre propio y llegó 'canta'", "razon": "no derivable con la gramática dada"}

Oración: el niño canta y corre
{"acepta": false, "arbol": null, "regla_que_falla": "palabra(s) fuera del léxico: y", "razon": "no derivable con la gramática dada"}

Analiza esta oración:
Oración: {oracion}
````

## Respuestas

### [01] el gato persigue al ratón

- Nivel 1 · español correcto: sí · fenómeno: SVO simple (a personal con animal)
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
{"acepta": true, "arbol": "(O (SN (Det[m,sg] el) (N[m,sg] gato)) (SV (V[pres,sg] persigue) (Obj (A a) (SN (Det[m,sg] el) (N[m,sg] ratón)))))", "regla_que_falla": null, "razon": "derivable"}
````

### [02] la niña lee un libro

- Nivel 1 · español correcto: sí · fenómeno: SVO simple
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
{"acepta": true, "arbol": "(O (SN (Det[f,sg] la) (N[f,sg] niña)) (SV (V[pres,sg] lee) (SN (Det[m,sg] un) (N[m,sg] libro))))", "regla_que_falla": null, "razon": "derivable"}
````

### [03] el profesor escribe una carta

- Nivel 1 · español correcto: sí · fenómeno: SVO simple
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
{"acepta": true, "arbol": "(O (SN (Det[m,sg] el) (N[m,sg] profesor)) (SV (V[pres,sg] escribe) (SN (Det[f,sg] una) (N[f,sg] carta))))", "regla_que_falla": null, "razon": "derivable"}
````

### [04] los niños comen el pan

- Nivel 1 · español correcto: sí · fenómeno: SVO simple plural
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
{"acepta": true, "arbol": "(O (SN (Det[m,pl] los) (N[m,pl] niños)) (SV (V[pres,pl] comen) (SN (Det[m,sg] el) (N[m,sg] pan))))", "regla_que_falla": null, "razon": "derivable"}
````

### [05] la mujer abre la puerta

- Nivel 1 · español correcto: sí · fenómeno: SVO simple
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
{"acepta": true, "arbol": "(O (SN (Det[f,sg] la) (N[f,sg] mujer)) (SV (V[pres,sg] abre) (SN (Det[f,sg] la) (N[f,sg] puerta))))", "regla_que_falla": null, "razon": "derivable"}
````
