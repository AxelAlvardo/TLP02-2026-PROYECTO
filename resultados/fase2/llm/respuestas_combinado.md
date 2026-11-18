# Respuestas del LLM — variante combinado

- Proveedor: gemini · modelo: gemini-3.5-flash-lite (la API reporta: gemini-3.5-flash-lite)
- SDK: google-genai 3.4.0
- Parámetros: temperature = 0 · max_tokens = 4096
- Prompt: `casos/espanol/prompts/combinado.txt` · instrucciones de sistema: sí · ejemplos resueltos: 6
- Primera llamada: 2026-11-18T11:49:19.241-06:00 · última llamada: 2026-11-18T11:54:36.279-06:00
- Oraciones analizadas: 71
- Log bruto (una línea JSON por llamada): `resultados/fase2/logs/llm_combinado.jsonl`

## Resumen

Referencia: lo que acepta la gramática (veredicto del parser propio).

| Resultado | Oraciones |
|---|---|
| Coincide con la gramática | 67/71 |
| Desviación hacia el español (acepta lo que la gramática rechaza, pero es español correcto) | 2 |
| Aceptó una oración agramatical | 0 |
| Sobre-rechazo (rechaza lo que la gramática deriva) | 2 |
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
- Llamada: 2026-11-18T11:49:19.241-06:00 · 1138 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": true, "arbol": "(O (SN (Det[m,sg] el) (N[m,sg] gato)) (SV (V[pres,sg] persigue) (Obj (A a) (SN (Det[m,sg] el) (N[m,sg] ratón)))))", "regla_que_falla": null, "razon": "derivable"}
```
````

### [02] la niña lee un libro

- Nivel 1 · español correcto: sí · fenómeno: SVO simple
- Llamada: 2026-11-18T11:49:20.379-06:00 · 4954 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": true, "arbol": "(O (SN (Det[f,sg] la) (N[f,sg] niña)) (SV (V[pres,sg] lee) (SN (Det[m,sg] un) (N[m,sg] libro))))", "regla_que_falla": null, "razon": "derivable"}
```
````

### [03] el profesor escribe una carta

- Nivel 1 · español correcto: sí · fenómeno: SVO simple
- Llamada: 2026-11-18T11:49:25.334-06:00 · 794 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,sg] el) (N[m,sg,h] profesor)) (SV (V[pres,sg,tr] escribe) (SN (Det[f,sg] una) (N[f,sg,n] carta))))",
  "regla_que_falla": null,
  "razon": "derivable"
}
```
````

### [04] los niños comen el pan

- Nivel 1 · español correcto: sí · fenómeno: SVO simple plural
- Llamada: 2026-11-18T11:49:26.129-06:00 · 5646 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,pl] los) (N[m,pl] niños)) (SV (V[pres,pl] comen) (SN (Det[m,sg] el) (N[m,sg] pan))))",
  "regla_que_falla": null,
  "razon": "derivable"
}
```
````

### [05] la mujer abre la puerta

- Nivel 1 · español correcto: sí · fenómeno: SVO simple
- Llamada: 2026-11-18T11:49:31.776-06:00 · 695 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": true, "arbol": "(O (SN (Det[f,sg] la) (N[f,sg] mujer)) (SV (V[pres,sg] abre) (SN (Det[f,sg] la) (N[f,sg] puerta))))", "regla_que_falla": null, "razon": "derivable"}
```
````

### [06] el perro mira al niño

- Nivel 1 · español correcto: sí · fenómeno: SVO con a personal humano
- Llamada: 2026-11-18T11:49:32.472-06:00 · 16616 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": true, "arbol": "(O (SN (Det[m,sg] el) (N[m,sg] perro)) (SV (V[pres,sg] mira) (Obj (A a) (SN (Det[m,sg] el) (N[m,sg] niño)))))", "regla_que_falla": null, "razon": "derivable"}
```
````

### [07] María compra una manzana

- Nivel 1 · español correcto: sí · fenómeno: SVO con nombre propio
- Llamada: 2026-11-18T11:49:49.088-06:00 · 4975 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": true, "arbol": "(O (SN (PN[f,sg] maría)) (SV (V[pres,sg] compra) (SN (Det[f,sg] una) (N[f,sg] manzana))))", "regla_que_falla": null, "razon": "derivable"}
```
````

### [08] Juan ve a Ana

- Nivel 1 · español correcto: sí · fenómeno: SVO con nombres propios y a personal
- Llamada: 2026-11-18T11:49:54.064-06:00 · 712 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (PN[m,sg,h] juan)) (SV (V[pres,sg] ve) (Obj (A a) (SN (PN[f,sg,h] ana)))))",
  "regla_que_falla": null,
  "razon": "derivable"
}
```
````

### [09] el gato corre

- Nivel 1 · español correcto: sí · fenómeno: intransitiva
- Llamada: 2026-11-18T11:49:54.777-06:00 · 719 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,sg] el) (N[m,sg,a] gato)) (SV (V[pres,sg] corre)))",
  "regla_que_falla": null,
  "razon": "derivable"
}
```
````

### [10] los pájaros cantan

- Nivel 1 · español correcto: sí · fenómeno: intransitiva plural
- Llamada: 2026-11-18T11:49:55.498-06:00 · 792 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,pl] los) (N[m,pl] pájaros)) (SV (V[pres,pl] cantan)))",
  "regla_que_falla": null,
  "razon": "derivable"
}
```
````

### [11] la niña duerme

- Nivel 1 · español correcto: sí · fenómeno: intransitiva
- Llamada: 2026-11-18T11:49:56.291-06:00 · 4326 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": true, "arbol": "(O (SN (Det[f,sg] la) (N[f,sg,h] niña)) (SV (V[pres,sg] duerme)))", "regla_que_falla": null, "razon": "derivable"}
```
````

### [12] el profesor llegó

- Nivel 1 · español correcto: sí · fenómeno: intransitiva pretérito
- Llamada: 2026-11-18T11:50:00.619-06:00 · 870 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": true, "arbol": "(O (SN (Det[m,sg] el) (N[m,sg] profesor)) (SV (V[pret,sg] llegó)))", "regla_que_falla": null, "razon": "derivable"}
```
````

### [13] las gatas comieron el pan

- Nivel 1 · español correcto: sí · fenómeno: SVO pretérito plural
- Llamada: 2026-11-18T11:50:01.490-06:00 · 4348 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[f,pl] las) (N[f,pl] gatas)) (SV (V[pret,pl] comieron) (SN (Det[m,sg] el) (N[m,sg] pan))))",
  "regla_que_falla": null,
  "razon": "derivable"
}
```
````

### [14] Pedro leyó un libro

- Nivel 1 · español correcto: sí · fenómeno: SVO pretérito
- Llamada: 2026-11-18T11:50:05.839-06:00 · 3563 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (PN[m,sg,h] pedro)) (SV (V[pret,sg] leyó) (SN (Det[m,sg] un) (N[m,sg,n] libro))))",
  "regla_que_falla": null,
  "razon": "derivable"
}
```
````

### [15] los estudiantes escribieron las cartas

- Nivel 1 · español correcto: sí · fenómeno: SVO pretérito plural (sustantivo mf)
- Llamada: 2026-11-18T11:50:09.403-06:00 · 4446 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,pl] los) (N[m,pl,h] estudiantes)) (SV (V[pret,pl] escribieron) (SN (Det[f,pl] las) (N[f,pl,n] cartas))))",
  "regla_que_falla": null,
  "razon": "derivable"
}
```
````

### [16] el perro persiguió al gato

- Nivel 1 · español correcto: sí · fenómeno: SVO pretérito
- Llamada: 2026-11-18T11:50:13.851-06:00 · 3869 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": true, "arbol": "(O (SN (Det[m,sg] el) (N[m,sg] perro)) (SV (V[pret,sg,tr] persiguió) (Obj (A a) (SN (Det[m,sg] el) (N[m,sg] gato)))))", "regla_que_falla": null, "razon": "derivable"}
```
````

### [17] la profesora abre la ventana

- Nivel 1 · español correcto: sí · fenómeno: SVO simple
- Llamada: 2026-11-18T11:50:17.721-06:00 · 917 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[f,sg] la) (N[f,sg] profesora)) (SV (V[pres,sg,tr] abre) (SN (Det[f,sg] la) (N[f,sg] ventana))))",
  "regla_que_falla": null,
  "razon": "derivable"
}
```
````

### [18] Ana compró una casa

- Nivel 1 · español correcto: sí · fenómeno: SVO pretérito con nombre propio
- Llamada: 2026-11-18T11:50:18.639-06:00 · 15386 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (PN[f,sg,h] ana)) (SV (V[pret,sg] compró) (SN (Det[f,sg] una) (N[f,sg,n] casa))))",
  "regla_que_falla": null,
  "razon": "derivable"
}
```
````

### [19] los niños corrieron

- Nivel 1 · español correcto: sí · fenómeno: intransitiva pretérito plural
- Llamada: 2026-11-18T11:50:34.025-06:00 · 4992 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": true, "arbol": "(O (SN (Det[m,pl] los) (N[m,pl] niños)) (SV (V[pret,pl] corrieron)))", "regla_que_falla": null, "razon": "derivable"}
```
````

### [20] el hombre trabaja

- Nivel 1 · español correcto: sí · fenómeno: intransitiva
- Llamada: 2026-11-18T11:50:39.018-06:00 · 4749 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": true, "arbol": "(O (SN (Det[m,sg] el) (N[m,sg,h] hombre)) (SV (V[pres,sg,intr] trabaja)))", "regla_que_falla": null, "razon": "derivable"}
```
````

### [21] el gato negro persigue al ratón blanco

- Nivel 2 · español correcto: sí · fenómeno: adjetivos pospuestos
- Llamada: 2026-11-18T11:50:43.768-06:00 · 5368 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,sg] el) (N[m,sg] gato) (Adj[m,sg] negro)) (SV (V[pres,sg] persigue) (Obj (A a) (SN (Det[m,sg] el) (N[m,sg] ratón) (Adj[m,sg] blanco)))))",
  "regla_que_falla": null,
  "razon": "derivable"
}
```
````

### [22] la niña pequeña lee un libro nuevo

- Nivel 2 · español correcto: sí · fenómeno: adjetivos en sujeto y objeto
- Llamada: 2026-11-18T11:50:49.137-06:00 · 5238 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[f,sg] la) (N[f,sg] niña) (Adj[f,sg] pequeña)) (SV (V[pres,sg] lee) (SN (Det[m,sg] un) (N[m,sg] libro) (Adj[m,sg] nuevo))))",
  "regla_que_falla": null,
  "razon": "derivable"
}
```
````

### [23] los gatos negros persiguen a los ratones

- Nivel 2 · español correcto: sí · fenómeno: adjetivo plural y a personal con animal
- Llamada: 2026-11-18T11:50:54.377-06:00 · 4996 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,pl] los) (N[m,pl] gatos) (Adj[m,pl] negros)) (SV (V[pres,pl] persiguen) (Obj (A a) (SN (Det[m,pl] los) (N[m,pl] ratones)))))",
  "regla_que_falla": null,
  "razon": "derivable"
}
```
````

### [24] el profesor lee rápidamente la carta

- Nivel 2 · español correcto: sí · fenómeno: adverbio antes del objeto
- Llamada: 2026-11-18T11:50:59.373-06:00 · 841 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,sg] el) (N[m,sg] profesor)) (SV (V[pres,sg] lee) (Adv rápidamente) (SN (Det[f,sg] la) (N[f,sg] carta))))",
  "regla_que_falla": null,
  "razon": "derivable"
}
```
````

### [25] la niña escribe la carta lentamente

- Nivel 2 · español correcto: sí · fenómeno: adverbio después del objeto
- Llamada: 2026-11-18T11:51:00.216-06:00 · 1126 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": true, "arbol": "(O (SN (Det[f,sg] la) (N[f,sg] niña)) (SV (V[pres,sg] escribe) (SN (Det[f,sg] la) (N[f,sg] carta)) (Adv lentamente)))", "regla_que_falla": null, "razon": "derivable"}
```
````

### [26] el gato duerme tranquilamente

- Nivel 2 · español correcto: sí · fenómeno: adverbio con intransitivo
- Llamada: 2026-11-18T11:51:01.342-06:00 · 5010 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": true, "arbol": "(O (SN (Det[m,sg] el) (N[m,sg] gato)) (SV (V[pres,sg] duerme) (Adv tranquilamente)))", "regla_que_falla": null, "razon": "derivable"}
```
````

### [27] los niños cansados llegaron a la escuela

- Nivel 2 · español correcto: sí · fenómeno: frase preposicional con intransitivo
- Llamada: 2026-11-18T11:51:06.354-06:00 · 1032 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,pl] los) (N[m,pl] niños) (Adj[m,pl] cansados)) (SV (V[pret,pl] llegaron) (SP (P a) (SN (Det[f,sg] la) (N[f,sg] escuela)))))",
  "regla_que_falla": null,
  "razon": "derivable"
}
```
````

### [28] la mujer compró el pan en la ciudad

- Nivel 2 · español correcto: sí · fenómeno: frase preposicional
- Llamada: 2026-11-18T11:51:07.386-06:00 · 5240 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[f,sg] la) (N[f,sg] mujer)) (SV (V[pret,sg] compró) (SN (Det[m,sg] el) (N[m,sg] pan)) (SP (P en) (SN (Det[f,sg] la) (N[f,sg] ciudad)))))",
  "regla_que_falla": null,
  "razon": "derivable"
}
```
````

### [29] el hombre ve al gato con el telescopio

- Nivel 2 · español correcto: sí · fenómeno: ambigüedad por adjunción de FP (2 árboles)
- Llamada: 2026-11-18T11:51:12.628-06:00 · 752 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,sg] el) (N[m,sg] hombre)) (SV (V[pres,sg] ve) (Obj (A a) (SN (Det[m,sg] el) (N[m,sg] gato))) (SP (P con) (SN (Det[m,sg] el) (N[m,sg] telescopio)))))",
  "regla_que_falla": null,
  "razon": "derivable; 'al' se descompone en 'a el' según las restricciones."
}
```
````

### [30] el profesor mira a la niña con el libro

- Nivel 2 · español correcto: sí · fenómeno: ambigüedad por adjunción de FP (2 árboles)
- Llamada: 2026-11-18T11:51:13.381-06:00 · 11002 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,sg] el) (N[m,sg] profesor)) (SV (V[pres,sg] mira) (Obj (A a) (SN (Det[f,sg] la) (N[f,sg] niña))) (SP (P con) (SN (Det[m,sg] el) (N[m,sg] libro)))))",
  "regla_que_falla": null,
  "razon": "derivable"
}
```
````

### [31] la gata que duerme come el pan

- Nivel 2 · español correcto: sí · fenómeno: relativa de sujeto
- Llamada: 2026-11-18T11:51:24.385-06:00 · 5011 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": true, "arbol": "(O (SN (Det[f,sg] la) (N[f,sg] gata) (Rel (Que que) (SV (V[pres,sg] duerme)))) (SV (V[pres,sg] come) (SN (Det[m,sg] el) (N[m,sg] pan))))", "regla_que_falla": null, "razon": "derivable"}
```
````

### [32] el niño que lee el libro corre

- Nivel 2 · español correcto: sí · fenómeno: relativa de sujeto con objeto
- Llamada: 2026-11-18T11:51:29.397-06:00 · 5221 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,sg] el) (N[m,sg] niño) (Rel (Que que) (SV (V[pres,sg] lee) (SN (Det[m,sg] el) (N[m,sg] libro))))) (SV (V[pres,sg] corre)))",
  "regla_que_falla": null,
  "razon": "derivable"
}
```
````

### [33] María dice que el gato corre

- Nivel 2 · español correcto: sí · fenómeno: completiva con que
- Llamada: 2026-11-18T11:51:34.619-06:00 · 5114 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (PN[f,sg,h] maría)) (SV (V[pres,sg] dice) (Que que) (O (SN (Det[m,sg] el) (N[m,sg,a] gato)) (SV (V[pres,sg] corre)))))",
  "regla_que_falla": null,
  "razon": "derivable"
}
```
````

### [34] Juan piensa que los niños duermen

- Nivel 2 · español correcto: sí · fenómeno: completiva con que
- Llamada: 2026-11-18T11:51:39.734-06:00 · 1542 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": true, "arbol": "(O (SN (PN[m,sg,h] juan)) (SV (V[pres,sg] piensa) (Que que) (O (SN (Det[m,pl] los) (N[m,pl] niños)) (SV (V[pres,pl] duermen)))))", "regla_que_falla": null, "razon": "derivable"}
```
````

### [35] los estudiantes jóvenes escribieron una carta grande para la profesora

- Nivel 2 · español correcto: sí · fenómeno: adjetivos mf y frase preposicional
- Llamada: 2026-11-18T11:51:41.277-06:00 · 5592 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,pl] los) (N[m,pl] estudiantes) (Adj[mf,pl] jóvenes)) (SV (V[pret,pl] escribieron) (SN (Det[f,sg] una) (N[f,sg] carta) (Adj[f,sg] grande)) (SP (P para) (SN (Det[f,sg] la) (N[f,sg] profesora)))))",
  "regla_que_falla": null,
  "razon": "derivable"
}
```
````

### [36] la gatos negros persiguen al ratón

- Nivel 2 · español correcto: no · fenómeno: discordancia determinante-sustantivo
- Llamada: 2026-11-18T11:51:46.870-06:00 · 794 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": false, "arbol": null, "regla_que_falla": "falla en la posición 1 ('gatos'), regla «concordancia Det–N»: 'la' (f,sg) no concuerda con 'gatos' (m,pl)", "razon": "no derivable con la gramática dada"}
```
````

### [37] el gato negro persiguen al ratón

- Nivel 2 · español correcto: no · fenómeno: discordancia sujeto-verbo
- Llamada: 2026-11-18T11:51:47.666-06:00 · 691 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "número de SN y de V deben coincidir",
  "razon": "el sujeto 'el gato negro' es singular (m,sg) pero el verbo 'persiguen' es plural (pl), violando la regla de concordancia entre SN y SV"
}
```
````

### [38] los niños duerme

- Nivel 2 · español correcto: no · fenómeno: discordancia sujeto-verbo
- Llamada: 2026-11-18T11:51:48.358-06:00 · 748 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "falla en la posición 2 ('duerme'), regla «O → SN SV»: el número de SN (pl) y de V (sg) no coinciden",
  "razon": "no derivable con la gramática dada"
}
```
````

### [39] las niñas pequeño leen un libro

- Nivel 2 · español correcto: no · fenómeno: discordancia sustantivo-adjetivo
- Llamada: 2026-11-18T11:51:49.107-06:00 · 5616 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "falla en la posición 2 ('pequeño'), regla «concordancia N–Adj»: 'niñas' (f,pl) no concuerda con 'pequeño' (m,sg)",
  "razon": "no derivable con la gramática dada"
}
```
````

### [40] el niña lee un libro

- Nivel 2 · español correcto: no · fenómeno: discordancia de género det-sustantivo
- Llamada: 2026-11-18T11:51:54.724-06:00 · 5505 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": false, "arbol": null, "regla_que_falla": "falla en la posición 1 ('niña'), regla «concordancia Det–N»: 'el' (m,sg) no concuerda con 'niña' (f,sg)", "razon": "no derivable con la gramática dada"}
```
````

### [41] una gato corre

- Nivel 2 · español correcto: no · fenómeno: discordancia de género det-sustantivo
- Llamada: 2026-11-18T11:52:00.230-06:00 · 5318 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": false, "arbol": null, "regla_que_falla": "falla en la posición 1 ('gato'), regla «concordancia Det–N»: 'una' (f,sg) no concuerda con 'gato' (m,sg)", "razon": "no derivable con la gramática dada"}
```
````

### [42] gato el persigue ratón el

- Nivel 2 · español correcto: no · fenómeno: orden de palabras alterado
- Llamada: 2026-11-18T11:52:05.549-06:00 · 6708 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": false, "arbol": null, "regla_que_falla": "falla en la posición 0 ('gato'), regla «O → SN SV»: orden sintáctico incorrecto", "razon": "no derivable con la gramática dada"}
```
````

### [43] el persigue gato al ratón

- Nivel 2 · español correcto: no · fenómeno: orden de palabras alterado
- Llamada: 2026-11-18T11:52:12.259-06:00 · 893 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": false, "arbol": null, "regla_que_falla": "falla en la posición 1 ('persigue'), regla «SN → Det N Adj* SP* Rel?» o «O → SN SV»: orden sintáctico incorrecto o sujeto no explícito", "razon": "no derivable con la gramática dada"}
```
````

### [44] la niña lee un libro nuevos

- Nivel 2 · español correcto: no · fenómeno: discordancia sustantivo-adjetivo en objeto
- Llamada: 2026-11-18T11:52:13.153-06:00 · 5760 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "falla en la posición 4 ('nuevos'), regla «SN → Det N Adj* SP* Rel?» (concordancia Adj–N): 'nuevos' (m,pl) no concuerda con 'libro' (m,sg)",
  "razon": "no derivable con la gramática dada"
}
```
````

### [45] los gatos negra persiguen al ratón

- Nivel 2 · español correcto: no · fenómeno: discordancia sustantivo-adjetivo
- Llamada: 2026-11-18T11:52:18.914-06:00 · 5879 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "falla en la posición 2 ('negra'), regla «concordancia N–Adj»: 'negra' (f,sg) no concuerda con 'gatos' (m,pl)",
  "razon": "no derivable con la gramática dada"
}
```
````

### [46] come el pan

- Nivel 3 · español correcto: sí · fenómeno: sujeto tácito (pro-drop)
- Llamada: 2026-11-18T11:52:24.794-06:00 · 4461 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": false, "arbol": null, "regla_que_falla": "sujeto SIEMPRE explícito", "razon": "no derivable con la gramática dada"}
```
````

### [47] llegó ayer

- Nivel 3 · español correcto: sí · fenómeno: sujeto tácito y adverbio fuera del léxico
- Llamada: 2026-11-18T11:52:29.255-06:00 · 919 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "restricción: sujeto SIEMPRE explícito / regla O -> SN SV",
  "razon": "no derivable con la gramática dada debido a la falta de un sujeto explícito"
}
```
````

### [48] el gato la persigue

- Nivel 3 · español correcto: sí · fenómeno: pronombre clítico
- Llamada: 2026-11-18T11:52:30.175-06:00 · 5504 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": false, "arbol": null, "regla_que_falla": "no hay coordinación, clíticos, negación, interrogativas, pasivas, ni verbos copulativos", "razon": "la oración contiene el pronombre clítico 'la', el cual está explícitamente prohibido por las restricciones de la gramática"}
```
````

### [49] Juan y María leen un libro

- Nivel 3 · español correcto: sí · fenómeno: coordinación nominal
- Llamada: 2026-11-18T11:52:35.681-06:00 · 4836 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "restricción «no hay coordinación» o palabra(s) fuera del léxico: y",
  "razon": "no derivable con la gramática dada"
}
```
````

### [50] el gato come y duerme

- Nivel 3 · español correcto: sí · fenómeno: coordinación verbal
- Llamada: 2026-11-18T11:52:40.518-06:00 · 5106 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": false, "arbol": null, "regla_que_falla": "palabra(s) fuera del léxico: y", "razon": "no derivable con la gramática dada"}
```
````

### [51] el libro que el niño lee es nuevo

- Nivel 3 · español correcto: sí · fenómeno: relativa de objeto y verbo copulativo
- Llamada: 2026-11-18T11:52:45.625-06:00 · 5633 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "no hay verbos copulativos (restricción: \"ni verbos copulativos\") / palabra \"es\" fuera del léxico",
  "razon": "no derivable con la gramática dada"
}
```
````

### [52] el libro fue escrito por el profesor

- Nivel 3 · español correcto: sí · fenómeno: voz pasiva
- Llamada: 2026-11-18T11:52:51.259-06:00 · 4344 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "restricción «no hay pasivas»",
  "razon": "no derivable con la gramática dada"
}
```
````

### [53] quiero que el gato corra

- Nivel 3 · español correcto: sí · fenómeno: primera persona y subjuntivo
- Llamada: 2026-11-18T11:52:55.604-06:00 · 1143 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "falla en la posición 0 ('quiero'), palabra fuera del léxico",
  "razon": "no derivable con la gramática dada"
}
```
````

### [54] ¿dónde está el gato?

- Nivel 3 · español correcto: sí · fenómeno: interrogativa
- Llamada: 2026-11-18T11:52:56.748-06:00 · 582 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": false, "arbol": null, "regla_que_falla": "no hay interrogativas / palabra(s) fuera del léxico: ¿, dónde, está", "razon": "no derivable con la gramática dada"}
```
````

### [55] el gato no come el pan

- Nivel 3 · español correcto: sí · fenómeno: negación
- Llamada: 2026-11-18T11:52:57.330-06:00 · 765 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "restricción: no hay negación",
  "razon": "no derivable con la gramática dada"
}
```
````

### [56] el gato es negro

- Nivel 3 · español correcto: sí · fenómeno: verbo copulativo
- Llamada: 2026-11-18T11:52:58.096-06:00 · 740 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "restricción: no hay verbos copulativos",
  "razon": "no derivable con la gramática dada"
}
```
````

### [57] yo veo a María

- Nivel 3 · español correcto: sí · fenómeno: primera persona y pronombre sujeto
- Llamada: 2026-11-18T11:52:58.837-06:00 · 507 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": false, "arbol": null, "regla_que_falla": "palabra(s) fuera del léxico: yo", "razon": "no derivable con la gramática dada"}
```
````

### [58] se venden casas

- Nivel 3 · español correcto: sí · fenómeno: se impersonal/pasivo reflejo
- Llamada: 2026-11-18T11:52:59.345-06:00 · 4584 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "palabra(s) fuera del léxico / uso de clítico (no permitido)",
  "razon": "no derivable con la gramática dada"
}
```
````

### [59] la niña que el gato persigue corre

- Nivel 3 · español correcto: sí · fenómeno: relativa de objeto (hueco en el objeto)
- Llamada: 2026-11-18T11:53:03.930-06:00 · 5560 ms
- Esperado (gramática): **RECHAZA** · LLM: **ACEPTA** · resultado: **desviación hacia el español**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[f,sg] la) (N[f,sg] niña) (Rel (Que que) (SV (SN (Det[m,sg] el) (N[m,sg] gato)) (V[pres,sg] persigue)))) (SV (V[pres,sg] corre)))",
  "regla_que_falla": null,
  "razon": "derivable"
}
```
````

### [60] el gato que duerme en la casa que Juan compró come el pan

- Nivel 3 · español correcto: sí · fenómeno: doble relativa con objeto relativizado
- Llamada: 2026-11-18T11:53:09.491-06:00 · 5668 ms
- Esperado (gramática): **RECHAZA** · LLM: **ACEPTA** · resultado: **desviación hacia el español**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,sg] el) (N[m,sg] gato) (Rel (Que que) (SV (V[pres,sg] duerme) (SP (P en) (SN (Det[f,sg] la) (N[f,sg] casa) (Rel (Que que) (SV (PN[m,sg,h] juan) (V[pret,sg] compró)))))))) (SV (V[pres,sg] come) (SN (Det[m,sg] el) (N[m,sg] pan))))",
  "regla_que_falla": null,
  "razon": "derivable"
}
```
````

### [61] el profesor lee más libros que la estudiante

- Nivel 3 · español correcto: sí · fenómeno: comparativa
- Llamada: 2026-11-18T11:53:15.160-06:00 · 15174 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": false, "arbol": null, "regla_que_falla": "palabra(s) fuera del léxico: más", "razon": "no derivable con la gramática dada"}
```
````

### [62] Juan y María son rubio y morena respectivamente

- Nivel 3 · español correcto: sí · fenómeno: dependencias cruzadas (respectivamente)
- Llamada: 2026-11-18T11:53:30.336-06:00 · 6062 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": false, "arbol": null, "regla_que_falla": "palabra(s) fuera del léxico: y, son, rubio, morena, respectivamente", "razon": "no derivable con la gramática dada"}
```
````

### [63] el gato duerme porque está cansado

- Nivel 3 · español correcto: sí · fenómeno: subordinada adverbial causal
- Llamada: 2026-11-18T11:53:36.398-06:00 · 4998 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "palabra(s) fuera del léxico: porque, está",
  "razon": "no derivable con la gramática dada"
}
```
````

### [64] cuando llegó Pedro los niños corrieron

- Nivel 3 · español correcto: sí · fenómeno: subordinada temporal antepuesta y sujeto pospuesto
- Llamada: 2026-11-18T11:53:41.397-06:00 · 4424 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "palabra(s) fuera del léxico: cuando",
  "razon": "no derivable con la gramática dada"
}
```
````

### [65] el libro come la casa

- Nivel 3 · español correcto: sí · fenómeno: anomalía semántica (sintácticamente correcta)
- Llamada: 2026-11-18T11:53:45.822-06:00 · 6103 ms
- Esperado (gramática): **ACEPTA** · LLM: **RECHAZA** · resultado: **sobre-rechazo**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "Obj -> SN",
  "razon": "el núcleo de SN 'la casa' es no animado (n), pero 'come' exige un objeto no animado o animal, sin embargo la restricción de objeto humano exige 'a' o en este caso 'libro' come 'casa' viola la semántica de la gramática (la casa no puede ser comida por el libro, o 'libro' es no animado, Obj requiere no animado o animal pero el verbo 'comer' con objeto no animado viola los rasgos o la regla de Obj)"
}
```
````

### [66] la mesa duerme tranquilamente

- Nivel 3 · español correcto: sí · fenómeno: anomalía semántica (sintácticamente correcta)
- Llamada: 2026-11-18T11:53:51.926-06:00 · 23658 ms
- Esperado (gramática): **ACEPTA** · LLM: **RECHAZA** · resultado: **sobre-rechazo**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "restricción semántica de léxico / selección de verbo intr: 'duerme' requiere sujeto con rasgo animado o humano, pero 'mesa' es inanimado (n)",
  "razon": "no derivable con la gramática dada"
}
```
````

### [67] el gato que corre persiguen al ratón

- Nivel 3 · español correcto: no · fenómeno: discordancia a distancia a través de una relativa
- Llamada: 2026-11-18T11:54:15.585-06:00 · 1425 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "número de SN y de V deben coincidir en O: SN 'el gato que corre' es sg, pero V 'persiguen' es pl",
  "razon": "no derivable con la gramática dada"
}
```
````

### [68] los niños que duerme corren

- Nivel 3 · español correcto: no · fenómeno: discordancia verbo-antecedente en relativa
- Llamada: 2026-11-18T11:54:17.012-06:00 · 6393 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": false, "arbol": null, "regla_que_falla": "falla en la posición 3 ('duerme'), regla «relativa de sujeto: el verbo concuerda en número con el SN antecedente»: 'duerme' (sg) no concuerda con 'niños' (pl)", "razon": "no derivable con la gramática dada"}
```
````

### [69] los niños de la escuela duerme

- Nivel 3 · español correcto: no · fenómeno: discordancia con atractor (sustantivo intermedio)
- Llamada: 2026-11-18T11:54:23.406-06:00 · 7100 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "falla en la posición 5 ('duerme'), regla «O -> SN SV»: el número del SN ('los niños de la escuela', plural) y del V ('duerme', singular) no coinciden",
  "razon": "no derivable con la gramática dada"
}
```
````

### [70] la niña que lee el libro corren

- Nivel 3 · español correcto: no · fenómeno: discordancia a distancia tras relativa con objeto
- Llamada: 2026-11-18T11:54:30.507-06:00 · 5771 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "número de SN y de V deben coincidir en O: 'la niña que lee el libro' (sg) no concuerda con 'corren' (pl)",
  "razon": "no derivable con la gramática dada"
}
```
````

### [71] el gato persigue al ratón con con

- Nivel 3 · español correcto: no · fenómeno: secuencia agramatical de preposiciones
- Llamada: 2026-11-18T11:54:36.279-06:00 · 6118 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": false, "arbol": null, "regla_que_falla": "falla en la posición 6 ('con'), regla «SP → P SN»: se esperaba un nombre propio o determinante y llegó la preposición 'con'", "razon": "no derivable con la gramática dada"}
```
````
