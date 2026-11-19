# Respuestas del LLM — variante few_shot

- Proveedor: gemini · modelo: gemini-3.5-flash-lite (la API reporta: gemini-3.5-flash-lite)
- SDK: google-genai 3.5.0
- Parámetros: temperature = 0 · max_tokens = 4096
- Prompt: `casos/espanol/prompts/few_shot.txt` · instrucciones de sistema: sí · ejemplos resueltos: 6
- Primera llamada: 2026-11-18T23:10:57.661-06:00 · última llamada: 2026-11-18T23:14:51.490-06:00
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
- Llamada: 2026-11-18T23:10:57.661-06:00 · 2515 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,sg] el) (N[m,sg,a] gato)) (SV (V[pres,sg,tr] persigue) (Obj (A a) (SN (Det[m,sg] el) (N[m,sg,a] ratón)))))",
  "regla_que_falla": null,
  "razon": "derivable; 'al' se convierte en 'a el', y el objeto directo de un animal (ratón) puede emplear la forma con 'a'."
}
```
````

### [02] la niña lee un libro

- Nivel 1 · español correcto: sí · fenómeno: SVO simple
- Llamada: 2026-11-18T23:11:00.177-06:00 · 702 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[f,sg] la) (N[f,sg] niña)) (SV (V[pres,sg] lee) (SN (Det[m,sg] un) (N[m,sg] libro))))",
  "regla_que_falla": null,
  "razon": "derivable"
}
```
````

### [03] el profesor escribe una carta

- Nivel 1 · español correcto: sí · fenómeno: SVO simple
- Llamada: 2026-11-18T23:11:00.879-06:00 · 1848 ms
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
- Llamada: 2026-11-18T23:11:02.729-06:00 · 1512 ms
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
- Llamada: 2026-11-18T23:11:04.242-06:00 · 1407 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[f,sg] la) (N[f,sg] mujer)) (SV (V[pres,sg] abre) (SN (Det[f,sg] la) (N[f,sg] puerta))))",
  "regla_que_falla": null,
  "razon": "derivable"
}
```
````

### [06] el perro mira al niño

- Nivel 1 · español correcto: sí · fenómeno: SVO con a personal humano
- Llamada: 2026-11-18T23:11:05.650-06:00 · 846 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,sg] el) (N[m,sg] perro)) (SV (V[pres,sg] mira) (Obj (A a) (SN (Det[m,sg] el) (N[m,sg] niño)))))",
  "regla_que_falla": null,
  "razon": "derivable tras la expansión de 'al' a 'a el'"
}
```
````

### [07] María compra una manzana

- Nivel 1 · español correcto: sí · fenómeno: SVO con nombre propio
- Llamada: 2026-11-18T23:11:06.496-06:00 · 764 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (PN[f,sg,h] maría)) (SV (V[pres,sg] compra) (SN (Det[f,sg] una) (N[f,sg,n] manzana))))",
  "regla_que_falla": null,
  "razon": "derivable"
}
```
````

### [08] Juan ve a Ana

- Nivel 1 · español correcto: sí · fenómeno: SVO con nombres propios y a personal
- Llamada: 2026-11-18T23:11:07.261-06:00 · 848 ms
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
- Llamada: 2026-11-18T23:11:08.110-06:00 · 919 ms
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
- Llamada: 2026-11-18T23:11:09.031-06:00 · 884 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": true, "arbol": "(O (SN (Det[m,pl] los) (N[m,pl] pájaros)) (SV (V[pres,pl] cantan)))", "regla_que_falla": null, "razon": "derivable"}
```
````

### [11] la niña duerme

- Nivel 1 · español correcto: sí · fenómeno: intransitiva
- Llamada: 2026-11-18T23:11:09.915-06:00 · 955 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[f,sg] la) (N[f,sg] niña)) (SV (V[pres,sg] duerme)))",
  "regla_que_falla": null,
  "razon": "derivable"
}
```
````

### [12] el profesor llegó

- Nivel 1 · español correcto: sí · fenómeno: intransitiva pretérito
- Llamada: 2026-11-18T23:11:10.871-06:00 · 912 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,sg] el) (N[m,sg,h] profesor)) (SV (V[pret,sg] llegó)))",
  "regla_que_falla": null,
  "razon": "derivable"
}
```
````

### [13] las gatas comieron el pan

- Nivel 1 · español correcto: sí · fenómeno: SVO pretérito plural
- Llamada: 2026-11-18T23:11:11.784-06:00 · 838 ms
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
- Llamada: 2026-11-18T23:11:12.622-06:00 · 792 ms
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
- Llamada: 2026-11-18T23:11:13.415-06:00 · 820 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": true, "arbol": "(O (SN (Det[m,pl] los) (N[mf,pl,h] estudiantes)) (SV (V[pret,pl] escribieron) (SN (Det[f,pl] las) (N[f,pl,n] cartas))))", "regla_que_falla": null, "razon": "derivable"}
```
````

### [16] el perro persiguió al gato

- Nivel 1 · español correcto: sí · fenómeno: SVO pretérito
- Llamada: 2026-11-18T23:11:14.235-06:00 · 772 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": true, "arbol": "(O (SN (Det[m,sg] el) (N[m,sg] perro)) (SV (V[pret,sg] persiguió) (Obj (A a) (SN (Det[m,sg] el) (N[m,sg] gato)))))", "regla_que_falla": null, "razon": "derivable"}
```
````

### [17] la profesora abre la ventana

- Nivel 1 · español correcto: sí · fenómeno: SVO simple
- Llamada: 2026-11-18T23:11:15.008-06:00 · 742 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[f,sg] la) (N[f,sg] profesora)) (SV (V[pres,sg] abre) (SN (Det[f,sg] la) (N[f,sg] ventana))))",
  "regla_que_falla": null,
  "razon": "derivable"
}
```
````

### [18] Ana compró una casa

- Nivel 1 · español correcto: sí · fenómeno: SVO pretérito con nombre propio
- Llamada: 2026-11-18T23:11:15.750-06:00 · 902 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (PN[f,sg,h] Ana)) (SV (V[pret,sg] compró) (SN (Det[f,sg] una) (N[f,sg,n] casa))))",
  "regla_que_falla": null,
  "razon": "derivable"
}
```
````

### [19] los niños corrieron

- Nivel 1 · español correcto: sí · fenómeno: intransitiva pretérito plural
- Llamada: 2026-11-18T23:11:16.653-06:00 · 810 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": true, "arbol": "(O (SN (Det[m,pl] los) (N[m,pl] niños)) (SV (V[pret,pl] corrieron)))", "regla_que_falla": null, "razon": "derivable"}
```
````

### [20] el hombre trabaja

- Nivel 1 · español correcto: sí · fenómeno: intransitiva
- Llamada: 2026-11-18T23:11:17.464-06:00 · 11130 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,sg] el) (N[m,sg,h] hombre)) (SV (V[pres,sg] trabaja)))",
  "regla_que_falla": null,
  "razon": "derivable"
}
```
````

### [21] el gato negro persigue al ratón blanco

- Nivel 2 · español correcto: sí · fenómeno: adjetivos pospuestos
- Llamada: 2026-11-18T23:11:28.595-06:00 · 31890 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,sg] el) (N[m,sg] gato) (Adj[m,sg] negro)) (SV (V[pres,sg] persigue) (Obj (P a) (SN (Det[m,sg] el) (N[m,sg] ratón) (Adj[m,sg] blanco)))))",
  "regla_que_falla": null,
  "razon": "derivable"
}
```
````

### [22] la niña pequeña lee un libro nuevo

- Nivel 2 · español correcto: sí · fenómeno: adjetivos en sujeto y objeto
- Llamada: 2026-11-18T23:12:00.486-06:00 · 5372 ms
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
- Llamada: 2026-11-18T23:12:05.859-06:00 · 867 ms
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
- Llamada: 2026-11-18T23:12:06.726-06:00 · 952 ms
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
- Llamada: 2026-11-18T23:12:07.679-06:00 · 954 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": true, "arbol": "(O (SN (Det[f,sg] la) (N[f,sg] niña)) (SV (V[pres,sg] escribe) (SN (Det[f,sg] la) (N[f,sg] carta)) (Adv lentamente)))", "regla_que_falla": null, "razon": "derivable"}
```
````

### [26] el gato duerme tranquilamente

- Nivel 2 · español correcto: sí · fenómeno: adverbio con intransitivo
- Llamada: 2026-11-18T23:12:08.634-06:00 · 697 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": true, "arbol": "(O (SN (Det[m,sg] el) (N[m,sg] gato)) (SV (V[pres,sg] duerme) (Adv tranquilamente)))", "regla_que_falla": null, "razon": "derivable"}
```
````

### [27] los niños cansados llegaron a la escuela

- Nivel 2 · español correcto: sí · fenómeno: frase preposicional con intransitivo
- Llamada: 2026-11-18T23:12:09.332-06:00 · 726 ms
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
- Llamada: 2026-11-18T23:12:10.058-06:00 · 809 ms
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
- Llamada: 2026-11-18T23:12:10.869-06:00 · 971 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": true, "arbol": "(O (SN (Det[m,sg] el) (N[m,sg,h] hombre)) (SV (V[pres,sg,tr] ve) (Obj (A a) (SN (Det[m,sg] el) (N[m,sg,a] gato))) (SP (P con) (SN (Det[m,sg] el) (N[m,sg,n] telescopio)))))", "regla_que_falla": null, "razon": "derivable"}
```
````

### [30] el profesor mira a la niña con el libro

- Nivel 2 · español correcto: sí · fenómeno: ambigüedad por adjunción de FP (2 árboles)
- Llamada: 2026-11-18T23:12:11.841-06:00 · 813 ms
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
- Llamada: 2026-11-18T23:12:12.654-06:00 · 789 ms
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
- Llamada: 2026-11-18T23:12:13.444-06:00 · 804 ms
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
- Llamada: 2026-11-18T23:12:14.249-06:00 · 882 ms
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
- Llamada: 2026-11-18T23:12:15.132-06:00 · 11279 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (PN[m,sg,h] juan)) (SV (V[pres,sg] piensa) (Que que) (O (SN (Det[m,pl] los) (N[m,pl] niños)) (SV (V[pres,pl] duermen)))))",
  "regla_que_falla": null,
  "razon": "derivable"
}
```
````

### [35] los estudiantes jóvenes escribieron una carta grande para la profesora

- Nivel 2 · español correcto: sí · fenómeno: adjetivos mf y frase preposicional
- Llamada: 2026-11-18T23:12:26.411-06:00 · 31323 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": true, "arbol": "(O (SN (Det[m,pl] los) (N[m,pl] estudiantes) (Adj[mf,pl] jóvenes)) (SV (V[pret,pl] escribieron) (SN (Det[f,sg] una) (N[f,sg] carta) (Adj[f,sg] grande)) (SP (P para) (SN (Det[f,sg] la) (N[f,sg] profesora)))))", "regla_que_falla": null, "razon": "derivable"}
```
````

### [36] la gatos negros persiguen al ratón

- Nivel 2 · español correcto: no · fenómeno: discordancia determinante-sustantivo
- Llamada: 2026-11-18T23:12:57.736-06:00 · 939 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": false, "arbol": null, "regla_que_falla": "falla en la posición 1 ('gatos'), regla «concordancia Det–N»: 'la' (f,sg) no concuerda con 'gatos' (m,pl)", "razon": "no derivable con la gramática dada"}
```
````

### [37] el gato negro persiguen al ratón

- Nivel 2 · español correcto: no · fenómeno: discordancia sujeto-verbo
- Llamada: 2026-11-18T23:12:58.676-06:00 · 792 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "número de SN y de V deben coincidir",
  "razon": "el sujeto 'el gato negro' es singular (m,sg) pero el verbo 'persiguen' es plural (pl), violando la regla de concordancia de número entre SN y SV"
}
```
````

### [38] los niños duerme

- Nivel 2 · español correcto: no · fenómeno: discordancia sujeto-verbo
- Llamada: 2026-11-18T23:12:59.468-06:00 · 912 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "falla en la posición 2 ('duerme'), regla «O → SN SV»: el número del SN ('los niños': pl) y el del V ('duerme': sg) no coinciden",
  "razon": "no derivable con la gramática dada"
}
```
````

### [39] las niñas pequeño leen un libro

- Nivel 2 · español correcto: no · fenómeno: discordancia sustantivo-adjetivo
- Llamada: 2026-11-18T23:13:00.382-06:00 · 748 ms
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
- Llamada: 2026-11-18T23:13:01.131-06:00 · 691 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": false, "arbol": null, "regla_que_falla": "falla en la posición 1 ('niña'), regla «concordancia Det–N»: 'el' (m,sg) no concuerda con 'niña' (f,sg)", "razon": "no derivable con la gramática dada"}
```
````

### [41] una gato corre

- Nivel 2 · español correcto: no · fenómeno: discordancia de género det-sustantivo
- Llamada: 2026-11-18T23:13:01.822-06:00 · 668 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": false, "arbol": null, "regla_que_falla": "falla en la posición 1 ('gato'), regla «concordancia Det–N»: 'una' (f,sg) no concuerda con 'gato' (m,sg)", "razon": "no derivable con la gramática dada"}
```
````

### [42] gato el persigue ratón el

- Nivel 2 · español correcto: no · fenómeno: orden de palabras alterado
- Llamada: 2026-11-18T23:13:02.492-06:00 · 762 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "falla en la posición 0 ('gato'), regla «O → SN SV»: orden de palabras no válido para la estructura de SN",
  "razon": "no derivable con la gramática dada"
}
```
````

### [43] el persigue gato al ratón

- Nivel 2 · español correcto: no · fenómeno: orden de palabras alterado
- Llamada: 2026-11-18T23:13:03.255-06:00 · 920 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "falla en la posición 1 ('persigue'), regla «SV → V Obj ...»: la estructura sintáctica no puede derivarse en ese orden para 'el persigue gato al ratón'",
  "razon": "no derivable con la gramática dada"
}
```
````

### [44] la niña lee un libro nuevos

- Nivel 2 · español correcto: no · fenómeno: discordancia sustantivo-adjetivo en objeto
- Llamada: 2026-11-18T23:13:04.176-06:00 · 820 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": false, "arbol": null, "regla_que_falla": "falla en la posición 4 ('nuevos'), regla «concordancia Det–N y Adj–N»: 'nuevos' (m,pl) no concuerda con 'libro' (m,sg)", "razon": "no derivable con la gramática dada"}
```
````

### [45] los gatos negra persiguen al ratón

- Nivel 2 · español correcto: no · fenómeno: discordancia sustantivo-adjetivo
- Llamada: 2026-11-18T23:13:04.997-06:00 · 952 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "falla en la posición 2 ('negra'), regla «Det y N concuerdan en género y número; cada Adj concuerda con N»: 'negra' (f,sg) no concuerda con 'gatos' (m,pl)",
  "razon": "no derivable con la gramática dada"
}
```
````

### [46] come el pan

- Nivel 3 · español correcto: sí · fenómeno: sujeto tácito (pro-drop)
- Llamada: 2026-11-18T23:13:05.950-06:00 · 768 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "restricción «sujeto SIEMPRE explícito»",
  "razon": "no derivable con la gramática dada"
}
```
````

### [47] llegó ayer

- Nivel 3 · español correcto: sí · fenómeno: sujeto tácito y adverbio fuera del léxico
- Llamada: 2026-11-18T23:13:06.719-06:00 · 808 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "restricción: sujeto SIEMPRE explícito / regla «O -> SN SV»: falta el sujeto explícito",
  "razon": "no derivable con la gramática dada"
}
```
````

### [48] el gato la persigue

- Nivel 3 · español correcto: sí · fenómeno: pronombre clítico
- Llamada: 2026-11-18T23:13:07.527-06:00 · 1104 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "restricción: \"no hay coordinación, clíticos, negación, interrogativas, pasivas, ni verbos copulativos\" (aparición del clítico 'la')",
  "razon": "no derivable con la gramática dada"
}
```
````

### [49] Juan y María leen un libro

- Nivel 3 · español correcto: sí · fenómeno: coordinación nominal
- Llamada: 2026-11-18T23:13:08.632-06:00 · 675 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "restricción «no hay coordinación»: 'y'",
  "razon": "no derivable con la gramática dada"
}
```
````

### [50] el gato come y duerme

- Nivel 3 · español correcto: sí · fenómeno: coordinación verbal
- Llamada: 2026-11-18T23:13:09.308-06:00 · 762 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": false, "arbol": null, "regla_que_falla": "palabra(s) fuera del léxico: y", "razon": "no derivable con la gramática dada"}
```
````

### [51] el libro que el niño lee es nuevo

- Nivel 3 · español correcto: sí · fenómeno: relativa de objeto y verbo copulativo
- Llamada: 2026-11-18T23:13:10.070-06:00 · 931 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "palabra(s) fuera del léxico / gramática: es (o ausencia de verbos copulativos)",
  "razon": "no derivable con la gramática dada"
}
```
````

### [52] el libro fue escrito por el profesor

- Nivel 3 · español correcto: sí · fenómeno: voz pasiva
- Llamada: 2026-11-18T23:13:11.002-06:00 · 910 ms
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
- Llamada: 2026-11-18T23:13:11.913-06:00 · 1019 ms
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
- Llamada: 2026-11-18T23:13:12.933-06:00 · 620 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "restricción: interrogativas",
  "razon": "no derivable con la gramática dada"
}
```
````

### [55] el gato no come el pan

- Nivel 3 · español correcto: sí · fenómeno: negación
- Llamada: 2026-11-18T23:13:13.554-06:00 · 919 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "restricción violada: no hay negación",
  "razon": "no derivable con la gramática dada"
}
```
````

### [56] el gato es negro

- Nivel 3 · español correcto: sí · fenómeno: verbo copulativo
- Llamada: 2026-11-18T23:13:14.474-06:00 · 778 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "restricción «no hay verbos copulativos»: 'es' no pertenece al léxico de verbos o está prohibido",
  "razon": "no derivable con la gramática dada"
}
```
````

### [57] yo veo a María

- Nivel 3 · español correcto: sí · fenómeno: primera persona y pronombre sujeto
- Llamada: 2026-11-18T23:13:15.252-06:00 · 11072 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": false, "arbol": null, "regla_que_falla": "palabra(s) fuera del léxico: yo", "razon": "no derivable con la gramática dada"}
```
````

### [58] se venden casas

- Nivel 3 · español correcto: sí · fenómeno: se impersonal/pasivo reflejo
- Llamada: 2026-11-18T23:13:26.325-06:00 · 71845 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "palabra(s) fuera del léxico: se",
  "razon": "no derivable con la gramática dada"
}
```
````

### [59] la niña que el gato persigue corre

- Nivel 3 · español correcto: sí · fenómeno: relativa de objeto (hueco en el objeto)
- Llamada: 2026-11-18T23:14:38.171-06:00 · 836 ms
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
- Llamada: 2026-11-18T23:14:39.008-06:00 · 1347 ms
- Esperado (gramática): **RECHAZA** · LLM: **ACEPTA** · resultado: **desviación hacia el español**

Respuesta del LLM:

````text
```json
{"acepta": true, "arbol": "(O (SN (Det[m,sg] el) (N[m,sg] gato) (Rel (Que que) (SV (V[pres,sg] duerme) (SP (P en) (SN (Det[f,sg] la) (N[f,sg] casa) (Rel (Que que) (SV (V[pret,sg] compró) (SN (PN[m,sg,h] juan))))))))) (SV (V[pres,sg] come) (SN (Det[m,sg] el) (N[m,sg] pan))))", "regla_que_falla": null, "razon": "derivable"}
```
````

### [61] el profesor lee más libros que la estudiante

- Nivel 3 · español correcto: sí · fenómeno: comparativa
- Llamada: 2026-11-18T23:14:40.357-06:00 · 2736 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "palabra(s) fuera del léxico: más",
  "razon": "no derivable con la gramática dada"
}
```
````

### [62] Juan y María son rubio y morena respectivamente

- Nivel 3 · español correcto: sí · fenómeno: dependencias cruzadas (respectivamente)
- Llamada: 2026-11-18T23:14:43.093-06:00 · 727 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "palabra(s) fuera del léxico: y, son, rubio, morena, respectivamente",
  "razon": "no derivable con la gramática dada"
}
```
````

### [63] el gato duerme porque está cansado

- Nivel 3 · español correcto: sí · fenómeno: subordinada adverbial causal
- Llamada: 2026-11-18T23:14:43.821-06:00 · 721 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": false, "arbol": null, "regla_que_falla": "palabra(s) fuera del léxico: porque, está", "razon": "no derivable con la gramática dada"}
```
````

### [64] cuando llegó Pedro los niños corrieron

- Nivel 3 · español correcto: sí · fenómeno: subordinada temporal antepuesta y sujeto pospuesto
- Llamada: 2026-11-18T23:14:44.544-06:00 · 791 ms
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
- Llamada: 2026-11-18T23:14:45.335-06:00 · 2150 ms
- Esperado (gramática): **ACEPTA** · LLM: **RECHAZA** · resultado: **sobre-rechazo**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "Obj → SN: 'la casa' es no animado (n), por lo que Obj no puede ser SN simple sin la preposición 'a' (que solo aplica para humano, animal o PN, donde el humano la exige), pero además el verbo 'come' requiere un objeto válido y 'libro' (n) como sujeto no puede comer una casa sintácticamente de acuerdo con las restricciones semánticas o la regla Obj → SN requiere un objeto no animado o animal, sin embargo la regla de Obj dice 'solo si el núcleo de SN es no animado (n) o animal (a)' para Obj -> SN. Espere, 'casa' es no animado (n), por lo que 'la casa' sí cumple la condición de Obj -> SN. No obstante, 'come' es un verbo transitivo cuyo sujeto es 'el libro' (n). La gramática no restringe la animación del sujeto para 'come', sino del Obj. ¿Por qué se rechaza? Revisemos el léxico y las reglas: 'come' es tr. 'el libro' es SN m,sg,n. 'la casa' es SN f,sg,n. La regla Obj -> SN exige que el núcleo de SN sea no animado (n) o animal (a). 'casa' es (n). Entonces 'la casa' es un Obj válido. ¿Falla la concordancia? 'la' (f,sg) y 'casa' (f,sg). ¿Falla algo más? Ah, la restricción del objeto humano o no animado. Espere, 'libro' es n, 'casa' es n. Todo parece encajar estructuralmente en la gramática formal. ¿Por qué fallaría? Analicemos bien la regla de Obj: 'Obj -> SN [solo si el núcleo de SN es no animado (n) o animal (a)]'. 'casa' es (n). Entonces la estructura sintáctica es derivable. Acepta: true? ¡Espere! El prompt dice: 'si una oración es correcta en español pero la gramática no puede derivarla, debes RECHAZARLA; si la gramática la deriva aunque suene rara, debes ACEPTARLA.' Semánticamente 'el libro come la casa' es absurda en español, pero sintácticamente la gramática la deriva.",
  "razon": "derivable"
}
```
````

### [66] la mesa duerme tranquilamente

- Nivel 3 · español correcto: sí · fenómeno: anomalía semántica (sintácticamente correcta)
- Llamada: 2026-11-18T23:14:47.486-06:00 · 785 ms
- Esperado (gramática): **ACEPTA** · LLM: **RECHAZA** · resultado: **sobre-rechazo**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "falla en la posición 3 ('duerme'), restricción léxica de selección o semántica: el verbo 'duerme' requiere un sujeto animado o humano, pero el núcleo del SN es 'mesa' que es inanimado (n)",
  "razon": "no derivable con la gramática dada"
}
```
````

### [67] el gato que corre persiguen al ratón

- Nivel 3 · español correcto: no · fenómeno: discordancia a distancia a través de una relativa
- Llamada: 2026-11-18T23:14:48.272-06:00 · 682 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "falla en la regla 'O -> SN SV': el número del SN principal ('el gato que corre', sg) y el del V ('persiguen', pl) no coinciden",
  "razon": "no derivable con la gramática dada"
}
```
````

### [68] los niños que duerme corren

- Nivel 3 · español correcto: no · fenómeno: discordancia verbo-antecedente en relativa
- Llamada: 2026-11-18T23:14:48.955-06:00 · 753 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": false, "arbol": null, "regla_que_falla": "falla en la posición 3 ('duerme'), regla «Rel → Que SV (el verbo concuerda en número con el SN antecedente)»: 'duerme' (pres,sg) no concuerda con 'niños' (m,pl)", "razon": "no derivable con la gramática dada"}
```
````

### [69] los niños de la escuela duerme

- Nivel 3 · español correcto: no · fenómeno: discordancia con atractor (sustantivo intermedio)
- Llamada: 2026-11-18T23:14:49.709-06:00 · 660 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": false, "arbol": null, "regla_que_falla": "concordancia de número entre SN (los niños de la escuela, pl) y V (duerme, sg)", "razon": "no derivable con la gramática dada"}
```
````

### [70] la niña que lee el libro corren

- Nivel 3 · español correcto: no · fenómeno: discordancia a distancia tras relativa con objeto
- Llamada: 2026-11-18T23:14:50.370-06:00 · 1119 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": false, "arbol": null, "regla_que_falla": "concordancia de número entre SN sujeto y V en O: 'la niña que lee el libro' (sg) no concuerda con 'corren' (pl)", "razon": "no derivable con la gramática dada"}
```
````

### [71] el gato persigue al ratón con con

- Nivel 3 · español correcto: no · fenómeno: secuencia agramatical de preposiciones
- Llamada: 2026-11-18T23:14:51.490-06:00 · 566 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": false, "arbol": null, "regla_que_falla": "palabra repetida o malformación en la posición 6 ('con')", "razon": "no derivable con la gramática dada"}
```
````
