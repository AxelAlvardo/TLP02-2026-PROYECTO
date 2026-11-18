# TLP02-2026 — Fase 2: gramática del español, comparación con NLP y experimento con LLM

Esta guía reúne los comandos para ejecutar cada parte de la Fase 2.

> Los comandos se ejecutan **desde la raíz del repositorio** (donde están `README.md` y la carpeta `tlp/`), con el entorno virtual **activado**.
> Cada comando va en su propio bloque para que lo copies directamente; debajo de cada uno se explica para qué sirve.

## Qué comando corresponde a cada parte

Para reproducir los experimentos, ejecuta las partes en el orden de la tabla: la parte 5 (métricas) lee los logs que escriben las partes 4 y 6.

| Parte de la Fase 2 | Comando | Resultado |
|---|---|---|
| 1. Gramática libre de contexto | — (no se ejecuta) | [`docs/02_gramatica_espanol.md`](docs/02_gramatica_espanol.md) |
| 2. Parser y árboles visuales | `python -m tlp.espanol.visualizar "<oración>"` · `python -m tlp.espanol.visualizar --conjunto` | `resultados/fase2/arboles/*.png` |
| 3. Conjunto de prueba | `python -m unittest tests.test_fase2_espanol -v` | [`casos/espanol/conjunto_prueba.csv`](casos/espanol/conjunto_prueba.csv) |
| 4. Parser propio, spaCy y HuggingFace sobre el corpus | `python -m tlp.espanol.comparacion_nlp` | `resultados/fase2/logs/` (un log por sistema) |
| 6. Experimento con LLM (4 variantes de prompt) | `python -m tlp.espanol.llm_experimento --variante todas` | `resultados/fase2/logs/llm_<variante>.jsonl` · `resultados/fase2/llm/respuestas_<variante>.md` |
| 5. Métricas, tablas y gráficas de todos los enfoques | `python -m tlp.espanol.evaluar` | `resultados/fase2/` (`tablas.md`, CSV y gráficas) |

---

## 1. Instalación

### 1.1 Cambiar a la rama de la Fase 2 (solo si no la tienes)
```bash
git checkout fase2-1.0
```
Selecciona la rama `fase2-1.0`, que contiene la Fase 2.

### 1.2 Crear el entorno virtual
```bash
python -m venv .venv
```
Crea la carpeta `.venv` con un Python aislado. Se hace una sola vez (si ya lo creaste para la Fase 1, sáltate este paso).

### 1.3 Activar el entorno virtual

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```
Activa el entorno en PowerShell. Si PowerShell bloquea el script, ejecuta antes `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned`.

**Windows (CMD):**
```bat
.venv\Scripts\activate.bat
```
Activa el entorno en el símbolo del sistema clásico (CMD).

**Linux / macOS:**
```bash
source .venv/bin/activate
```
Activa el entorno en Linux o macOS.

> Debes activar el entorno **cada vez** que abras una terminal nueva.

### 1.4 Instalar las dependencias de la Fase 2
```bash
pip install -r requirements-fase2.txt
```
Instala spaCy (y las dependencias de la Fase 1), `transformers` y `torch` (HuggingFace) y los SDK de los tres LLM: `anthropic` (Claude), `openai` (ChatGPT) y `google-genai` (Gemini).

### 1.5 Descargar el modelo de spaCy en español
```bash
python -m spacy download es_core_news_sm
```
Descarga el modelo pequeño de spaCy para español, que usa la comparación de las partes 4 y 5.

---

## 2. Parte 1 — Gramática libre de contexto

Esta parte no tiene comando. La gramática (rasgos, reglas de producción y léxico) está documentada en [`docs/02_gramatica_espanol.md`](docs/02_gramatica_espanol.md) y programada en [`tlp/espanol/gramatica_es.py`](tlp/espanol/gramatica_es.py).

---

## 3. Parte 2 — Parser y árboles de análisis

### 3.1 Analizar una oración y dibujar su árbol
```bash
python -m tlp.espanol.visualizar "el gato negro persigue al ratón"
```
Analiza la oración con el parser propio. Si la acepta, muestra el árbol en pantalla y lo guarda en PNG en `resultados/fase2/arboles/` (una imagen por derivación si es ambigua). Si la rechaza, indica la regla que falla. Cambia el texto por cualquier oración que quieras probar.

### 3.2 Analizar todo el conjunto de prueba y dibujar sus árboles
```bash
python -m tlp.espanol.visualizar --conjunto
```
Analiza las 71 oraciones del conjunto de prueba, compara cada resultado con la salida esperada (ACEPTA / RECHAZA) y guarda los árboles de las aceptadas en `resultados/fase2/arboles/`.

---

## 4. Parte 3 — Conjunto de prueba

El conjunto está en [`casos/espanol/conjunto_prueba.csv`](casos/espanol/conjunto_prueba.csv): 71 oraciones (56 gramaticales y 15 agramaticales) en 3 niveles de dificultad, con la salida esperada, el fenómeno que prueba cada una y su sujeto-verbo-objeto.

### 4.1 Probar la gramática, el parser y el conjunto
```bash
python -m unittest tests.test_fase2_espanol -v
```
Verifica el tamaño y los niveles del conjunto, que el parser da la salida esperada y el sujeto-verbo-objeto esperado en cada oración, y que se dibuja un PNG por derivación.

---

## 5. Parte 4 — Correr el parser propio, spaCy y HuggingFace sobre el corpus

### 5.1 Generar los logs de los tres sistemas
```bash
python -m tlp.espanol.comparacion_nlp
```
Procesa las 71 oraciones con el parser propio, spaCy (crudo y con concordancia) y HuggingFace con reglas, y escribe la salida bruta de cada uno en `resultados/fase2/logs/`, una línea JSON por oración:
- `parser.jsonl`: veredicto, regla que falla, árbol en notación de paréntesis, número de derivaciones y sujeto-verbo-objeto.
- `spacy_sm_crudo.jsonl` y `spacy_sm_concordancia.jsonl`: cada token con su lema, categoría, dependencia, cabeza y morfología; sujeto-verbo-objeto y veredicto.
- `huggingface.jsonl`: la categoría UPOS de cada palabra, el veredicto y la regla que falla.

Cada línea lleva además la versión de la librería y del modelo, y el tiempo de esa oración en milisegundos. Este comando **no** calcula métricas: eso lo hace `evaluar` (sección 7). La primera vez descarga el modelo de HuggingFace (`wietsedv/xlm-roberta-base-ft-udpos28-es`, ~1,1 GB), así que necesita internet.

### 5.2 (Opcional) Incluir también el modelo mediano de spaCy
```bash
python -m spacy download es_core_news_md
```
Descarga el modelo mediano de spaCy.

```bash
python -m tlp.espanol.comparacion_nlp --modelos sm md
```
Igual que 5.1, pero también corre el modelo mediano (sus logs son `spacy_md_crudo.jsonl` y `spacy_md_concordancia.jsonl`).

### 5.3 Pruebas de los tres sistemas y sus logs
```bash
python -m unittest tests.test_comparacion_nlp -v
```
Corre las pruebas de la parte 4. Las de spaCy se omiten (`skipped`) si el modelo no está instalado y las de HuggingFace si faltan `transformers` o `torch`.

---

## 6. Parte 6 — Experimento con LLM

### 6.1 Crear la API Key de Gemini y configurar el `.env`
El repositorio trae la plantilla `.env.ejemplo`, sin claves. A partir de ella cada quien crea su propio `.env`, que **no se sube** al repositorio (está en `.gitignore`), así que tu API Key queda solo en tu computadora.

**Paso 1. Buscar la página de la API Key.** Busca en Google **«API Key Gemini»** y entra en la página de Google para crear la API Key de Gemini.

**Paso 2. Crear la API Key.** Sigue los pasos que te indica la página para crear la API Key. Al terminar, cópiala: la vas a pegar en el `.env`.

**Paso 3. Copiar la plantilla como `.env`** (una sola vez)

Linux / macOS:
```bash
cp .env.ejemplo .env
```
Windows (PowerShell):
```powershell
Copy-Item .env.ejemplo .env
```
Windows (CMD):
```bat
copy .env.ejemplo .env
```
Crea el archivo `.env` en la raíz del proyecto, con las líneas de las claves y del modelo vacías.

**Paso 4. Pegar la API Key.** Abre `.env` con cualquier editor de texto y pega tu API Key en la línea `GEMINI_API_KEY`. Deja vacías `ANTHROPIC_API_KEY` y `OPENAI_API_KEY`.

**Paso 5. Escribir el modelo.** En la línea `LLM_MODELO` escribe `gemini-3.5-flash-lite`, que es el modelo con el que se hicieron las pruebas. El `.env` queda así:
```
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
GEMINI_API_KEY=<pega-aquí-tu-api-key>
LLM_MODELO=gemini-3.5-flash-lite
```

**Paso 6. Guardar el archivo y probar** con la prueba corta de la sección 6.3. Si falta algo (no existe `.env`, no hay ninguna clave, hay más de una o falta `LLM_MODELO`), el script indica qué corregir y se detiene sin llamar al LLM.

> No pongas tu API Key en `.env.ejemplo`: ese archivo **sí** se sube al repositorio.
>
> El script también funciona con Claude o ChatGPT: en ese caso pega la clave en `ANTHROPIC_API_KEY` u `OPENAI_API_KEY` (en lugar de `GEMINI_API_KEY`) y escribe en `LLM_MODELO` el modelo de ese proveedor.

### 6.2 Los cuatro prompts
Hay un archivo de prompt por variante en [`casos/espanol/prompts/`](casos/espanol/prompts). Los cuatro llevan la gramática, el léxico, el formato de respuesta (JSON) y la oración; solo cambian las instrucciones de sistema y los ejemplos:

| Variante | Archivo | Instrucciones de sistema («aplica ÚNICAMENTE estas reglas») | Ejemplos resueltos |
|---|---|---|---|
| `sin_ejemplos` | [`sin_ejemplos.txt`](casos/espanol/prompts/sin_ejemplos.txt) | no | no |
| `zero_shot` | [`zero_shot.txt`](casos/espanol/prompts/zero_shot.txt) | sí | no |
| `few_shot` | [`few_shot.txt`](casos/espanol/prompts/few_shot.txt) | no | 6 |
| `combinado` | [`combinado.txt`](casos/espanol/prompts/combinado.txt) | sí | 6 |

Puedes editarlos: las marcas `{gramatica}`, `{lexico}` y `{oracion}` se reemplazan solas por las reglas de producción, el léxico y la oración; cada ejemplo es una línea `Oración: ...` seguida de su respuesta en JSON. Si la sección `=== SISTEMA ===` queda vacía, no se envía mensaje de sistema.

### 6.3 Prueba corta con 5 oraciones
```bash
python -m tlp.espanol.llm_experimento --variante few_shot --limite 5
```
Envía al LLM solo las 5 primeras oraciones con el prompt `few_shot`. Sirve para comprobar la clave y el nombre del modelo sin gastar las llamadas de la corrida completa (la corrida completa reemplaza este log).

### 6.4 Corrida completa: las cuatro variantes
```bash
python -m tlp.espanol.llm_experimento --variante todas
```
Envía al LLM las 71 oraciones con cada uno de los cuatro prompts (4 × 71 = 284 llamadas a la API, que cobra el proveedor). Si el proveedor responde que está saturado (error 503) o que se llegó al límite de peticiones (error 429), espera 10, 20 y 40 segundos y reintenta la misma oración. Si la primera llamada falla por otro motivo (clave o modelo mal escritos), se detiene enseguida. Por cada variante escribe:
- `resultados/fase2/logs/llm_<variante>.jsonl`: el log bruto, una línea JSON por llamada con su timestamp, la duración, el proveedor, el modelo (el pedido y el que reporta la API), la versión del SDK, los parámetros (`temperature` y `max_tokens`), el prompt completo enviado y la respuesta cruda.
- `resultados/fase2/llm/respuestas_<variante>.md`: lo mismo en forma legible, con un resumen.

Para correr una sola variante, cambia `todas` por su nombre:
```bash
python -m tlp.espanol.llm_experimento --variante zero_shot
```
Corre solo la variante `zero_shot` (71 llamadas). Sirve igual con `sin_ejemplos`, `few_shot` o `combinado`.

### 6.5 Pruebas del experimento (sin llamar a la API)
```bash
python -m unittest tests.test_llm_experimento -v
```
Corre las pruebas con un LLM simulado: no usa la clave ni gasta llamadas.

---

## 7. Parte 5 — Métricas de todos los enfoques (script de evaluación)

### 7.1 Calcular las métricas, las tablas y las gráficas
```bash
python -m tlp.espanol.evaluar
```
Lee **solo** el corpus y los logs de `resultados/fase2/logs/` (no vuelve a correr ningún sistema) y calcula, para cada enfoque, precisión, cobertura, tasa de rechazo correcto y la clasificación de errores (falsos positivos, falsos negativos y errores de etiquetado), contra dos referencias: si la oración es español correcto (`gramatical_es`) y si la gramática la deriva (`esperado_gramatica`). Escribe en `resultados/fase2/`:
- `tablas.md`: versiones y parámetros de cada enfoque y las tablas comparativas.
- `metricas_globales.csv`: las mismas métricas, con sus intervalos de confianza.
- `errores_detalle.csv`: cada error, con su referencia y su motivo.
- `grafica_metricas.png` y `grafica_errores.png`: las gráficas (un panel por referencia).

Es reproducible: con los mismos logs produce exactamente los mismos archivos, porque no usa la fecha ni mide tiempos (los milisegundos por oración salen de los logs).

### 7.2 Pruebas del script de evaluación
```bash
python -m unittest tests.test_evaluar -v
```
Comprueba las métricas con las dos referencias, la lectura del sujeto-verbo-objeto en los árboles del LLM y que dos corridas con los mismos logs producen archivos idénticos.

---

## 8. Ejecutar todas las pruebas (Fase 1 y Fase 2)
```bash
python -m unittest discover -s tests -t . -v
```
Corre todas las pruebas del proyecto con detalle.
