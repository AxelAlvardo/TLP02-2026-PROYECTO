# Respuestas del LLM — variante zero_shot

- Proveedor: gemini · modelo: gemini-3.5-flash-lite (la API reporta: gemini-3.5-flash-lite)
- SDK: google-genai 3.4.0
- Parámetros: temperature = 0 · max_tokens = 4096
- Prompt: `casos/espanol/prompts/zero_shot.txt` · instrucciones de sistema: sí · ejemplos resueltos: 0
- Primera llamada: 2026-11-18T10:45:20.656-06:00 · última llamada: 2026-11-18T10:52:18.634-06:00
- Oraciones analizadas: 71
- Log bruto (una línea JSON por llamada): `resultados/fase2/logs/llm_zero_shot.jsonl`

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

Analiza esta oración:
Oración: {oracion}
````

## Respuestas

### [01] el gato persigue al ratón

- Nivel 1 · español correcto: sí · fenómeno: SVO simple (a personal con animal)
- Llamada: 2026-11-18T10:45:20.656-06:00 · 6281 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,sg] el) (N[m,sg,a] gato)) (SV (V[pres,sg,tr] persigue) (Obj (A a) (SN (Det[m,sg] el) (N[m,sg,a] ratón)))))",
  "regla_que_falla": null,
  "razon": "La oración cumple estrictamente con todas las reglas gramaticales, de concordancia de género, número y persona, y respeta la exigencia de la forma 'a' con el objeto directo animal ('ratón'). 'al' se descompone correctamente en 'a el'."
}
```
````

### [02] la niña lee un libro

- Nivel 1 · español correcto: sí · fenómeno: SVO simple
- Llamada: 2026-11-18T10:45:26.939-06:00 · 1754 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[f,sg] la) (N[f,sg,h] niña)) (SV (V[pres,sg,tr] lee) (Obj (SN (Det[m,sg] un) (N[m,sg,n] libro)))))",
  "regla_que_falla": null,
  "razon": "La oración cumple estrictamente con la gramática: SN (Det N) + SV (V Tránsito + Obj SN no animado), con concordancia correcta de género, número y persona."
}
```
````

### [03] el profesor escribe una carta

- Nivel 1 · español correcto: sí · fenómeno: SVO simple
- Llamada: 2026-11-18T10:45:28.694-06:00 · 5409 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,sg] el) (N[m,sg,h] profesor)) (SV (V[pres,sg,tr] escribe) (Obj (SN (Det[f,sg] una) (N[f,sg,n] carta)))))",
  "regla_que_falla": null,
  "razon": "La oración cumple estrictamente con la gramática: SN (Det N) SV (V Obj(SN)) donde el profesor es un sujeto masculino singular válido para 'escribe' y 'una carta' es un objeto inanimado válido."
}
```
````

### [04] los niños comen el pan

- Nivel 1 · español correcto: sí · fenómeno: SVO simple plural
- Llamada: 2026-11-18T10:45:34.105-06:00 · 4960 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,pl] los) (N[m,pl,h] niños)) (SV (V[pres,pl,tr] comen) (Obj (SN (Det[m,sg] el) (N[m,sg,n] pan)))))",
  "regla_que_falla": null,
  "razon": "La oración cumple estrictamente con la gramática: sujeto explícito con concordancia de número (pl), verbo transitivo con objeto directo no animado sin preposición 'a'."
}
```
````

### [05] la mujer abre la puerta

- Nivel 1 · español correcto: sí · fenómeno: SVO simple
- Llamada: 2026-11-18T10:45:39.066-06:00 · 6347 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[f,sg] la) (N[f,sg,h] mujer)) (SV (V[pres,sg,tr] abre) (Obj (SN (Det[f,sg] la) (N[f,sg,n] puerta)))))",
  "regla_que_falla": null,
  "razon": "La oración cumple estrictamente con la gramática: SN (Det N) + SV (V Obj), con concordancia de número y persona (3ª sg), y el objeto inanimado cumple con la regla de Obj para sustantivos no animados."
}
```
````

### [06] el perro mira al niño

- Nivel 1 · español correcto: sí · fenómeno: SVO con a personal humano
- Llamada: 2026-11-18T10:45:45.415-06:00 · 8166 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,sg] el) (N[m,sg,a] perro)) (SV (V[pres,sg,tr] mira) (Obj (A a) (SN (Det[m,sg] el) (N[m,sg,h] niño)))))",
  "regla_que_falla": null,
  "razon": "La oración cumple con todas las reglas gramaticales y léxicas. Se ha expandido 'al' en 'a el' y el objeto humano 'niño' exige la presencia de 'a'."
}
```
````

### [07] María compra una manzana

- Nivel 1 · español correcto: sí · fenómeno: SVO con nombre propio
- Llamada: 2026-11-18T10:45:53.583-06:00 · 5044 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (PN[f,sg,h] maría)) (SV (V[pres,sg,tr] compra) (Obj (Det[f,sg] una) (N[f,sg,n] manzana))))",
  "regla_que_falla": null,
  "razon": "La oración es gramaticalmente correcta según las reglas y el léxico proporcionados."
}
```
````

### [08] Juan ve a Ana

- Nivel 1 · español correcto: sí · fenómeno: SVO con nombres propios y a personal
- Llamada: 2026-11-18T10:45:58.628-06:00 · 3972 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (PN[m,sg,h] juan)) (SV (V[pres,sg,tr] ve) (Obj (A a) (SN (PN[f,sg,h] ana)))))",
  "regla_que_falla": null,
  "razon": "La oración es gramaticalmente correcta según la gramática y el léxico proporcionados."
}
```
````

### [09] el gato corre

- Nivel 1 · español correcto: sí · fenómeno: intransitiva
- Llamada: 2026-11-18T10:46:02.602-06:00 · 5185 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,sg] el) (N[m,sg,a] gato)) (SV (V[pres,sg,intr] corre)))",
  "regla_que_falla": null,
  "razon": "La oración cumple estrictamente con todas las reglas de la gramática y el léxico proporcionados."
}
```
````

### [10] los pájaros cantan

- Nivel 1 · español correcto: sí · fenómeno: intransitiva plural
- Llamada: 2026-11-18T10:46:07.788-06:00 · 16868 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,pl] los) (N[m,pl,a] pájaros)) (SV (V[pres,pl,intr] cantan)))",
  "regla_que_falla": null,
  "razon": "La oración cumple con todas las reglas sintácticas, de concordancia de número entre el sujeto y el verbo, y de concordancia en género y número entre el determinante y el sustantivo."
}
```
````

### [11] la niña duerme

- Nivel 1 · español correcto: sí · fenómeno: intransitiva
- Llamada: 2026-11-18T10:46:24.657-06:00 · 1754 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[f,sg] la) (N[f,sg,h] niña)) (SV (V[pres,sg,intr] duerme)))",
  "regla_que_falla": null,
  "razon": "La oración cumple estrictamente con todas las reglas de la gramática, la concordancia de género y número entre Det y N, la concordancia de número entre el sujeto y el verbo, y la valencia del verbo intransitivo."
}
```
````

### [12] el profesor llegó

- Nivel 1 · español correcto: sí · fenómeno: intransitiva pretérito
- Llamada: 2026-11-18T10:46:26.413-06:00 · 830 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,sg] el) (N[m,sg,h] profesor)) (SV (V[pres,sg,intr] llegó)))",
  "regla_que_falla": null,
  "razon": "La oración cumple con todas las reglas de la gramática, concordancia de número y género entre el determinante y el núcleo del sujeto, la concordancia entre el sujeto y el verbo intransitivo, y las restricciones léxicas."
}
```
````

### [13] las gatas comieron el pan

- Nivel 1 · español correcto: sí · fenómeno: SVO pretérito plural
- Llamada: 2026-11-18T10:46:27.244-06:00 · 9556 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[f,pl] las) (N[f,pl,a] gatas)) (SV (V[pret,pl,tr] comieron) (Obj (SN (Det[m,sg] el) (N[m,sg,n] pan)))))",
  "regla_que_falla": null,
  "razon": "La oración cumple estrictamente con la gramática: SN (Det N concordantes en género y número femeninos plurales) + SV (verbo transitivo en pretérito plural) + Obj (SN con núcleo no animado precedido de determinante sin requerir la preposición 'a')."
}
```
````

### [14] Pedro leyó un libro

- Nivel 1 · español correcto: sí · fenómeno: SVO pretérito
- Llamada: 2026-11-18T10:46:36.800-06:00 · 6501 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (PN[m,sg,h] pedro)) (SV (V[pret,sg,tr] leyó) (Obj (SN (Det[m,sg] un) (N[m,sg,n] libro)))))",
  "regla_que_falla": null,
  "razon": "La oración cumple estrictamente con todas las reglas de la gramática, concordancias de número y género, transitividad del verbo y la restricción del objeto no animado."
}
```
````

### [15] los estudiantes escribieron las cartas

- Nivel 1 · español correcto: sí · fenómeno: SVO pretérito plural (sustantivo mf)
- Llamada: 2026-11-18T10:46:43.303-06:00 · 7037 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,pl] los) (N[mf,pl,h] estudiantes)) (SV (V[pret,pl,tr] escribieron) (Obj (A a) (SN (Det[f,pl] las) (N[f,pl,n] cartas)))))",
  "regla_que_falla": null,
  "razon": "La oración cumple con todas las reglas gramaticales y de léxico, incluyendo la concordancia de sujeto y verbo, y la exigencia de la preposición 'a' para el objeto directo humano."
}
```
````

### [16] el perro persiguió al gato

- Nivel 1 · español correcto: sí · fenómeno: SVO pretérito
- Llamada: 2026-11-18T10:46:50.342-06:00 · 5898 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,sg] el) (N[m,sg,a] perro)) (SV (V[pret,sg,tr] persiguió) (Obj (A a) (SN (Det[m,sg] el) (N[m,sg,a] gato)))))",
  "regla_que_falla": null,
  "razon": "La oración cumple con todas las restricciones sintácticas, de concordancia de género y número, y las reglas de los objetos directos con animales."
}
```
````

### [17] la profesora abre la ventana

- Nivel 1 · español correcto: sí · fenómeno: SVO simple
- Llamada: 2026-11-18T10:46:56.241-06:00 · 2033 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[f,sg] la) (N[f,sg,h] profesora)) (SV (V[pres,sg,tr] abre) (Obj (SN (Det[f,sg] la) (N[f,sg,n] ventana)))))",
  "regla_que_falla": null,
  "razon": "La oración cumple con todas las reglas gramaticales, de concordancia de género, número y persona, así como con las restricciones de animación del objeto directo."
}
```
````

### [18] Ana compró una casa

- Nivel 1 · español correcto: sí · fenómeno: SVO pretérito con nombre propio
- Llamada: 2026-11-18T10:46:58.276-06:00 · 1058 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (PN[f,sg,h] ana)) (SV (V[pret,sg,tr] compró) (Obj (Det[f,sg] una) (N[f,sg,n] casa))))",
  "regla_que_falla": null,
  "razon": "La oración cumple con todas las reglas gramaticales, de concordancia, restricciones de léxico y de animación para el objeto directo."
}
```
````

### [19] los niños corrieron

- Nivel 1 · español correcto: sí · fenómeno: intransitiva pretérito plural
- Llamada: 2026-11-18T10:46:59.334-06:00 · 5046 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,pl] los) (N[m,pl,h] niños)) (SV (V[pret,pl,intr] corrieron)))",
  "regla_que_falla": null,
  "razon": "La oración cumple con la concordancia de número entre el sujeto (los niños, plural) y el verbo (corrieron, pret,pl)."
}
```
````

### [20] el hombre trabaja

- Nivel 1 · español correcto: sí · fenómeno: intransitiva
- Llamada: 2026-11-18T10:47:04.382-06:00 · 906 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,sg] el) (N[m,sg,h] hombre)) (SV (V[pres,sg,intr] trabaja)))",
  "regla_que_falla": null,
  "razon": "La oración cumple estrictamente con todas las reglas sintácticas, de concordancia de género y número (singular masculino), y léxicas de la gramática."
}
```
````

### [21] el gato negro persigue al ratón blanco

- Nivel 2 · español correcto: sí · fenómeno: adjetivos pospuestos
- Llamada: 2026-11-18T10:47:05.289-06:00 · 20783 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,sg] el) (N[m,sg,a] gato) (Adj[m,sg] negro)) (SV (V[pres,sg,tr] persigue) (Obj (A a) (SN (Det[m,sg] el) (N[m,sg,a] ratón) (Adj[m,sg] blanco)))))",
  "regla_que_falla": null,
  "razon": "La oración es gramaticalmente correcta y cumple con todas las restricciones léxicas, de concordancia, de animación para objetos animales con la preposición 'a' (convertido desde 'al' por regla) y de estructura."
}
```
````

### [22] la niña pequeña lee un libro nuevo

- Nivel 2 · español correcto: sí · fenómeno: adjetivos en sujeto y objeto
- Llamada: 2026-11-18T10:47:26.075-06:00 · 1123 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[f,sg] la) (N[f,sg,h] niña) (Adj[f,sg] pequeña)) (SV (V[pres,sg,tr] lee) (Obj (SN (Det[m,sg] un) (N[m,sg,n] libro) (Adj[m,sg] nuevo)))))",
  "regla_que_falla": null,
  "razon": "La oración cumple estrictamente con las reglas sintácticas y de concordancia de género y número de la gramática."
}
```
````

### [23] los gatos negros persiguen a los ratones

- Nivel 2 · español correcto: sí · fenómeno: adjetivo plural y a personal con animal
- Llamada: 2026-11-18T10:47:27.198-06:00 · 804 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,pl] los) (N[m,pl,a] gatos) (Adj[m,pl] negros)) (SV (V[pres,pl,tr] persiguen) (Obj (A a) (SN (Det[m,pl] los) (N[m,pl,a] ratones)))))",
  "regla_que_falla": null,
  "razon": "La oración cumple estrictamente con todas las reglas gramaticales, de concordancia, léxicas y de restricciones."
}
```
````

### [24] el profesor lee rápidamente la carta

- Nivel 2 · español correcto: sí · fenómeno: adverbio antes del objeto
- Llamada: 2026-11-18T10:47:28.003-06:00 · 1089 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,sg] el) (N[m,sg,h] profesor)) (SV (V[pres,sg,tr] lee) (Adv rápidamente) (Obj (SN (Det[f,sg] la) (N[f,sg,n] carta)))))",
  "regla_que_falla": null,
  "razon": "La oración cumple estrictamente con todas las reglas sintácticas, de concordancia de género y número, animacidad para el objeto directo y el léxico de la gramática."
}
```
````

### [25] la niña escribe la carta lentamente

- Nivel 2 · español correcto: sí · fenómeno: adverbio después del objeto
- Llamada: 2026-11-18T10:47:29.093-06:00 · 5033 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[f,sg] la) (N[f,sg,h] niña)) (SV (V[pres,sg,tr] escribe) (Adv lentamente) (Obj (SN (Det[f,sg] la) (N[f,sg,n] carta)))))",
  "regla_que_falla": null,
  "razon": "La oración cumple estrictamente con todas las reglas sintácticas, de concordancia de género y número, la restricción de objeto humano (aquí el objeto es 'carta', que es no animado [n], por lo que no lleva la preposición 'a'), y utiliza únicamente elementos y categorías presentes en la gramática y el léxico proporcionados."
}
```
````

### [26] el gato duerme tranquilamente

- Nivel 2 · español correcto: sí · fenómeno: adverbio con intransitivo
- Llamada: 2026-11-18T10:47:34.127-06:00 · 5068 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,sg] el) (N[m,sg,a] gato)) (SV (V[pres,sg,intr] duerme) (Adv tranquilamente)))",
  "regla_que_falla": null,
  "razon": "La oración cumple estrictamente con todas las reglas de la gramática, concordancias de género, número y persona, y el uso correcto del léxico."
}
```
````

### [27] los niños cansados llegaron a la escuela

- Nivel 2 · español correcto: sí · fenómeno: frase preposicional con intransitivo
- Llamada: 2026-11-18T10:47:39.197-06:00 · 9242 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,pl] los) (N[m,pl] niños) (Adj[m,pl] cansados)) (SV (V[pret,pl,intr] llegaron) (SP (P a) (SN (Det[f,sg] la) (N[f,sg] escuela)))))",
  "regla_que_falla": null,
  "razon": "La oración cumple con todas las reglas gramaticales y de concordancia: el sujeto 'los niños cansados' concuerda en número (plural) y persona (3.ª) con el verbo 'llegaron', los determinantes y adjetivos concuerdan en género y número con sus respectivos sustantivos, y el verbo intransitivo 'llegar' acepta un sintagma preposicional (SP)."
}
```
````

### [28] la mujer compró el pan en la ciudad

- Nivel 2 · español correcto: sí · fenómeno: frase preposicional
- Llamada: 2026-11-18T10:47:48.440-06:00 · 1166 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[f,sg] la) (N[f,sg,h] mujer)) (SV (V[pret,sg,tr] compró) (Obj (SN (Det[m,sg] el) (N[m,sg,n] pan))) (SP (P en) (SN (Det[f,sg] la) (N[f,sg,n] ciudad)))))",
  "regla_que_falla": null,
  "razon": "La oración cumple estrictamente con la gramática, las restricciones de concordancia, rasgos semánticos (el objeto pan es no animado, por lo que no lleva 'a') y el léxico proporcionado."
}
```
````

### [29] el hombre ve al gato con el telescopio

- Nivel 2 · español correcto: sí · fenómeno: ambigüedad por adjunción de FP (2 árboles)
- Llamada: 2026-11-18T10:47:49.607-06:00 · 26540 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,sg] el) (N[m,sg,h] hombre)) (SV (V[pres,sg,tr] ve) (Obj (A a) (SN (Det[m,sg] el) (N[m,sg,a] gato))) (SP (P con) (SN (Det[m,sg] el) (N[m,sg,n] telescopio)))))",
  "regla_que_falla": null,
  "razon": "La oración cumple con todas las restricciones de la gramática y el léxico proporcionados, incluyendo la concordancia de número, género, el uso obligatorio de 'a' con objetos humanos, y la correcta expansión de los sintagmas."
}
```
````

### [30] el profesor mira a la niña con el libro

- Nivel 2 · español correcto: sí · fenómeno: ambigüedad por adjunción de FP (2 árboles)
- Llamada: 2026-11-18T10:48:16.148-06:00 · 8321 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,sg] el) (N[m,sg,h] profesor)) (SV (V[pres,sg,tr] mira) (Obj (A a) (SN (Det[f,sg] la) (N[f,sg,h] niña))) (SP (P con) (SN (Det[m,sg] el) (N[m,sg,n] libro)))))",
  "regla_que_falla": null,
  "razon": "La oración cumple estrictamente con la gramática formal, la concordancia de género, número, persona y tiempo, y las restricciones de objetos animados y humanos."
}
```
````

### [31] la gata que duerme come el pan

- Nivel 2 · español correcto: sí · fenómeno: relativa de sujeto
- Llamada: 2026-11-18T10:48:24.470-06:00 · 4232 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[f,sg] la) (N[f,sg,a] gata) (Rel (Que que) (SV (V[pres,sg,intr] duerme)))) (SV (V[pres,sg,tr] come) (Obj (SN (Det[m,sg] el) (N[m,sg,n] pan)))))",
  "regla_que_falla": null,
  "razon": "La oración es gramaticalmente correcta según las reglas de la gramática y el léxico proporcionados."
}
```
````

### [32] el niño que lee el libro corre

- Nivel 2 · español correcto: sí · fenómeno: relativa de sujeto con objeto
- Llamada: 2026-11-18T10:48:28.703-06:00 · 4630 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,sg] el) (N[m,sg,h] niño) (Rel (Que que) (SV (V[pres,sg,tr] lee) (Obj (SN (Det[m,sg] el) (N[m,sg,n] libro)))))) (SV (V[pres,sg,intr] corre)))",
  "regla_que_falla": null,
  "razon": "La oración es gramaticalmente correcta según las reglas de la gramática y el léxico proporcionados."
}
```
````

### [33] María dice que el gato corre

- Nivel 2 · español correcto: sí · fenómeno: completiva con que
- Llamada: 2026-11-18T10:48:33.335-06:00 · 4989 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (PN[f,sg,h] maría)) (SV (V[pres,sg,comp] dice) (Que que) (O (SN (Det[m,sg] el) (N[m,sg,a] gato)) (SV (V[pres,sg,intr] corre)))))",
  "regla_que_falla": null,
  "razon": "La oración es gramaticalmente correcta según las reglas y léxico proporcionados."
}
```
````

### [34] Juan piensa que los niños duermen

- Nivel 2 · español correcto: sí · fenómeno: completiva con que
- Llamada: 2026-11-18T10:48:38.326-06:00 · 4599 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (PN[m,sg,h] juan)) (SV (V[pres,sg,comp] piensa) (Que que) (O (SN (Det[m,pl] los) (N[m,pl,h] niños)) (SV (V[pres,pl,intr] duermen)))))",
  "regla_que_falla": null,
  "razon": "La oración cumple estrictamente con la gramática formal, las restricciones de concordancia (número y persona), la estructura de SV con verbos de tipo 'comp', y el léxico proporcionado."
}
```
````

### [35] los estudiantes jóvenes escribieron una carta grande para la profesora

- Nivel 2 · español correcto: sí · fenómeno: adjetivos mf y frase preposicional
- Llamada: 2026-11-18T10:48:42.925-06:00 · 6197 ms
- Esperado (gramática): **ACEPTA** · LLM: **ACEPTA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,pl] los) (N[mf,pl,h] estudiantes) (Adj[mf,pl] jóvenes)) (SV (V[pret,pl,tr] escribieron) (Obj (Det[f,sg] una) (N[f,sg,n] carta) (Adj[f,sg] grande)) (SP (P para) (SN (Det[f,sg] la) (N[f,sg,h] profesora)))))",
  "regla_que_falla": null,
  "razon": "La oración cumple con todas las restricciones de concordancia, léxico y sintaxis de la gramática."
}
```
````

### [36] la gatos negros persiguen al ratón

- Nivel 2 · español correcto: no · fenómeno: discordancia determinante-sustantivo
- Llamada: 2026-11-18T10:48:49.123-06:00 · 3343 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "SN -> Det N Adj* SP* Rel?",
  "razon": "El determinante 'la' (f,sg) y el núcleo 'gatos' (m,pl) no concuerdan en género ni número."
}
```
````

### [37] el gato negro persiguen al ratón

- Nivel 2 · español correcto: no · fenómeno: discordancia sujeto-verbo
- Llamada: 2026-11-18T10:48:52.467-06:00 · 1000 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "O -> SN SV [el número de SN y de V deben coincidir]",
  "razon": "El sujeto 'el gato negro' es singular (m,sg), pero el verbo 'persiguen' es plural (pl), por lo que no hay concordancia de número entre el SN y el V."
}
```
````

### [38] los niños duerme

- Nivel 2 · español correcto: no · fenómeno: discordancia sujeto-verbo
- Llamada: 2026-11-18T10:48:53.468-06:00 · 4293 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "O -> SN SV",
  "razon": "El número del SN (pl) y del verbo (sg) no coinciden."
}
```
````

### [39] las niñas pequeño leen un libro

- Nivel 2 · español correcto: no · fenómeno: discordancia sustantivo-adjetivo
- Llamada: 2026-11-18T10:48:57.762-06:00 · 7440 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "SN -> Det N Adj* SP* Rel?",
  "razon": "El adjetivo 'pequeño' (m,sg) no concuerda en género y número con el sustantivo 'niñas' (f,pl)."
}
```
````

### [40] el niña lee un libro

- Nivel 2 · español correcto: no · fenómeno: discordancia de género det-sustantivo
- Llamada: 2026-11-18T10:49:05.204-06:00 · 4197 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "SN -> Det N Adj* SP* Rel?",
  "razon": "El determinante 'el' (m,sg) y el nombre 'niña' (f,sg) no concuerdan en género."
}
```
````

### [41] una gato corre

- Nivel 2 · español correcto: no · fenómeno: discordancia de género det-sustantivo
- Llamada: 2026-11-18T10:49:09.402-06:00 · 4270 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "SN -> Det N Adj* SP* Rel?",
  "razon": "El determinante 'una' (f,sg) y el núcleo 'gato' (m,sg) no concuerdan en género."
}
```
````

### [42] gato el persigue ratón el

- Nivel 2 · español correcto: no · fenómeno: orden de palabras alterado
- Llamada: 2026-11-18T10:49:13.673-06:00 · 708 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "SN -> Det N Adj* SP* Rel?",
  "razon": "El orden de los componentes en el SN es incorrecto según la gramática (debe ser Det N, no N Det)."
}
```
````

### [43] el persigue gato al ratón

- Nivel 2 · español correcto: no · fenómeno: orden de palabras alterado
- Llamada: 2026-11-18T10:49:14.383-06:00 · 14776 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "SN -> Det N Adj* SP* Rel?",
  "razon": "La secuencia de palabras 'el persigue gato al ratón' no cumple con el orden gramatical de la oración transitiva, ya que el sujeto está interrumpido o el verbo está en posición incorrecta, o hay un error en el orden de los constituyentes del SN."
}
```
````

### [44] la niña lee un libro nuevos

- Nivel 2 · español correcto: no · fenómeno: discordancia sustantivo-adjetivo en objeto
- Llamada: 2026-11-18T10:49:29.160-06:00 · 5626 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "SN -> Det N Adj* SP* Rel?",
  "razon": "El adjetivo 'nuevos' (m,pl) no concuerda en género y número con el núcleo del SN 'libro' (m,sg)."
}
```
````

### [45] los gatos negra persiguen al ratón

- Nivel 2 · español correcto: no · fenómeno: discordancia sustantivo-adjetivo
- Llamada: 2026-11-18T10:49:34.787-06:00 · 5445 ms
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
- Llamada: 2026-11-18T10:49:40.233-06:00 · 5423 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "O -> SN SV",
  "razon": "La oración no tiene un sujeto (SN) explícito, lo cual es obligatorio según las restricciones."
}
```
````

### [47] llegó ayer

- Nivel 3 · español correcto: sí · fenómeno: sujeto tácito y adverbio fuera del léxico
- Llamada: 2026-11-18T10:49:45.658-06:00 · 1267 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "O -> SN SV",
  "razon": "La oración no tiene un sujeto (SN) explícito, lo cual es obligatorio según las restricciones."
}
```
````

### [48] el gato la persigue

- Nivel 3 · español correcto: sí · fenómeno: pronombre clítico
- Llamada: 2026-11-18T10:49:46.926-06:00 · 1518 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "Restricciones",
  "razon": "La oración contiene un clítico ('la'), lo cual está explícitamente prohibido por las restricciones."
}
```
````

### [49] Juan y María leen un libro

- Nivel 3 · español correcto: sí · fenómeno: coordinación nominal
- Llamada: 2026-11-18T10:49:48.446-06:00 · 792 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "no hay coordinación",
  "razon": "La gramática y las restricciones prohíben explícitamente la coordinación (la presencia de 'y')."
}
```
````

### [50] el gato come y duerme

- Nivel 3 · español correcto: sí · fenómeno: coordinación verbal
- Llamada: 2026-11-18T10:49:49.239-06:00 · 701 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "no hay coordinación",
  "razon": "La oración contiene la conjunción 'y', pero la gramática prohíbe explícitamente la coordinación."
}
```
````

### [51] el libro que el niño lee es nuevo

- Nivel 3 · español correcto: sí · fenómeno: relativa de objeto y verbo copulativo
- Llamada: 2026-11-18T10:49:49.940-06:00 · 1149 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "SV -> V Adv? SP* / V Adv? Obj Adv? SP* / V Que O",
  "razon": "El verbo 'es' no pertenece al léxico proporcionado (no hay verbos copulativos en la gramática)."
}
```
````

### [52] el libro fue escrito por el profesor

- Nivel 3 · español correcto: sí · fenómeno: voz pasiva
- Llamada: 2026-11-18T10:49:51.090-06:00 · 7427 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "SV -> V Adv? SP* / pasivas",
  "restriccion_violada": "no hay pasivas",
  "razon": "La oración contiene una estructura pasiva ('fue escrito por'), la cual está explícitamente prohibida en las restricciones y no es generada por las reglas de SV."
}
```
````

### [53] quiero que el gato corra

- Nivel 3 · español correcto: sí · fenómeno: primera persona y subjuntivo
- Llamada: 2026-11-18T10:49:58.519-06:00 · 1055 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "Léxico: V",
  "razon": "La palabra \"quiero\" no está en el léxico proporcionado."
}
```
````

### [54] ¿dónde está el gato?

- Nivel 3 · español correcto: sí · fenómeno: interrogativa
- Llamada: 2026-11-18T10:49:59.575-06:00 · 6544 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "Interrogativas / Lexico / Verbo copulativo",
  "razon": "La oración contiene una interrogativa (dónde) y un verbo copulativo (está), ambos prohibidos por la gramática."
}
```
````

### [55] el gato no come el pan

- Nivel 3 · español correcto: sí · fenómeno: negación
- Llamada: 2026-11-18T10:50:06.121-06:00 · 5581 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "no hay negación",
  "razon": "La gramática prohíbe explícitamente el uso de la negación, y la oración contiene la palabra 'no'."
}
```
````

### [56] el gato es negro

- Nivel 3 · español correcto: sí · fenómeno: verbo copulativo
- Llamada: 2026-11-18T10:50:11.703-06:00 · 6097 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "SV -> V Adv? SP* / SV -> V Adv? Obj Adv? SP* / SV -> V Que O",
  "razon": "No hay verbos copulativos en el léxico ni en las reglas de SV permitidas."
}
```
````

### [57] yo veo a María

- Nivel 3 · español correcto: sí · fenómeno: primera persona y pronombre sujeto
- Llamada: 2026-11-18T10:50:17.802-06:00 · 1535 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "Restricciones: solo 3.ª persona; sujeto SIEMPRE explícito (léxico)",
  "razon": "La palabra 'yo' no está en el léxico permitido y corresponde a la 1.ª persona, la cual está prohibida por las restricciones."
}
```
````

### [58] se venden casas

- Nivel 3 · español correcto: sí · fenómeno: se impersonal/pasivo reflejo
- Llamada: 2026-11-18T10:50:19.337-06:00 · 1127 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "Restricción: no hay clíticos ni pasivas / Lexico",
  "razon": "La palabra 'se' no está en el léxico y la gramática no permite construcciones reflexivas o pasivas con clíticos."
}
```
````

### [59] la niña que el gato persigue corre

- Nivel 3 · español correcto: sí · fenómeno: relativa de objeto (hueco en el objeto)
- Llamada: 2026-11-18T10:50:20.465-06:00 · 16588 ms
- Esperado (gramática): **RECHAZA** · LLM: **ACEPTA** · resultado: **desviación hacia el español**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[f,sg] la) (N[f,sg,h] niña) (Rel (Que que) (SV (SN (Det[m,sg] el) (N[m,sg,a] gato)) (SV (V[pres,sg,tr] persigue))))) (SV (V[pres,sg,intr] corre)))",
  "regla_que_falla": null,
  "razon": "La oración cumple estrictamente con todas las reglas de la gramática, concordancias de género, número y persona, así como las restricciones de transitividad e intransitividad."
}
```
````

### [60] el gato que duerme en la casa que Juan compró come el pan

- Nivel 3 · español correcto: sí · fenómeno: doble relativa con objeto relativizado
- Llamada: 2026-11-18T10:50:37.055-06:00 · 6844 ms
- Esperado (gramática): **RECHAZA** · LLM: **ACEPTA** · resultado: **desviación hacia el español**

Respuesta del LLM:

````text
```json
{
  "acepta": true,
  "arbol": "(O (SN (Det[m,sg] el) (N[m,sg,a] gato) (Rel (Que que) (SV (V[pres,sg,intr] duerme) (SP (P en) (SN (Det[f,sg] la) (N[f,sg,n] casa) (Rel (Que que) (SV (SN[m,sg,h] (PN[m,sg,h] juan)) (V[pret,sg,tr] compró)))))))) (SV (V[pres,sg,tr] come) (Obj (SN (Det[m,sg] el) (N[m,sg,n] pan)))))",
  "regla_que_falla": null,
  "razon": "La oración es gramaticalmente correcta según las reglas de la gramática y el léxico proporcionados."
}
```
````

### [61] el profesor lee más libros que la estudiante

- Nivel 3 · español correcto: sí · fenómeno: comparativa
- Llamada: 2026-11-18T10:50:43.900-06:00 · 1213 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "Léxico / Gramática",
  "razon": "La palabra 'más' no está incluida en el léxico proporcionado."
}
```
````

### [62] Juan y María son rubio y morena respectivamente

- Nivel 3 · español correcto: sí · fenómeno: dependencias cruzadas (respectivamente)
- Llamada: 2026-11-18T10:50:45.115-06:00 · 834 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "No hay coordinación",
  "razon": "La gramática prohíbe explícitamente la coordinación (como 'y')."
}
```
````

### [63] el gato duerme porque está cansado

- Nivel 3 · español correcto: sí · fenómeno: subordinada adverbial causal
- Llamada: 2026-11-18T10:50:45.950-06:00 · 7117 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "SV -> V Adv? SP*",
  "razon": "La palabra 'porque' no está en el léxico proporcionado y la gramática no la contempla."
}
```
````

### [64] cuando llegó Pedro los niños corrieron

- Nivel 3 · español correcto: sí · fenómeno: subordinada temporal antepuesta y sujeto pospuesto
- Llamada: 2026-11-18T10:50:53.069-06:00 · 6171 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "Léxico",
  "razon": "La palabra 'cuando' no pertenece al léxico de la gramática."
}
```
````

### [65] el libro come la casa

- Nivel 3 · español correcto: sí · fenómeno: anomalía semántica (sintácticamente correcta)
- Llamada: 2026-11-18T10:50:59.242-06:00 · 56767 ms
- Esperado (gramática): **ACEPTA** · LLM: **RECHAZA** · resultado: **sobre-rechazo**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "Obj -> SN",
  "razon": "El verbo come es transitivo y exige un objeto, pero la casa es un N inanimado (n) y el objeto directo con SN requiere que sea no animado o animal, sin embargo la regla estricta para objetos directos indica que si es inanimado usa SN, pero semánticamente no afecta a la gramática formal salvo que 'come' requiere un objeto válido. No obstante, 'come' requiere un objeto; aquí el objeto es 'la casa' (SN). La regla Obj -> SN requiere que el núcleo del SN sea no animado (n). 'casa' es n. Sin embargo, la oración infringe la semántica de la gramática formal o bien el árbol no es válido porque la regla Obj -> SN se aplica pero la oración es sintácticamente aceptada por la gramática a nivel formal estricto. Espera: ¿es 'la casa' un SN con núcleo 'casa' (n, sg)? Sí. Entonces formalmente pasa la regla sintáctica. Revisemos la concordancia: 'el' (Det, m, sg), 'libro' (N, m, sg). 'come' (V, pres, sg, tr). 'la' (Det, f, sg), 'casa' (N, f, sg). Sintácticamente la derivación es posible bajo la gramática dada. Vamos a aceptarla si la gramática la deriva."
}
```
````

### [66] la mesa duerme tranquilamente

- Nivel 3 · español correcto: sí · fenómeno: anomalía semántica (sintácticamente correcta)
- Llamada: 2026-11-18T10:51:56.012-06:00 · 1600 ms
- Esperado (gramática): **ACEPTA** · LLM: **RECHAZA** · resultado: **sobre-rechazo**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "SV -> V Adv? SP*",
  "razon": "El verbo 'duerme' es intransitivo ('intr'), pero su selección semántica o restricciones del modelo no permiten que un objeto inanimado como 'mesa' realice la acción de dormir, o el verbo no es compatible, o la regla requiere un sujeto animado (aunque la gramática formal solo exige concordancia, el verbo 'duerme' requiere un sujeto semánticamente compatible con dormir, o la mesa no es compatible)."
}
```
````

### [67] el gato que corre persiguen al ratón

- Nivel 3 · español correcto: no · fenómeno: discordancia a distancia a través de una relativa
- Llamada: 2026-11-18T10:51:57.613-06:00 · 6585 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "O -> SN SV",
  "razon": "El número del SN sujeto ('el gato que corre', sg) no coincide con el número del verbo ('persiguen', pl)."
}
```
````

### [68] los niños que duerme corren

- Nivel 3 · español correcto: no · fenómeno: discordancia verbo-antecedente en relativa
- Llamada: 2026-11-18T10:52:04.200-06:00 · 11360 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "Rel -> Que SV",
  "razon": "El verbo de la relativa ('duerme', pres,sg) no concuerda en número con el SN antecedente ('los niños', m,pl)."
}
```
````

### [69] los niños de la escuela duerme

- Nivel 3 · español correcto: no · fenómeno: discordancia con atractor (sustantivo intermedio)
- Llamada: 2026-11-18T10:52:15.562-06:00 · 1436 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "O -> SN SV",
  "razon": "El número del sujeto ('los niños', plural) y el del verbo ('duerme', singular) no coinciden."
}
```
````

### [70] la niña que lee el libro corren

- Nivel 3 · español correcto: no · fenómeno: discordancia a distancia tras relativa con objeto
- Llamada: 2026-11-18T10:52:16.998-06:00 · 1634 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "O -> SN SV",
  "razon": "El número del SN antecedente y el V principal no coinciden (SN singular 'la niña que lee el libro' con V plural 'corren')."
}
```
````

### [71] el gato persigue al ratón con con

- Nivel 3 · español correcto: no · fenómeno: secuencia agramatical de preposiciones
- Llamada: 2026-11-18T10:52:18.634-06:00 · 5013 ms
- Esperado (gramática): **RECHAZA** · LLM: **RECHAZA** · resultado: **coincide**

Respuesta del LLM:

````text
```json
{
  "acepta": false,
  "arbol": null,
  "regla_que_falla": "P -> P SN",
  "razon": "La preposición 'con' al final de la oración no tiene un sintagma nominal (SN) siguiente para formar el SP."
}
```
````
