# Respuestas del LLM — variante sin_ejemplos

- Proveedor: gemini · modelo: gemini-3.5-flash-lite (la API reporta: gemini-3.5-flash-lite)
- SDK: google-genai 3.4.0
- Parámetros: temperature = 0 · max_tokens = 4096
- Prompt: `casos/espanol/prompts/sin_ejemplos.txt` · instrucciones de sistema: no · ejemplos resueltos: 0
- Primera llamada: 2026-11-18T10:26:37.128-06:00 · última llamada: 2026-11-18T10:35:17.386-06:00
- Oraciones analizadas: 71
- Log bruto (una línea JSON por llamada): `resultados/fase2/logs/llm_sin_ejemplos.jsonl`

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

Analiza esta oración:
Oración: {oracion}
````

## Respuestas

### [01] el gato persigue al ratón

- Nivel 1 · español correcto: sí · fenómeno: SVO simple (a personal con animal)
- Llamada: 2026-11-18T10:26:37.128-06:00 · 20715 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,sg] el) (N[m,sg,a] gato)) (SV (V[pres,sg,tr] persigue) (Obj (A a) (SN (Det[m,sg] el) (N[m,sg,a] ratón)))))",
  "regla_que_falla": null,
  "razon": "La oración es gramaticalmente correcta. El sujeto 'el gato' concuerda en número (singular) con el verbo 'persigue'. El objeto directo lleva la preposición 'a' ('al' = 'a el') requerida porque el núcleo del objeto ('ratón') es un animal ('a')."
}
```
````

### [02] la niña lee un libro

- Nivel 1 · español correcto: sí · fenómeno: SVO simple
- Llamada: 2026-11-18T10:26:57.843-06:00 · 7909 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[f,sg] la) (N[f,sg,h] niña)) (SV (V[pres,sg,tr] lee) (Obj (SN (Det[m,sg] un) (N[m,sg,n] libro)))))",
  "regla_que_falla": null,
  "razon": "La oración cumple estrictamente con todas las reglas gramaticales, de concordancia de género y número, y de selección de objeto (el objeto es no animado, por lo que no lleva la preposición 'a')."
}
```
````

### [03] el profesor escribe una carta

- Nivel 1 · español correcto: sí · fenómeno: SVO simple
- Llamada: 2026-11-18T10:27:05.754-06:00 · 7650 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,sg] el) (N[m,sg,h] profesor)) (SV (V[pres,sg,tr] escribe) (Obj (Det[f,sg] una) (N[f,sg,n] carta))))",
  "regla_que_falla": null,
  "razon": "La oración cumple estrictamente con todas las reglas gramaticales, de concordancia de género, número y persona, y las restricciones de animación del objeto directo."
}
```
````

### [04] los niños comen el pan

- Nivel 1 · español correcto: sí · fenómeno: SVO simple plural
- Llamada: 2026-11-18T10:27:13.405-06:00 · 7939 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,pl] los) (N[m,pl,h] niños)) (SV (V[pres,pl,tr] comen) (Obj (SN (Det[m,sg] el) (N[m,sg,n] pan)))))",
  "regla_que_falla": null,
  "razon": "La oración cumple con todas las reglas gramaticales, de concordancia de género y número, y de selección de objeto (pan es no animado)."
}
```
````

### [05] la mujer abre la puerta

- Nivel 1 · español correcto: sí · fenómeno: SVO simple
- Llamada: 2026-11-18T10:27:21.344-06:00 · 7354 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[f,sg] la) (N[f,sg,h] mujer)) (SV (V[pres,sg,tr] abre) (Obj (SN (Det[f,sg] la) (N[f,sg,n] puerta)))))",
  "regla_que_falla": null,
  "razon": "La oración cumple estrictamente con todas las reglas gramaticales, de concordancia de género y número, y de selección de objeto (puerta es no animado)."
}
```
````

### [06] el perro mira al niño

- Nivel 1 · español correcto: sí · fenómeno: SVO con a personal humano
- Llamada: 2026-11-18T10:27:28.699-06:00 · 1314 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,sg] el) (N[m,sg,a] perro)) (SV (V[pres,sg,tr] mira) (Obj (A a) (SN (Det[m,sg] el) (N[m,sg,h] niño)))))",
  "regla_que_falla": null,
  "razon": "La oración cumple con todas las reglas gramaticales, de concordancia, de selección de objeto (requiere 'a' por ser humano) y la contracción 'al' fue debidamente desglosada como 'a el'."
}
```
````

### [07] María compra una manzana

- Nivel 1 · español correcto: sí · fenómeno: SVO con nombre propio
- Llamada: 2026-11-18T10:27:30.014-06:00 · 7726 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (PN[f,sg,h] maría)) (SV (V[pres,sg,tr] compra) (Obj (SN (Det[f,sg] una) (N[f,sg,n] manzana)))))",
  "regla_que_falla": null,
  "razon": "La oración cumple estrictamente con todas las reglas gramaticales, restricciones de concordancia (género y número entre determinante y nombre, número entre sujeto y verbo) y el tipo de objeto adecuado para nombres no animados."
}
```
````

### [08] Juan ve a Ana

- Nivel 1 · español correcto: sí · fenómeno: SVO con nombres propios y a personal
- Llamada: 2026-11-18T10:27:37.740-06:00 · 7088 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (PN[m,sg,h] juan)) (SV (V[pres,sg,tr] ve) (Obj (A[a] a) (SN (PN[f,sg,h] ana)))))",
  "regla_que_falla": null,
  "razon": "La oración cumple con todas las reglas gramaticales, de concordancia, léxicas y de selección de objeto para entidades humanas."
}
```
````

### [09] el gato corre

- Nivel 1 · español correcto: sí · fenómeno: intransitiva
- Llamada: 2026-11-18T10:27:44.829-06:00 · 7583 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,sg] el) (N[m,sg,a] gato)) (SV (V[pres,sg,intr] corre)))",
  "regla_que_falla": null,
  "razon": "La oración cumple con todas las reglas gramaticales y de concordancia."
}
```
````

### [10] los pájaros cantan

- Nivel 1 · español correcto: sí · fenómeno: intransitiva plural
- Llamada: 2026-11-18T10:27:52.413-06:00 · 7560 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,pl] los) (N[m,pl,a] pájaros)) (SV (V[pres,pl,intr] cantan)))",
  "regla_que_falla": null,
  "razon": "La oración cumple estrictamente con las reglas gramaticales, la concordancia de número y género entre determinantes y nombres, y la correspondencia de persona y número entre el sujeto y el verbo intransitivo."
}
```
````

### [11] la niña duerme

- Nivel 1 · español correcto: sí · fenómeno: intransitiva
- Llamada: 2026-11-18T10:27:59.975-06:00 · 13901 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[f,sg] la) (N[f,sg,h] niña)) (SV (V[pres,sg,intr] duerme)))",
  "regla_que_falla": null,
  "razon": "La oración cumple con todas las reglas gramaticales y de concordancia: el determinante 'la' y el sustantivo 'niña' concuerdan en género (femenino) y número (singular), el sujeto y el verbo concuerdan en número (singular), y el verbo 'duerme' es intransitivo."
}
```
````

### [12] el profesor llegó

- Nivel 1 · español correcto: sí · fenómeno: intransitiva pretérito
- Llamada: 2026-11-18T10:28:13.878-06:00 · 2165 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,sg] el) (N[m,sg,h] profesor)) (SV (V[pres,sg,intr] llegó)))",
  "regla_que_falla": null,
  "razon": "La oración cumple con todas las reglas gramaticales, de concordancia y restricciones del léxico."
}
```
````

### [13] las gatas comieron el pan

- Nivel 1 · español correcto: sí · fenómeno: SVO pretérito plural
- Llamada: 2026-11-18T10:28:16.044-06:00 · 1021 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[f,pl] las) (N[f,pl,a] gatas)) (SV (V[pret,pl,tr] comieron) (Obj (SN (Det[m,sg] el) (N[m,sg,n] pan)))))",
  "regla_que_falla": null,
  "razon": "La oración es gramaticalmente correcta según las reglas y restricciones especificadas."
}
```
````

### [14] Pedro leyó un libro

- Nivel 1 · español correcto: sí · fenómeno: SVO pretérito
- Llamada: 2026-11-18T10:28:17.066-06:00 · 7559 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (PN[m,sg,h] pedro)) (SV (V[pret,sg,tr] leyó) (Obj (SN (Det[m,sg] un) (N[m,sg,n] libro)))))",
  "regla_que_falla": null,
  "razon": "La oración cumple estrictamente con todas las reglas gramaticales, restricciones de concordancia y de léxico."
}
```
````

### [15] los estudiantes escribieron las cartas

- Nivel 1 · español correcto: sí · fenómeno: SVO pretérito plural (sustantivo mf)
- Llamada: 2026-11-18T10:28:24.626-06:00 · 7021 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,pl] los) (N[m,pl,h] estudiantes)) (SV (V[pret,pl,tr] escribieron) (Obj (SN (Det[f,pl] las) (N[f,pl,n] cartas)))))",
  "regla_que_falla": null,
  "razon": "La oración es gramaticalmente correcta: el sujeto concuerda en número con el verbo, los determinantes y sustantivos concuerdan en género y número, el verbo transitivo está seguido de un objeto directo válido (no animado)."
}
```
````

### [16] el perro persiguió al gato

- Nivel 1 · español correcto: sí · fenómeno: SVO pretérito
- Llamada: 2026-11-18T10:28:31.649-06:00 · 1944 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,sg] el) (N[m,sg,a] perro)) (SV (V[pret,sg,tr] persiguió) (Obj (A a) (SN (Det[m,sg] el) (N[m,sg,a] gato)))))",
  "regla_que_falla": null,
  "razon": "La oración cumple estrictamente con todas las reglas gramaticales, de concordancia, de selección de objeto (animal con la preposición 'a') y restricciones léxicas."
}
```
````

### [17] la profesora abre la ventana

- Nivel 1 · español correcto: sí · fenómeno: SVO simple
- Llamada: 2026-11-18T10:28:33.594-06:00 · 6963 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[f,sg] la) (N[f,sg,h] profesora)) (SV (V[pres,sg,tr] abre) (Obj (SN (Det[f,sg] la) (N[f,sg,n] ventana)))))",
  "regla_que_falla": null,
  "razon": "La oración es gramaticalmente correcta: cumple con la concordancia de género y número entre determinante y nombre en ambos sintagmas nominales, el verbo transitivo está acompañado por un objeto directo válido (con nombre no animado), respeta la restricción de sujeto explícito y la concordancia de número entre el sujeto y el verbo."
}
```
````

### [18] Ana compró una casa

- Nivel 1 · español correcto: sí · fenómeno: SVO pretérito con nombre propio
- Llamada: 2026-11-18T10:28:40.558-06:00 · 1346 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (PN[f,sg,h] ana)) (SV (V[pret,sg,tr] compró) (Obj (Det[f,sg] una) (N[f,sg,n] casa))))",
  "regla_que_falla": null,
  "razon": "La oración cumple estrictamente con la gramática y el léxico proporcionados, respetando la concordancia de número entre el sujeto y el verbo, la selección del tipo de objeto según el rasgo de animación (casa es no animado, por lo que no requiere la preposición 'a') y los rasgos morfológicos."
}
```
````

### [19] los niños corrieron

- Nivel 1 · español correcto: sí · fenómeno: intransitiva pretérito plural
- Llamada: 2026-11-18T10:28:41.904-06:00 · 7257 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,pl] los) (N[m,pl,h] niños)) (SV (V[pret,pl] corrieron)))",
  "regla_que_falla": null,
  "razon": "La oración cumple con todas las reglas gramaticales, léxicas y de concordancia."
}
```
````

### [20] el hombre trabaja

- Nivel 1 · español correcto: sí · fenómeno: intransitiva
- Llamada: 2026-11-18T10:28:49.164-06:00 · 12778 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,sg] el) (N[m,sg,h] hombre)) (SV (V[pres,sg,intr] trabaja)))",
  "regla_que_falla": null,
  "razon": "La oración cumple con todas las reglas gramaticales, de concordancia y restricciones del sistema."
}
```
````

### [21] el gato negro persigue al ratón blanco

- Nivel 2 · español correcto: sí · fenómeno: adjetivos pospuestos
- Llamada: 2026-11-18T10:29:01.943-06:00 · 2046 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,sg] el) (N[m,sg,a] gato) (Adj[m,sg] negro)) (SV (V[pres,sg,tr] persigue) (Obj (A a) (SN (Det[m,sg] el) (N[m,sg,a] ratón) (Adj[m,sg] blanco)))))",
  "regla_que_falla": null,
  "razon": "La oración cumple estrictamente con todas las reglas gramaticales, restricciones de concordancia, tipos de verbos y el uso obligatorio de la preposición 'a' (que se funde en 'al') para el objeto directo animal."
}
```
````

### [22] la niña pequeña lee un libro nuevo

- Nivel 2 · español correcto: sí · fenómeno: adjetivos en sujeto y objeto
- Llamada: 2026-11-18T10:29:03.990-06:00 · 7137 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[f,sg] la) (N[f,sg,h] niña) (Adj[f,sg] pequeña)) (SV (V[pres,sg,tr] lee) (Obj (SN (Det[m,sg] un) (N[m,sg,n] libro) (Adj[m,sg] nuevo)))))",
  "regla_que_falla": null,
  "razon": "La oración cumple estrictamente con todas las reglas gramaticales, léxicas, de concordancia de género y número, y de selección de objeto (libro es no animado [n], por lo que usa la regla de Obj -> SN sin la preposición 'a')."
}
```
````

### [23] los gatos negros persiguen a los ratones

- Nivel 2 · español correcto: sí · fenómeno: adjetivo plural y a personal con animal
- Llamada: 2026-11-18T10:29:11.128-06:00 · 1684 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,pl] los) (N[m,pl,a] gatos) (Adj[m,pl] negros)) (SV (V[pres,pl,tr] persiguen) (Obj (A a) (SN (Det[m,pl] los) (N[m,pl,a] ratones)))))",
  "regla_que_falla": null,
  "razon": "La oración cumple estrictamente con todas las reglas gramaticales, de concordancia, de selección de objeto (ratones es animal 'a', por lo que exige la preposición 'a') y con las restricciones del léxico."
}
```
````

### [24] el profesor lee rápidamente la carta

- Nivel 2 · español correcto: sí · fenómeno: adverbio antes del objeto
- Llamada: 2026-11-18T10:29:12.813-06:00 · 7921 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,sg] el) (N[m,sg,h] profesor)) (SV (V[pres,sg,tr] lee) (Adv rápidamente) (Obj (Det[f,sg] la) (N[f,sg,n] carta))))",
  "regla_que_falla": null,
  "razon": "La oración cumple estrictamente con todas las reglas gramaticales, de concordancia, restricciones y léxico proporcionadas."
}
```
````

### [25] la niña escribe la carta lentamente

- Nivel 2 · español correcto: sí · fenómeno: adverbio después del objeto
- Llamada: 2026-11-18T10:29:20.736-06:00 · 7402 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[f,sg] la) (N[f,sg,h] niña)) (SV (V[pres,sg,tr] escribe) (Obj (SN (Det[f,sg] la) (N[f,sg,n] carta))) (Adv lentamente)))",
  "regla_que_falla": null,
  "razon": "La oración cumple estrictamente con todas las reglas gramaticales, restricciones, concordancias de género y número, y selección de rasgos léxicos."
}
```
````

### [26] el gato duerme tranquilamente

- Nivel 2 · español correcto: sí · fenómeno: adverbio con intransitivo
- Llamada: 2026-11-18T10:29:28.138-06:00 · 7803 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,sg] el) (N[m,sg,a] gato)) (SV (V[pres,sg,intr] duerme) (Adv tranquilamente)))",
  "regla_que_falla": null,
  "razon": "La oración cumple con todas las reglas gramaticales, de concordancia de género y número, y de selección léxica."
}
```
````

### [27] los niños cansados llegaron a la escuela

- Nivel 2 · español correcto: sí · fenómeno: frase preposicional con intransitivo
- Llamada: 2026-11-18T10:29:35.942-06:00 · 8341 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,pl] los) (N[m,pl,h] niños) (Adj[m,pl] cansados)) (SV (V[pret,pl,intr] llegaron) (SP (P a) (SN (Det[f,sg] la) (N[f,sg,n] escuela)))))",
  "regla_que_falla": null,
  "razon": "La oración cumple estrictamente con todas las reglas gramaticales, de concordancia en género y número, y de selección léxica."
}
```
````

### [28] la mujer compró el pan en la ciudad

- Nivel 2 · español correcto: sí · fenómeno: frase preposicional
- Llamada: 2026-11-18T10:29:44.291-06:00 · 1601 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[f,sg] la) (N[f,sg,h] mujer)) (SV (V[pret,sg,tr] compró) (Obj (SN (Det[m,sg] el) (N[m,sg,n] pan))) (SP (P en) (SN (Det[f,sg] la) (N[f,sg,n] ciudad)))))",
  "regla_que_falla": null,
  "razon": "La oración cumple estrictamente con todas las reglas gramaticales, de concordancia de género y número, la regla de objeto directo para entidades no animadas y las restricciones del léxico."
}
```
````

### [29] el hombre ve al gato con el telescopio

- Nivel 2 · español correcto: sí · fenómeno: ambigüedad por adjunción de FP (2 árboles)
- Llamada: 2026-11-18T10:29:45.894-06:00 · 8600 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": true, "arbol": "(O (SN (Det[m,sg] el) (N[m,sg,h] hombre)) (SV (V[pres,sg,tr] ve) (Obj (A a) (SN (Det[m,sg] el) (N[m,sg,a] gato))) (SP (P con) (SN (Det[m,sg] el) (N[m,sg,n] telescopio)))))", "regla_que_falla": null, "razon": "La oración es gramaticalmente correcta según las reglas y el léxico proporcionados."}
```
````

### [30] el profesor mira a la niña con el libro

- Nivel 2 · español correcto: sí · fenómeno: ambigüedad por adjunción de FP (2 árboles)
- Llamada: 2026-11-18T10:29:54.501-06:00 · 9258 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,sg] el) (N[m,sg,h] profesor)) (SV (V[pres,sg,tr] mira) (Obj (A a) (SN (Det[f,sg] la) (N[f,sg,h] niña) (SP (P con) (SN (Det[m,sg] el) (N[m,sg,n] libro)))))))",
  "regla_que_falla": null,
  "razon": "La oración cumple estrictamente con todas las reglas gramaticales, de concordancia de género y número, la exigencia de la preposición 'a' con objetos directos humanos, y las restricciones léxicas."
}
```
````

### [31] la gata que duerme come el pan

- Nivel 2 · español correcto: sí · fenómeno: relativa de sujeto
- Llamada: 2026-11-18T10:30:03.764-06:00 · 1280 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[f,sg] la) (N[f,sg,a] gata) (Rel (Que que) (SV (V[pres,sg] duerme)))) (SV (V[pres,sg,tr] come) (Obj (SN (Det[m,sg] el) (N[m,sg,n] pan)))))",
  "regla_que_falla": null,
  "razon": "La oración cumple con todas las reglas gramaticales, de concordancia, restricciones de animación y selección de argumentos."
}
```
````

### [32] el niño que lee el libro corre

- Nivel 2 · español correcto: sí · fenómeno: relativa de sujeto con objeto
- Llamada: 2026-11-18T10:30:05.046-06:00 · 8592 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,sg] el) (N[m,sg] niño) (Rel (Que que) (SV (V[pres,sg,tr] lee) (Obj (SN (Det[m,sg] el) (N[m,sg,n] libro)))))) (SV (V[pres,sg,intr] corre)))",
  "regla_que_falla": null,
  "razon": "La oración cumple con todas las reglas gramaticales y de concordancia: sujeto y verbo principal en singular, sujeto explícito, relativo correcto con concordancia de número, verbo transitivo con objeto inanimado válido y ausencia de restricciones violadas."
}
```
````

### [33] María dice que el gato corre

- Nivel 2 · español correcto: sí · fenómeno: completiva con que
- Llamada: 2026-11-18T10:30:13.641-06:00 · 942 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (PN[f,sg,h] maría)) (SV (V[pres,sg,comp] dice) (Que que) (O (SN (Det[m,sg] el) (N[m,sg,a] gato)) (SV (V[pres,sg,intr] corre)))))",
  "regla_que_falla": null,
  "razon": "La oración cumple con todas las reglas gramaticales, de concordancia, restricciones léxicas y de subcategorización del verbo tipo comp."
}
```
````

### [34] Juan piensa que los niños duermen

- Nivel 2 · español correcto: sí · fenómeno: completiva con que
- Llamada: 2026-11-18T10:30:14.584-06:00 · 8699 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (PN[m,sg,h] juan)) (SV (V[pres,sg,comp] piensa) (Que que) (O (SN (Det[m,pl] los) (N[m,pl,h] niños)) (SV (V[pres,pl,intr] duermen)))))",
  "regla_que_falla": null,
  "razon": "La oración cumple con todas las reglas gramaticales, de concordancia, restricciones de verbos tipo comp y de léxico."
}
```
````

### [35] los estudiantes jóvenes escribieron una carta grande para la profesora

- Nivel 2 · español correcto: sí · fenómeno: adjetivos mf y frase preposicional
- Llamada: 2026-11-18T10:30:23.287-06:00 · 2148 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,pl] los) (N[mf,pl,h] estudiantes) (Adj[mf,pl] jóvenes)) (SV (V[pret,pl,tr] escribieron) (Obj (Det[f,sg] una) (N[f,sg,n] carta) (Adj[f,sg] grande)) (SP (P para) (SN (Det[f,sg] la) (N[f,sg,h] profesora)))))",
  "regla_que_falla": null,
  "razon": "La oración cumple estrictamente con todas las reglas gramaticales y de concordancia en género, número y animación."
}
```
````

### [36] la gatos negros persiguen al ratón

- Nivel 2 · español correcto: no · fenómeno: discordancia determinante-sustantivo
- Llamada: 2026-11-18T10:30:25.436-06:00 · 7978 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "SN -> Det N Adj* SP* Rel?",
  "razon": "El determinante \"la\" (f,sg) y el sustantivo \"gatos\" (m,pl) no concuerdan en género y número."
}
```
````

### [37] el gato negro persiguen al ratón

- Nivel 2 · español correcto: no · fenómeno: discordancia sujeto-verbo
- Llamada: 2026-11-18T10:30:33.416-06:00 · 7947 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "O -> SN SV",
  "razon": "El número del sujeto ('el gato negro', singular) y el verbo ('persiguen', plural) no coinciden."
}
```
````

### [38] los niños duerme

- Nivel 2 · español correcto: no · fenómeno: discordancia sujeto-verbo
- Llamada: 2026-11-18T10:30:41.364-06:00 · 18016 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "O -> SN SV",
  "razon": "el número de SN (pl) y de V (sg) deben coincidir"
}
```
````

### [39] las niñas pequeño leen un libro

- Nivel 2 · español correcto: no · fenómeno: discordancia sustantivo-adjetivo
- Llamada: 2026-11-18T10:30:59.382-06:00 · 1172 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "SN -> Det N Adj* SP* Rel?",
  "razon": "El determinante 'las' (f,pl), el sustantivo 'niñas' (f,pl) y el adjetivo 'pequeño' (m,sg) no concuerdan en género y número."
}
```
````

### [40] el niña lee un libro

- Nivel 2 · español correcto: no · fenómeno: discordancia de género det-sustantivo
- Llamada: 2026-11-18T10:31:00.556-06:00 · 7630 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "SN -> Det N Adj* SP* Rel?",
  "razon": "El determinante 'el' (m,sg) y el sustantivo 'niña' (f,sg) no concuerdan en género."
}
```
````

### [41] una gato corre

- Nivel 2 · español correcto: no · fenómeno: discordancia de género det-sustantivo
- Llamada: 2026-11-18T10:31:08.187-06:00 · 7324 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "SN -> Det N Adj* SP* Rel?",
  "razon": "El determinante \"una\" (femenino, singular) no concuerda en género con el sustantivo \"gato\" (masculino, singular)."
}
```
````

### [42] gato el persigue ratón el

- Nivel 2 · español correcto: no · fenómeno: orden de palabras alterado
- Llamada: 2026-11-18T10:31:15.513-06:00 · 29552 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "SN -> Det N Adj* SP* Rel?",
  "razon": "El orden de los constituyentes en el sintagma nominal no es correcto (debería ser Det N y no N Det)."
}
```
````

### [43] el persigue gato al ratón

- Nivel 2 · español correcto: no · fenómeno: orden de palabras alterado
- Llamada: 2026-11-18T10:31:45.067-06:00 · 10351 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "SN -> Det N Adj* SP* Rel?",
  "razon": "El orden de las palabras en la oración es incorrecto según la gramática española; el objeto directo 'al ratón' interrumpe el sintagma nominal sujeto 'el gato'."
}
```
````

### [44] la niña lee un libro nuevos

- Nivel 2 · español correcto: no · fenómeno: discordancia sustantivo-adjetivo en objeto
- Llamada: 2026-11-18T10:31:55.420-06:00 · 8806 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "SN -> Det N Adj* SP* Rel?",
  "razon": "El adjetivo 'nuevos' (m,pl) no concuerda en género y número con el núcleo del SN 'niña' (f,sg)."
}
```
````

### [45] los gatos negra persiguen al ratón

- Nivel 2 · español correcto: no · fenómeno: discordancia sustantivo-adjetivo
- Llamada: 2026-11-18T10:32:04.227-06:00 · 8733 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "SN -> Det N Adj* SP* Rel?",
  "razon": "El adjetivo 'negra' (f,sg) no concuerda en género y número con el núcleo del sujeto 'gatos' (m,pl)."
}
```
````

### [46] come el pan

- Nivel 3 · español correcto: sí · fenómeno: sujeto tácito (pro-drop)
- Llamada: 2026-11-18T10:32:12.961-06:00 · 7984 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": false, "arbol": null, "regla_que_falla": "sujeto SIEMPRE explícito", "razon": "La oración no tiene un sujeto explícito."}
```
````

### [47] llegó ayer

- Nivel 3 · español correcto: sí · fenómeno: sujeto tácito y adverbio fuera del léxico
- Llamada: 2026-11-18T10:32:20.947-06:00 · 8052 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "Restricción: sujeto SIEMPRE explícito",
  "razon": "La oración no tiene un sujeto explícito."
}
```
````

### [48] el gato la persigue

- Nivel 3 · español correcto: sí · fenómeno: pronombre clítico
- Llamada: 2026-11-18T10:32:29.000-06:00 · 15087 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "Obj -> A SN",
  "razon": "El núcleo de SN en el objeto es 'gata' (rasgo 'a', animal), por lo que el objeto directo exige la forma 'A SN' ('a la gata'), pero en la oración falta la preposición 'a'."
}
```
````

### [49] Juan y María leen un libro

- Nivel 3 · español correcto: sí · fenómeno: coordinación nominal
- Llamada: 2026-11-18T10:32:44.089-06:00 · 7799 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "no hay coordinación",
  "razon": "La gramática prohíbe explícitamente la coordinación (como el uso de 'y')."
}
```
````

### [50] el gato come y duerme

- Nivel 3 · español correcto: sí · fenómeno: coordinación verbal
- Llamada: 2026-11-18T10:32:51.890-06:00 · 4077 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "no hay coordinación",
  "razon": "La oración contiene la conjunción coordinante 'y', lo cual infringe la restricción de que no hay coordinación."
}
```
````

### [51] el libro que el niño lee es nuevo

- Nivel 3 · español correcto: sí · fenómeno: relativa de objeto y verbo copulativo
- Llamada: 2026-11-18T10:32:55.968-06:00 · 7962 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "no hay verbos copulativos / LÉXICO: V",
  "razon": "La oración contiene el verbo copulativo 'es' (ser), el cual está excluido por las restricciones de la gramática."
}
```
````

### [52] el libro fue escrito por el profesor

- Nivel 3 · español correcto: sí · fenómeno: voz pasiva
- Llamada: 2026-11-18T10:33:03.931-06:00 · 7729 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "no hay pasivas / restricciones léxicas",
  "razon": "La oración contiene una estructura pasiva (\"fue escrito\"), la cual está explícitamente prohibida por las restricciones gramaticales."
}
```
````

### [53] quiero que el gato corra

- Nivel 3 · español correcto: sí · fenómeno: primera persona y subjuntivo
- Llamada: 2026-11-18T10:33:11.662-06:00 · 1059 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "Léxico",
  "razon": "La palabra 'quiero' no está en el léxico permitido o no cumple con la restricción de ser exclusivamente de 3.ª persona."
}
```
````

### [54] ¿dónde está el gato?

- Nivel 3 · español correcto: sí · fenómeno: interrogativa
- Llamada: 2026-11-18T10:33:12.721-06:00 · 9057 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "Restricciones: no hay interrogativas / Verbos copulativos",
  "razon": "La oración contiene una pregunta (interrogativa) y un verbo copulativo ('está'), los cuales están explícitamente prohibidos por las restricciones de la gramática."
}
```
````

### [55] el gato no come el pan

- Nivel 3 · español correcto: sí · fenómeno: negación
- Llamada: 2026-11-18T10:33:21.779-06:00 · 8476 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "no hay coordinación, clíticos, negación, interrogativas, pasivas, ni verbos copulativos",
  "razon": "La oración contiene la partícula de negación \"no\", la cual está explícitamente prohibida por las restricciones."
}
```
````

### [56] el gato es negro

- Nivel 3 · español correcto: sí · fenómeno: verbo copulativo
- Llamada: 2026-11-18T10:33:30.257-06:00 · 7695 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "no hay verbos copulativos",
  "razon": "La gramática prohíbe explícitamente el uso de verbos copulativos como 'es'."
}
```
````

### [57] yo veo a María

- Nivel 3 · español correcto: sí · fenómeno: primera persona y pronombre sujeto
- Llamada: 2026-11-18T10:33:37.953-06:00 · 8706 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "Restricciones",
  "razon": "El léxico y la gramática solo permiten la 3.ª persona, y el pronombre \"yo\" es de 1.ª persona (además de no estar incluido en el léxico)."
}
```
````

### [58] se venden casas

- Nivel 3 · español correcto: sí · fenómeno: se impersonal/pasivo reflejo
- Llamada: 2026-11-18T10:33:46.660-06:00 · 702 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "clíticos",
  "razon": "La gramática prohíbe explícitamente el uso de clíticos ('se')."
}
```
````

### [59] la niña que el gato persigue corre

- Nivel 3 · español correcto: sí · fenómeno: relativa de objeto (hueco en el objeto)
- Llamada: 2026-11-18T10:33:47.363-06:00 · 14250 ms
- Esperado (gramática): **RECHAZA** · LLM: **ACEPTA** · resultado: **desviación hacia el español**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[f,sg] la) (N[f,sg,h] niña) (Rel (Que que) (SV (SN (Det[m,sg] el) (N[m,sg,a] gato)) (SV (Obj (A a) (SN (Det[f,sg] la) (N[f,sg,h] niña))) (V[pres,sg,tr] persigue))))) (SV (V[pres,sg,intr] corre)))",
  "regla_que_falla": null,
  "razon": "La oración es gramaticalmente correcta y cumple con todas las restricciones de concordancia, tipología verbal y selección de objeto."
}
```
````

### [60] el gato que duerme en la casa que Juan compró come el pan

- Nivel 3 · español correcto: sí · fenómeno: doble relativa con objeto relativizado
- Llamada: 2026-11-18T10:34:01.615-06:00 · 1349 ms
- Esperado (gramática): **RECHAZA** · LLM: **ACEPTA** · resultado: **desviación hacia el español**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,sg] el) (N[m,sg,a] gato) (Rel (Que que) (SV (V[pres,sg,intr] duerme) (SP (P en) (SN (Det[f,sg] la) (N[f,sg,n] casa) (Rel (Que que) (SV (SN (PN[m,sg,h] juan)) (V[pret,sg,tr] compró)))))))) (SV (V[pres,sg,tr] come) (Obj (SN (Det[m,sg] el) (N[m,sg,n] pan)))))",
  "regla_que_falla": null,
  "razon": "La oración cumple estrictamente con todas las reglas gramaticales, restricciones de concordancia (género, número y persona), selección de objetos según animacidad y restricciones del léxico."
}
```
````

### [61] el profesor lee más libros que la estudiante

- Nivel 3 · español correcto: sí · fenómeno: comparativa
- Llamada: 2026-11-18T10:34:02.965-06:00 · 894 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "Reglas de léxico / Rel",
  "razon": "La palabra 'más' no está en el léxico de adverbios y la estructura 'que' seguida de SN no coincide con la regla de la oración de relativa (Rel -> Que SV)."
}
```
````

### [62] Juan y María son rubio y morena respectivamente

- Nivel 3 · español correcto: sí · fenómeno: dependencias cruzadas (respectivamente)
- Llamada: 2026-11-18T10:34:03.859-06:00 · 1743 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "no hay coordinación, clíticos, negación, interrogativas, pasivas, ni verbos copulativos.",
  "razon": "La oración contiene conjunciones coordinantes ('y'), verbos copulativos ('son') y elementos no permitidos por las restricciones gramaticales."
}
```
````

### [63] el gato duerme porque está cansado

- Nivel 3 · español correcto: sí · fenómeno: subordinada adverbial causal
- Llamada: 2026-11-18T10:34:05.603-06:00 · 7165 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "Léxico / Gramática",
  "razon": "La palabra 'porque' no está en el léxico permitido y las oraciones causales con 'estar' (verbo copulativo) no están permitidas."
}
```
````

### [64] cuando llegó Pedro los niños corrieron

- Nivel 3 · español correcto: sí · fenómeno: subordinada temporal antepuesta y sujeto pospuesto
- Llamada: 2026-11-18T10:34:12.769-06:00 · 8401 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "O -> SN SV",
  "razon": "La palabra 'cuando' no pertenece a ninguna categoría léxica permitida en la gramática y el sujeto no está al principio sin nexos temporales."
}
```
````

### [65] el libro come la casa

- Nivel 3 · español correcto: sí · fenómeno: anomalía semántica (sintácticamente correcta)
- Llamada: 2026-11-18T10:34:21.172-06:00 · 31432 ms
- Esperado (gramática): **ACEPTA** · LLM: **RECHAZA** · resultado: **sobre-rechazo**

Respuesta del LLM:

````text
```json
{"acepta": false, "arbol": null, "regla_que_falla": "Obj -> SN", "razon": "El objeto directo 'la casa' es inanimado pero el verbo 'come' requiere un sujeto animado/humano o el objeto infringe las restricciones de selección (un libro no come casas) y la regla de objeto exige que el SN no sea animado o animal, pero aquí el problema principal es que el núcleo del SN objeto ('casa') es inanimado y el verbo transitivo 'comer' lógicamente no concuerda, o bien viola la restricción semántica implícita en 'Obj' (solo si el núcleo de SN es no animado o animal, pero el verbo 'comer' exige sujeto y objeto compatibles; sin embargo, gramaticalmente 'libro' es inanimado (n)). Espera, revisemos las reglas de 'Obj': Obj -> SN [solo si el núcleo de SN es no animado (n) o animal (a)]. El núcleo de 'casa' es 'casa:f,sg,n' (no animado). Entonces sintácticamente la regla 'Obj -> SN' se cumple. Sin embargo, la regla general del SV para transitivos dice 'SV -> V Adv? Obj Adv? SP*'. ¿Dónde falla? El sujeto es 'el libro' (n). ¿Puede un libro comer? Léxico-semánticamente no, pero la gramática proporcionada es puramente sintáctica. Revisemos la regla de 'Obj': 'solo si el núcleo de SN es no animado (n) o animal (a)'. 'casa' es (n). Entonces, ¿por qué fallaría? Ah, el verbo 'come' es transitivo. ¿El objeto 'la casa' es no animado? Sí. ¿Falla otra cosa? 'el libro' es el sujeto. ¿El verbo 'come' concuerda con 'el libro'? Sí, pres,sg. ¿Falla la regla 'Obj -> SN'? No, 'casa' es n. ¿Falla la regla de selección? La gramática no especifica restricciones semánticas estrictas más allá de los rasgos (h, a, n). Entonces, ¿por qué no aceptarla? Espere, ¿'casa' es (n)? Sí. ¿'libro' es (n)? Sí. ¿'come' es tr? Sí. Entonces, sintácticamente la oración es estrictamente CORRECTA según estas reglas formales, aunque absurda semánticamente."}
```
````

### [66] la mesa duerme tranquilamente

- Nivel 3 · español correcto: sí · fenómeno: anomalía semántica (sintácticamente correcta)
- Llamada: 2026-11-18T10:34:52.606-06:00 · 7643 ms
- Esperado (gramática): **ACEPTA** · LLM: **RECHAZA** · resultado: **sobre-rechazo**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "Obj",
  "razon": "El verbo 'duerme' es intransitivo y no puede tener un objeto directo o indirecto, pero en este caso la violación proviene de la semántica de la combinación del sujeto inanimado con un verbo intransitivo de sujeto típicamente animado, o la restricción semántica del léxico."
}
```
````

### [67] el gato que corre persiguen al ratón

- Nivel 3 · español correcto: no · fenómeno: discordancia a distancia a través de una relativa
- Llamada: 2026-11-18T10:35:00.250-06:00 · 1852 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{"acepta": false, "arbol": null, "regla_que_falla": "O -> SN SV", "razon": "El número del sujeto ('el gato que corre', singular) y el del verbo ('persiguen', plural) no coinciden."}
```
````

### [68] los niños que duerme corren

- Nivel 3 · español correcto: no · fenómeno: discordancia verbo-antecedente en relativa
- Llamada: 2026-11-18T10:35:02.103-06:00 · 7501 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "Rel -> Que SV",
  "razon": "El verbo de la relativa 'duerme' (pres,sg) no concuerda en número con el SN antecedente 'los niños' (pl)."
}
```
````

### [69] los niños de la escuela duerme

- Nivel 3 · español correcto: no · fenómeno: discordancia con atractor (sustantivo intermedio)
- Llamada: 2026-11-18T10:35:09.607-06:00 · 6772 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "O -> SN SV",
  "razon": "El número del sujeto ('los niños', plural) y el verbo ('duerme', singular) no coinciden."
}
```
````

### [70] la niña que lee el libro corren

- Nivel 3 · español correcto: no · fenómeno: discordancia a distancia tras relativa con objeto
- Llamada: 2026-11-18T10:35:16.381-06:00 · 1004 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "O -> SN SV",
  "razon": "El número del sujeto ('la niña que lee el libro', singular) y el del verbo ('corren', plural) no coinciden."
}
```
````

### [71] el gato persigue al ratón con con

- Nivel 3 · español correcto: no · fenómeno: secuencia agramatical de preposiciones
- Llamada: 2026-11-18T10:35:17.386-06:00 · 6660 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "Reglas de léxico",
  "razon": "La palabra \"con\" aparece repetida al final de la oración, lo cual no forma una estructura sintáctica válida según la gramática."
}
```
````
