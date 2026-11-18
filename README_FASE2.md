# TLP02-2026 — Fase 2: gramática del español, comparación con NLP y experimento con LLM

Esta guía reúne los comandos para ejecutar cada parte de la Fase 2. La Fase 1 está en [`README.md`](README.md).

> Los comandos se ejecutan **desde la raíz del repositorio** (donde están `README.md` y la carpeta `tlp/`), con el entorno virtual **activado**.
> Cada comando va en su propio bloque para que lo copies directamente; debajo de cada uno se explica para qué sirve.

## Qué comando corresponde a cada parte

| Parte de la Fase 2 | Comando | Resultado |
|---|---|---|
| 1. Gramática libre de contexto | — (no se ejecuta) | [`docs/02_gramatica_espanol.md`](docs/02_gramatica_espanol.md) |
| 2. Parser y árboles visuales | `python -m tlp.espanol.visualizar "<oración>"` · `python -m tlp.espanol.visualizar --conjunto` | `resultados/fase2/arboles/*.png` |
| 3. Conjunto de prueba | `python -m unittest tests.test_fase2_espanol -v` | [`casos/espanol/conjunto_prueba.csv`](casos/espanol/conjunto_prueba.csv) |
| 4 y 5. spaCy, HuggingFace y métricas | `python -m tlp.espanol.comparacion_nlp` | `resultados/fase2/` (tablas, CSV y gráficas) |
| 6. Experimento con LLM | `python -m tlp.espanol.llm_experimento` | `resultados/fase2/llm/*.md` |

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

## 5. Partes 4 y 5 — Comparación con spaCy y HuggingFace, y métricas

### 5.1 Generar la comparación, las tablas y las gráficas
```bash
python -m tlp.espanol.comparacion_nlp
```
Procesa el conjunto con el parser propio, spaCy (crudo y con concordancia) y HuggingFace con reglas. Calcula precisión, cobertura, tasa de rechazo correcto y la clasificación de errores (falsos positivos, falsos negativos y errores de etiquetado). Escribe en `resultados/fase2/`:
- `tablas.md`: tablas de aceptación/rechazo y de clasificación de errores.
- `metricas_globales.csv`: las mismas métricas, con sus intervalos de confianza.
- `errores_detalle.csv`: cada error, con su motivo.
- `grafica_metricas.png` y `grafica_errores.png`: las gráficas.

La primera vez descarga el modelo de HuggingFace (`wietsedv/xlm-roberta-base-ft-udpos28-es`, ~1,1 GB), así que necesita internet.

### 5.2 (Opcional) Incluir también el modelo mediano de spaCy
```bash
python -m spacy download es_core_news_md
```
Descarga el modelo mediano de spaCy.

```bash
python -m tlp.espanol.comparacion_nlp --modelos sm md
```
Igual que 5.1, pero compara con los modelos pequeño y mediano de spaCy.

### 5.3 Pruebas de la comparación
```bash
python -m unittest tests.test_comparacion_nlp -v
```
Corre las pruebas de las partes 4 y 5. Las de spaCy se omiten (`skipped`) si el modelo no está instalado y las de HuggingFace si faltan `transformers` o `torch`.

---

## 6. Parte 6 — Experimento con LLM

### 6.1 Configurar el LLM en el archivo `.env`
El repositorio trae la plantilla `.env.ejemplo`, sin claves. A partir de ella cada quien crea su propio `.env`, que **no se sube** al repositorio (está en `.gitignore`), así que tu clave queda solo en tu computadora.

**Paso 1. Copiar la plantilla como `.env`** (una sola vez)

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

**Paso 2. Pegar tu clave de API.** Abre `.env` con cualquier editor de texto y pega tu clave en la línea del proveedor que vas a usar. Deja las otras dos vacías: el script elige el proveedor según la única clave que esté llena.

| Línea del `.env` | Proveedor | Dónde se obtiene la clave |
|---|---|---|
| `ANTHROPIC_API_KEY` | Claude | console.anthropic.com |
| `OPENAI_API_KEY` | ChatGPT | platform.openai.com |
| `GEMINI_API_KEY` | Gemini | aistudio.google.com |

**Paso 3. Escribir el modelo.** En `LLM_MODELO` escribe el nombre exacto del modelo de ese proveedor (con o sin comillas). Por ejemplo, un `.env` listo para usar Gemini queda así:
```
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
GEMINI_API_KEY=<tu-clave-de-gemini>
LLM_MODELO=<nombre-del-modelo>
```

**Paso 4. Guardar el archivo y probar** con la prueba corta de la sección 6.3. Si falta algo (no existe `.env`, no hay ninguna clave, hay más de una o falta `LLM_MODELO`), el script indica qué corregir y se detiene sin llamar al LLM.

> No pongas tu clave en `.env.ejemplo`: ese archivo **sí** se sube al repositorio.

### 6.2 (Opcional) Editar el prompt: zero-shot o few-shot
El prompt está en [`casos/espanol/prompt_llm.txt`](casos/espanol/prompt_llm.txt). Las marcas `{gramatica}`, `{lexico}` y `{oracion}` se reemplazan solas por las reglas de producción, el léxico y la oración.
- **Zero-shot:** borra toda la sección `EJEMPLOS RESUELTOS`.
- **Few-shot:** deja, agrega o quita ejemplos (cada ejemplo es una línea `Oración: ...` seguida de su respuesta en JSON).

### 6.3 Prueba corta con 5 oraciones
```bash
python -m tlp.espanol.llm_experimento --limite 5
```
Envía al LLM solo las 5 primeras oraciones. Sirve para comprobar la clave y el nombre del modelo sin gastar las 71 llamadas.

### 6.4 Corrida completa (71 oraciones)
```bash
python -m tlp.espanol.llm_experimento
```
Envía al LLM las 71 oraciones del conjunto (71 llamadas a la API, que cobra el proveedor) y escribe `resultados/fase2/llm/respuestas_<proveedor>_<modelo>_<fecha-hora>.md` con el resumen, el prompt usado y la respuesta de cada oración. Si la primera llamada falla (clave o modelo mal escritos), se detiene enseguida.

### 6.5 Pruebas del experimento (sin llamar a la API)
```bash
python -m unittest tests.test_llm_experimento -v
```
Corre las pruebas con un LLM simulado: no usa la clave ni gasta llamadas.

---

## 7. Ejecutar todas las pruebas (Fase 1 y Fase 2)
```bash
python -m unittest discover -s tests -t . -v
```
Corre todas las pruebas del proyecto con detalle.
