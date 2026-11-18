# Respuestas del LLM — variante few_shot

- Proveedor: gemini · modelo: gemini-3.5-flash-lite (la API reporta: gemini-3.5-flash-lite)
- SDK: google-genai 3.4.0
- Parámetros: temperature = 0 · max_tokens = 4096
- Prompt: `casos/espanol/prompts/few_shot.txt` · instrucciones de sistema: no · ejemplos resueltos: 6
- Primera llamada: 2026-11-18T10:52:59.507-06:00 · última llamada: 2026-11-18T11:00:00.688-06:00
- Oraciones analizadas: 71
- Log bruto (una línea JSON por llamada): `resultados/fase2/logs/llm_few_shot.jsonl`

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
(sin mensaje de sistema)
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
- Llamada: 2026-11-18T10:52:59.507-06:00 · 6710 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,sg] el) (N[m,sg,a] gato)) (SV (V[pres,sg,tr] persigue) (Obj (A a) (SN (Det[m,sg] el) (N[m,sg,a] ratón)))))",
  "regla_que_falla": null,
  "razon": "derivable"
}
```
````

### [02] la niña lee un libro

- Nivel 1 · español correcto: sí · fenómeno: SVO simple
- Llamada: 2026-11-18T10:53:06.219-06:00 · 810 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[f,sg] la) (N[f,sg] niña)) (SV (V[pres,sg,tr] lee) (SN (Det[m,sg] un) (N[m,sg] libro))))",
  "regla_que_falla": null,
  "razon": "derivable"
}
```
````

### [03] el profesor escribe una carta

- Nivel 1 · español correcto: sí · fenómeno: SVO simple
- Llamada: 2026-11-18T10:53:07.030-06:00 · 7614 ms
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
- Llamada: 2026-11-18T10:53:14.646-06:00 · 1017 ms
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
- Llamada: 2026-11-18T10:53:15.664-06:00 · 1075 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": true, "arbol": "(O (SN (Det[f,sg] la) (N[f,sg] mujer)) (SV (V[pres,sg] abre) (SN (Det[f,sg] la) (N[f,sg] puerta))))", "regla_que_falla": null, "razon": "derivable"}
```
````

### [06] el perro mira al niño

- Nivel 1 · español correcto: sí · fenómeno: SVO con a personal humano
- Llamada: 2026-11-18T10:53:16.739-06:00 · 7176 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,sg] el) (N[m,sg] perro)) (SV (V[pres,sg,tr] mira) (Obj (A a) (SN (Det[m,sg] el) (N[m,sg,h] niño)))))",
  "regla_que_falla": null,
  "razon": "derivable"
}
```
````

### [07] María compra una manzana

- Nivel 1 · español correcto: sí · fenómeno: SVO con nombre propio
- Llamada: 2026-11-18T10:53:23.916-06:00 · 7730 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (PN[f,sg,h] maría)) (SV (V[pres,sg,tr] compra) (SN (Det[f,sg] una) (N[f,sg,n] manzana))))",
  "regla_que_falla": null,
  "razon": "derivable"
}
```
````

### [08] Juan ve a Ana

- Nivel 1 · español correcto: sí · fenómeno: SVO con nombres propios y a personal
- Llamada: 2026-11-18T10:53:31.648-06:00 · 1567 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": true, "arbol": "(O (SN (PN[m,sg,h] juan)) (SV (V[pres,sg] ve) (Obj (A a) (SN (PN[f,sg,h] ana)))))", "regla_que_falla": null, "razon": "derivable"}
```
````

### [09] el gato corre

- Nivel 1 · español correcto: sí · fenómeno: intransitiva
- Llamada: 2026-11-18T10:53:33.216-06:00 · 1504 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,sg] el) (N[m,sg,a] gato)) (SV (V[pres,sg,intr] corre)))",
  "regla_que_falla": null,
  "razon": "derivable"
}
```
````

### [10] los pájaros cantan

- Nivel 1 · español correcto: sí · fenómeno: intransitiva plural
- Llamada: 2026-11-18T10:53:34.721-06:00 · 7495 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": true, "arbol": "(O (SN (Det[m,pl] los) (N[m,pl] pájaros)) (SV (V[pres,pl] cantan)))", "regla_que_falla": null, "razon": "derivable"}
```
````

### [11] la niña duerme

- Nivel 1 · español correcto: sí · fenómeno: intransitiva
- Llamada: 2026-11-18T10:53:42.217-06:00 · 1315 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": true, "arbol": "(O (SN (Det[f,sg] la) (N[f,sg] niña)) (SV (V[pres,sg] duerme)))", "regla_que_falla": null, "razon": "derivable"}
```
````

### [12] el profesor llegó

- Nivel 1 · español correcto: sí · fenómeno: intransitiva pretérito
- Llamada: 2026-11-18T10:53:43.532-06:00 · 1857 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": true, "arbol": "(O (SN (Det[m,sg] el) (N[m,sg,h] profesor)) (SV (V[pret,sg] llegó)))", "regla_que_falla": null, "razon": "derivable"}
```
````

### [13] las gatas comieron el pan

- Nivel 1 · español correcto: sí · fenómeno: SVO pretérito plural
- Llamada: 2026-11-18T10:53:45.389-06:00 · 1024 ms
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
- Llamada: 2026-11-18T10:53:46.414-06:00 · 7324 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": true, "arbol": "(O (SN (PN[m,sg,h] pedro)) (SV (V[pret,sg] leyó) (SN (Det[m,sg] un) (N[m,sg,n] libro))))", "regla_que_falla": null, "razon": "derivable"}
```
````

### [15] los estudiantes escribieron las cartas

- Nivel 1 · español correcto: sí · fenómeno: SVO pretérito plural (sustantivo mf)
- Llamada: 2026-11-18T10:53:53.743-06:00 · 1208 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,pl] los) (N[m,pl,h] estudiantes)) (SV (V[pret,pl,tr] escribieron) (SN (Det[f,pl] las) (N[f,pl,n] cartas))))",
  "regla_que_falla": null,
  "razon": "derivable"
}
```
````

### [16] el perro persiguió al gato

- Nivel 1 · español correcto: sí · fenómeno: SVO pretérito
- Llamada: 2026-11-18T10:53:54.952-06:00 · 13757 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,sg] el) (N[m,sg] perro)) (SV (V[pret,sg] persiguió) (Obj (A a) (SN (Det[m,sg] el) (N[m,sg] gato)))))",
  "regla_que_falla": null,
  "razon": "derivable"
}
```
````

### [17] la profesora abre la ventana

- Nivel 1 · español correcto: sí · fenómeno: SVO simple
- Llamada: 2026-11-18T10:54:08.711-06:00 · 7621 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": true, "arbol": "(O (SN (Det[f,sg] la) (N[f,sg,h] profesora)) (SV (V[pres,sg,tr] abre) (SN (Det[f,sg] la) (N[f,sg,n] ventana))))", "regla_que_falla": null, "razon": "derivable"}
```
````

### [18] Ana compró una casa

- Nivel 1 · español correcto: sí · fenómeno: SVO pretérito con nombre propio
- Llamada: 2026-11-18T10:54:16.333-06:00 · 1394 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": true, "arbol": "(O (SN (PN[f,sg,h] ana)) (SV (V[pret,sg] compró) (SN (Det[f,sg] una) (N[f,sg,n] casa))))", "regla_que_falla": null, "razon": "derivable"}
```
````

### [19] los niños corrieron

- Nivel 1 · español correcto: sí · fenómeno: intransitiva pretérito plural
- Llamada: 2026-11-18T10:54:17.728-06:00 · 7248 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": true, "arbol": "(O (SN (Det[m,pl] los) (N[m,pl,h] niños)) (SV (V[pret,pl,intr] corrieron)))", "regla_que_falla": null, "razon": "derivable"}
```
````

### [20] el hombre trabaja

- Nivel 1 · español correcto: sí · fenómeno: intransitiva
- Llamada: 2026-11-18T10:54:24.977-06:00 · 6771 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,sg] el) (N[m,sg] hombre)) (SV (V[pres,sg] trabaja)))",
  "regla_que_falla": null,
  "razon": "derivable"
}
```
````

### [21] el gato negro persigue al ratón blanco

- Nivel 2 · español correcto: sí · fenómeno: adjetivos pospuestos
- Llamada: 2026-11-18T10:54:31.750-06:00 · 8633 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,sg] el) (N[m,sg] gato) (Adj[m,sg] negro)) (SV (V[pres,sg,tr] persigue) (Obj (A a) (SN (Det[m,sg] el) (N[m,sg] ratón) (Adj[m,sg] blanco)))))",
  "regla_que_falla": null,
  "razon": "derivable"
}
```
````

### [22] la niña pequeña lee un libro nuevo

- Nivel 2 · español correcto: sí · fenómeno: adjetivos en sujeto y objeto
- Llamada: 2026-11-18T10:54:40.383-06:00 · 6362 ms
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
- Llamada: 2026-11-18T10:54:46.746-06:00 · 1024 ms
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
- Llamada: 2026-11-18T10:54:47.770-06:00 · 5849 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": true, "arbol": "(O (SN (Det[m,sg] el) (N[m,sg,h] profesor)) (SV (V[pres,sg,tr] lee) (Adv rápidamente) (SN (Det[f,sg] la) (N[f,sg,n] carta))))", "regla_que_falla": null, "razon": "derivable"}
```
````

### [25] la niña escribe la carta lentamente

- Nivel 2 · español correcto: sí · fenómeno: adverbio después del objeto
- Llamada: 2026-11-18T10:54:53.620-06:00 · 5887 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": true, "arbol": "(O (SN (Det[f,sg] la) (N[f,sg] niña)) (SV (V[pres,sg,tr] escribe) (SN (Det[f,sg] la) (N[f,sg] carta)) (Adv lentamente)))", "regla_que_falla": null, "razon": "derivable"}
```
````

### [26] el gato duerme tranquilamente

- Nivel 2 · español correcto: sí · fenómeno: adverbio con intransitivo
- Llamada: 2026-11-18T10:54:59.508-06:00 · 1432 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": true, "arbol": "(O (SN (Det[m,sg] el) (N[m,sg] gato)) (SV (V[pres,sg] duerme) (Adv tranquilamente)))", "regla_que_falla": null, "razon": "derivable"}
```
````

### [27] los niños cansados llegaron a la escuela

- Nivel 2 · español correcto: sí · fenómeno: frase preposicional con intransitivo
- Llamada: 2026-11-18T10:55:00.942-06:00 · 1090 ms
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
- Llamada: 2026-11-18T10:55:02.033-06:00 · 2123 ms
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
- Llamada: 2026-11-18T10:55:04.157-06:00 · 22003 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": true, "arbol": "(O (SN (Det[m,sg] el) (N[m,sg] hombre)) (SV (V[pres,sg,tr] ve) (Obj (A a) (SN (Det[m,sg] el) (N[m,sg] gato))) (SP (P con) (SN (Det[m,sg] el) (N[m,sg] telescopio)))))", "regla_que_falla": null, "razon": "derivable"}
```
````

### [30] el profesor mira a la niña con el libro

- Nivel 2 · español correcto: sí · fenómeno: ambigüedad por adjunción de FP (2 árboles)
- Llamada: 2026-11-18T10:55:26.162-06:00 · 19984 ms
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
- Llamada: 2026-11-18T10:55:46.149-06:00 · 12778 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[f,sg] la) (N[f,sg] gata) (Rel (Que que) (SV (V[pres,sg] duerme)))) (SV (V[pres,sg] come) (SN (Det[m,sg] el) (N[m,sg] pan))))",
  "regla_que_falla": null,
  "razon": "derivable"
}
```
````

### [32] el niño que lee el libro corre

- Nivel 2 · español correcto: sí · fenómeno: relativa de sujeto con objeto
- Llamada: 2026-11-18T10:55:58.929-06:00 · 12523 ms
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
- Llamada: 2026-11-18T10:56:11.454-06:00 · 5981 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (PN[f,sg,h] maría)) (SV (V[pres,sg,comp] dice) (Que que) (O (SN (Det[m,sg] el) (N[m,sg,a] gato)) (SV (V[pres,sg,intr] corre)))))",
  "regla_que_falla": null,
  "razon": "derivable"
}
```
````

### [34] Juan piensa que los niños duermen

- Nivel 2 · español correcto: sí · fenómeno: completiva con que
- Llamada: 2026-11-18T10:56:17.437-06:00 · 5834 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (PN[m,sg,h] juan)) (SV (V[pres,sg,comp] piensa) (Que que) (O (SN (Det[m,pl] los) (N[m,pl,h] niños)) (SV (V[pres,pl] duermen)))))",
  "regla_que_falla": null,
  "razon": "derivable"
}
```
````

### [35] los estudiantes jóvenes escribieron una carta grande para la profesora

- Nivel 2 · español correcto: sí · fenómeno: adjetivos mf y frase preposicional
- Llamada: 2026-11-18T10:56:23.272-06:00 · 1442 ms
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
- Llamada: 2026-11-18T10:56:24.715-06:00 · 5530 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": false, "arbol": null, "regla_que_falla": "falla en la posición 1 ('gatos'), regla «concordancia Det–N»: 'la' (f,sg) no concuerda con 'gatos' (m,pl)", "razon": "no derivable con la gramática dada"}
```
````

### [37] el gato negro persiguen al ratón

- Nivel 2 · español correcto: no · fenómeno: discordancia sujeto-verbo
- Llamada: 2026-11-18T10:56:30.246-06:00 · 796 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "falla en la regla «O -> SN SV»: el número del sujeto 'el gato negro' (sg) no coincide con el número del verbo 'persiguen' (pl)",
  "razon": "no derivable con la gramática dada"
}
```
````

### [38] los niños duerme

- Nivel 2 · español correcto: no · fenómeno: discordancia sujeto-verbo
- Llamada: 2026-11-18T10:56:31.042-06:00 · 6204 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": false, "arbol": null, "regla_que_falla": "concordancia SN–SV / número del verbo: 'los niños' es pl, pero 'duerme' es sg", "razon": "no derivable con la gramática dada"}
```
````

### [39] las niñas pequeño leen un libro

- Nivel 2 · español correcto: no · fenómeno: discordancia sustantivo-adjetivo
- Llamada: 2026-11-18T10:56:37.248-06:00 · 5655 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "falla en la posición 3 ('pequeño'), regla «cada Adj concuerda con N»: 'pequeño' (m,sg) no concuerda con 'niñas' (f,pl)",
  "razon": "no derivable con la gramática dada"
}
```
````

### [40] el niña lee un libro

- Nivel 2 · español correcto: no · fenómeno: discordancia de género det-sustantivo
- Llamada: 2026-11-18T10:56:42.904-06:00 · 6208 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "falla en la posición 1 ('niña'), regla «concordancia Det–N»: 'el' (m,sg) no concuerda con 'niña' (f,sg)",
  "razon": "no derivable con la gramática dada"
}
```
````

### [41] una gato corre

- Nivel 2 · español correcto: no · fenómeno: discordancia de género det-sustantivo
- Llamada: 2026-11-18T10:56:49.113-06:00 · 5369 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "falla en la posición 1 ('gato'), regla «concordancia Det–N»: 'una' (f,sg) no concuerda con 'gato' (m,sg)",
  "razon": "no derivable con la gramática dada"
}
```
````

### [42] gato el persigue ratón el

- Nivel 2 · español correcto: no · fenómeno: orden de palabras alterado
- Llamada: 2026-11-18T10:56:54.484-06:00 · 1014 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "falla en la posición 0 ('gato'), regla «O → SN SV»: orden sintáctico incorrecto (se esperaba sujeto al inicio)",
  "razon": "no derivable con la gramática dada"
}
```
````

### [43] el persigue gato al ratón

- Nivel 2 · español correcto: no · fenómeno: orden de palabras alterado
- Llamada: 2026-11-18T10:56:55.498-06:00 · 1765 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "falla en la posición 1 ('persigue'), regla «SN -> SV»: se esperaba un sintagma nominal como sujeto pero llegó el verbo 'persigue'",
  "razon": "no derivable con la gramática dada"
}
```
````

### [44] la niña lee un libro nuevos

- Nivel 2 · español correcto: no · fenómeno: discordancia sustantivo-adjetivo en objeto
- Llamada: 2026-11-18T10:56:57.264-06:00 · 6532 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "falla en la posición 4 ('nuevos'), regla «concordancia N–Adj»: 'libro' (m,sg) no concuerda con 'nuevos' (m,pl)",
  "razon": "no derivable con la gramática dada"
}
```
````

### [45] los gatos negra persiguen al ratón

- Nivel 2 · español correcto: no · fenómeno: discordancia sustantivo-adjetivo
- Llamada: 2026-11-18T10:57:03.798-06:00 · 5456 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "falla en la posición 2 ('negra'), regla «concordancia N–Adj»: 'gatos' (m,pl) no concuerda con 'negra' (f,sg)",
  "razon": "no derivable con la gramática dada"
}
```
````

### [46] come el pan

- Nivel 3 · español correcto: sí · fenómeno: sujeto tácito (pro-drop)
- Llamada: 2026-11-18T10:57:09.255-06:00 · 5834 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "restricción de sujeto explícito: sujeto omitido al inicio de la oración",
  "razon": "no derivable con la gramática dada"
}
```
````

### [47] llegó ayer

- Nivel 3 · español correcto: sí · fenómeno: sujeto tácito y adverbio fuera del léxico
- Llamada: 2026-11-18T10:57:15.090-06:00 · 5728 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "palabra(s) fuera del léxico: ayer",
  "razon": "no derivable con la gramática dada"
}
```
````

### [48] el gato la persigue

- Nivel 3 · español correcto: sí · fenómeno: pronombre clítico
- Llamada: 2026-11-18T10:57:20.820-06:00 · 2350 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": false, "arbol": null, "regla_que_falla": "palabra(s) fuera del léxico: la", "razon": "no derivable con la gramática dada"}
```
````

### [49] Juan y María leen un libro

- Nivel 3 · español correcto: sí · fenómeno: coordinación nominal
- Llamada: 2026-11-18T10:57:23.171-06:00 · 824 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "restricción de gramática: no hay coordinación",
  "razon": "no derivable con la gramática dada"
}
```
````

### [50] el gato come y duerme

- Nivel 3 · español correcto: sí · fenómeno: coordinación verbal
- Llamada: 2026-11-18T10:57:23.996-06:00 · 7028 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": false, "arbol": null, "regla_que_falla": "palabra(s) fuera del léxico: y", "razon": "no derivable con la gramática dada"}
```
````

### [51] el libro que el niño lee es nuevo

- Nivel 3 · español correcto: sí · fenómeno: relativa de objeto y verbo copulativo
- Llamada: 2026-11-18T10:57:31.025-06:00 · 13041 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "restricción «no hay verbos copulativos» o palabra fuera del léxico: es",
  "razon": "no derivable con la gramática dada"
}
```
````

### [52] el libro fue escrito por el profesor

- Nivel 3 · español correcto: sí · fenómeno: voz pasiva
- Llamada: 2026-11-18T10:57:44.067-06:00 · 3479 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "restricción: no hay pasivas, ni verbos copulativos (fue)",
  "razon": "no derivable con la gramática dada"
}
```
````

### [53] quiero que el gato corra

- Nivel 3 · español correcto: sí · fenómeno: primera persona y subjuntivo
- Llamada: 2026-11-18T10:57:47.547-06:00 · 48644 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": false, "arbol": null, "regla_que_falla": "palabra(s) fuera del léxico: quiero", "razon": "no derivable con la gramática dada"}
```
````

### [54] ¿dónde está el gato?

- Nivel 3 · español correcto: sí · fenómeno: interrogativa
- Llamada: 2026-11-18T10:58:36.193-06:00 · 8492 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "restricción de interrogativas (no permitidas) y palabra(s) fuera del léxico: dónde, está",
  "razon": "no derivable con la gramática dada"
}
```
````

### [55] el gato no come el pan

- Nivel 3 · español correcto: sí · fenómeno: negación
- Llamada: 2026-11-18T10:58:44.687-06:00 · 868 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "restricción violada: no hay negación; llegó 'no'",
  "razon": "no derivable con la gramática dada"
}
```
````

### [56] el gato es negro

- Nivel 3 · español correcto: sí · fenómeno: verbo copulativo
- Llamada: 2026-11-18T10:58:45.556-06:00 · 7849 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "restricción «no hay verbos copulativos»",
  "razon": "no derivable con la gramática dada"
}
```
````

### [57] yo veo a María

- Nivel 3 · español correcto: sí · fenómeno: primera persona y pronombre sujeto
- Llamada: 2026-11-18T10:58:53.407-06:00 · 1503 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "palabra(s) fuera del léxico: yo",
  "razon": "no derivable con la gramática dada"
}
```
````

### [58] se venden casas

- Nivel 3 · español correcto: sí · fenómeno: se impersonal/pasivo reflejo
- Llamada: 2026-11-18T10:58:54.911-06:00 · 1394 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "restricción «no hay clíticos ni pasivas», o palabra fuera del léxico: se",
  "razon": "no derivable con la gramática dada"
}
```
````

### [59] la niña que el gato persigue corre

- Nivel 3 · español correcto: sí · fenómeno: relativa de objeto (hueco en el objeto)
- Llamada: 2026-11-18T10:58:56.305-06:00 · 1067 ms
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
- Llamada: 2026-11-18T10:58:57.374-06:00 · 18769 ms
- Esperado (gramática): **RECHAZA** · LLM: **ACEPTA** · resultado: **desviación hacia el español**

Respuesta del LLM:

````text
```json
{"acepta": true, "arbol": "(O (SN (Det[m,sg] el) (N[m,sg] gato) (Rel (Que que) (SV (V[pres,sg] duerme) (SP (P en) (SN (Det[f,sg] la) (N[f,sg] casa) (Rel (Que que) (SV (V[pret,sg] compró) (Obj (SN (PN[m,sg,h] juan)))))))))) (SV (V[pres,sg] come) (SN (Det[m,sg] el) (N[m,sg] pan))))", "regla_que_falla": null, "razon": "derivable"}
```
````

### [61] el profesor lee más libros que la estudiante

- Nivel 3 · español correcto: sí · fenómeno: comparativa
- Llamada: 2026-11-18T10:59:16.144-06:00 · 1156 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": false, "arbol": null, "regla_que_falla": "palabra(s) fuera del léxico: más", "razon": "no derivable con la gramática dada"}
```
````

### [62] Juan y María son rubio y morena respectivamente

- Nivel 3 · español correcto: sí · fenómeno: dependencias cruzadas (respectivamente)
- Llamada: 2026-11-18T10:59:17.301-06:00 · 934 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "restricción «no hay coordinación, clíticos, negación, interrogativas, pasivas, ni verbos copulativos» o palabra(s) fuera del léxico: y, son, respectivamente",
  "razon": "no derivable con la gramática dada"
}
```
````

### [63] el gato duerme porque está cansado

- Nivel 3 · español correcto: sí · fenómeno: subordinada adverbial causal
- Llamada: 2026-11-18T10:59:18.237-06:00 · 6490 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": false, "arbol": null, "regla_que_falla": "palabra(s) fuera del léxico: porque, está", "razon": "no derivable con la gramática dada"}
```
````

### [64] cuando llegó Pedro los niños corrieron

- Nivel 3 · español correcto: sí · fenómeno: subordinada temporal antepuesta y sujeto pospuesto
- Llamada: 2026-11-18T10:59:24.728-06:00 · 6553 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": false, "arbol": null, "regla_que_falla": "palabra(s) fuera del léxico: cuando", "razon": "no derivable con la gramática dada"}
```
````

### [65] el libro come la casa

- Nivel 3 · español correcto: sí · fenómeno: anomalía semántica (sintácticamente correcta)
- Llamada: 2026-11-18T10:59:31.282-06:00 · 13622 ms
- Esperado (gramática): **ACEPTA** · LLM: **RECHAZA** · resultado: **sobre-rechazo**

Respuesta del LLM:

````text
```json
{"acepta": false, "arbol": null, "regla_que_falla": "regla de objeto «Obj → SN»: el núcleo de 'casa' es no animado (n), pero 'casa' es el objeto directo de un verbo ('come') que requiere un objeto directo sin la preposición 'a' (en esta gramática las restricciones semánticas de 'comer' exigen un objeto animado o compatible, o bien falla por el rasgo del Obj)", "razon": "no derivable con la gramática dada"}
```
````

### [66] la mesa duerme tranquilamente

- Nivel 3 · español correcto: sí · fenómeno: anomalía semántica (sintácticamente correcta)
- Llamada: 2026-11-18T10:59:44.905-06:00 · 889 ms
- Esperado (gramática): **ACEPTA** · LLM: **RECHAZA** · resultado: **sobre-rechazo**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "falla en la semántica del verbo o restricciones de selección de 'duerme': el verbo intransitivo 'duerme' requiere un sujeto animado o humano, pero 'mesa' es no animado (n)",
  "razon": "no derivable con la gramática dada"
}
```
````

### [67] el gato que corre persiguen al ratón

- Nivel 3 · español correcto: no · fenómeno: discordancia a distancia a través de una relativa
- Llamada: 2026-11-18T10:59:45.795-06:00 · 6991 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": false, "arbol": null, "regla_que_falla": "concordancia de número entre el SN y el SV de la O principal: 'el gato que corre' (sg) no coincide con 'persiguen' (pl)", "razon": "no derivable con la gramática dada"}
```
````

### [68] los niños que duerme corren

- Nivel 3 · español correcto: no · fenómeno: discordancia verbo-antecedente en relativa
- Llamada: 2026-11-18T10:59:52.787-06:00 · 718 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": false, "arbol": null, "regla_que_falla": "falla en la posición 3 ('duerme'), regla «Rel -> Que SV»: 'duerme' (pres,sg) no concuerda en número con el SN antecedente 'los niños' (m,pl)", "razon": "no derivable con la gramática dada"}
```
````

### [69] los niños de la escuela duerme

- Nivel 3 · español correcto: no · fenómeno: discordancia con atractor (sustantivo intermedio)
- Llamada: 2026-11-18T10:59:53.506-06:00 · 935 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": false, "arbol": null, "regla_que_falla": "concordancia SN–SV", "razon": "el sujeto 'los niños de la escuela' es plural (m,pl) y el verbo 'duerme' es singular (sg)"}
```
````

### [70] la niña que lee el libro corren

- Nivel 3 · español correcto: no · fenómeno: discordancia a distancia tras relativa con objeto
- Llamada: 2026-11-18T10:59:54.441-06:00 · 6246 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": false, "arbol": null, "regla_que_falla": "concordancia de número entre SN y V", "razon": "el sujeto 'la niña que lee el libro' es singular (f,sg) y el verbo 'corren' es plural (pl)"}
```
````

### [71] el gato persigue al ratón con con

- Nivel 3 · español correcto: no · fenómeno: secuencia agramatical de preposiciones
- Llamada: 2026-11-18T11:00:00.688-06:00 · 1276 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "falla en la posición 7 ('con'), regla «SP → P SN»: se esperaba un sintagma nominal después de la preposición 'con'",
  "razon": "no derivable con la gramática dada"
}
```
````
