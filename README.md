# TLP02-2026 — Fase 1: Parser formal (Mini-C) y extensión al español

Proyecto «Gramáticas formales y lenguaje natural: experimentando los límites de la jerarquía de Chomsky».
Este repositorio contiene **solo la Fase 1**:

1. Parser descendente recursivo LL(1) para *Mini-C* (subconjunto de C), con árbol de análisis y errores con línea/columna.
2. Intento de extender la CFG a un fragmento controlado del español (concordancia, subordinación, modificadores) y catálogo de puntos de falla.
3. Contraste con NLTK (obligatorio, sin descargas) y con **spaCy** (comparación contra un modelo estadístico).
4. Informe técnico: [`docs/INFORME_TECNICO_FASE1.md`](docs/INFORME_TECNICO_FASE1.md) (Anexo A: [`docs/01_gramatica_minic.md`](docs/01_gramatica_minic.md)).

## Estructura
```
.
├── README.md · requirements.txt · requirements-spacy.txt · run_fase1.py
├── tlp/
│   ├── arbol.py                  # Node (árbol de análisis) + dibujo PNG
│   ├── formal/                   # LENGUAJE FORMAL: gramatica.py · lexer.py · parser.py · __main__.py
│   ├── espanol/                  # gramatica_es.py (léxico, reglas, CFG pura para NLTK) · catalogo_fallas.py
│   └── apoyo/                    # contraste_nlp.py (propio vs NLTK vs spaCy) · generar_arboles.py
├── casos/formal/{validos,invalidos}/*.mc   # 12 programas válidos y 13 inválidos · demo_errores.mc
├── tests/                        # test_formal · test_espanol_extension · test_contraste_nlp · test_run_fase1
├── docs/                         # INFORME_TECNICO_FASE1.md · 01_gramatica_minic.md (Anexo A)
└── resultados/                   # fase1_fallas.md · contraste_nlp.md · arboles/*.png
```

## Requisitos
- Python **3.10 o superior**.
- Git.

> Los comandos de esta guía se ejecutan **desde la raíz del repositorio** (donde están `run_fase1.py` y la carpeta `tlp/`).
> Cada comando va en su propio bloque para que lo copies directamente; debajo de cada uno se explica para qué sirve.

---

## 1. Instalación

### 1.1 Clonar el repositorio
```bash
git clone <URL-DEL-REPOSITORIO>
```
Descarga una copia del proyecto en tu computadora. Reemplaza `<URL-DEL-REPOSITORIO>` por la URL real.

### 1.2 Entrar a la carpeta del proyecto
```bash
cd <CARPETA-CLONADA>
```
Te sitúa en la raíz del repositorio. Todos los demás comandos se ejecutan desde aquí.

### 1.3 Cambiar a la rama de la entrega (solo si no la tienes)
```bash
git checkout fase1-1.0
```
Selecciona la rama `fase1-1.0`, que contiene la versión entregada de la Fase 1.

### 1.4 Crear el entorno virtual
```bash
python -m venv .venv
```
Crea la carpeta `.venv` con un Python aislado, para que las dependencias del proyecto no se mezclen con las de tu sistema. Se hace una sola vez.

### 1.5 Activar el entorno virtual

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```
Activa el entorno en PowerShell. Verás `(.venv)` al inicio de la línea de comandos. Si PowerShell bloquea el script, ejecuta antes el comando de la sección 1.6.

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

> Debes activar el entorno **cada vez** que abras una terminal nueva para trabajar en el proyecto.

### 1.6 (Solo Windows) Permitir scripts en PowerShell si la activación falla
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```
Permite ejecutar scripts **solo en la terminal actual** (no cambia la configuración global de tu equipo). Después repite el paso 1.5.

### 1.7 Instalar las dependencias básicas
```bash
pip install -r requirements.txt
```
Instala `nltk` y `matplotlib`. Es suficiente para el parser formal, la extensión al español, el contraste con NLTK y los árboles en PNG.

---

## 2. Instalar y usar spaCy

spaCy se usa para la comparación contra un modelo estadístico: procesa las mismas oraciones que intentó analizar la gramática y muestra la diferencia de capacidad.

### 2.1 Instalar spaCy
```bash
pip install -r requirements-spacy.txt
```
Instala `spacy` (y también las dependencias básicas, porque este archivo incluye `requirements.txt`).

### 2.2 Descargar el modelo en español
```bash
python -m spacy download es_core_news_sm
```
Descarga el modelo pequeño de spaCy para español (`es_core_news_sm`), que es el que usa el informe. Es necesario porque spaCy por sí solo no trae ningún modelo de idioma.

### 2.3 (Opcional) Descargar el modelo mediano
```bash
python -m spacy download es_core_news_md
```
Descarga el modelo mediano, más grande y con vectores de palabras. Solo hace falta si quieres comparar contra él (ver 2.7).

### 2.4 Verificar que spaCy y el modelo quedaron bien instalados
```bash
python -c "import spacy; nlp = spacy.load('es_core_news_sm'); print(spacy.__version__, nlp.meta['version'])"
```
Carga el modelo e imprime las versiones. Si no muestra errores, spaCy está listo. Los resultados del informe se obtuvieron con spaCy 3.8.18 y `es_core_news_sm` 3.8.0.

### 2.5 Contrastar UNA oración con spaCy (y con NLTK y el parser propio)
```bash
python -m tlp.apoyo.contraste_nlp "los niños duerme"
```
Analiza la oración entre comillas con las tres herramientas y muestra los resultados en pantalla. No escribe ningún archivo. Cambia el texto por cualquier oración en español que quieras probar.

### 2.6 Contrastar TODAS las oraciones del proyecto y generar el informe
```bash
python -m tlp.apoyo.contraste_nlp
```
Procesa el conjunto completo de oraciones (parser propio vs NLTK vs spaCy) y escribe la tabla comparativa en `resultados/contraste_nlp.md`.

### 2.7 Usar otro modelo de spaCy (opcional)
```bash
python -m tlp.apoyo.contraste_nlp --modelo es_core_news_md
```
Igual que 2.6, pero con el modelo mediano. Requiere haberlo descargado en 2.3.

### 2.8 Ejecutar solo las pruebas que usan spaCy
```bash
python -m unittest tests.test_contraste_nlp -v
```
Corre las pruebas del contraste. Las 2 pruebas de spaCy se ejecutan si el modelo está instalado y se omiten (`skipped`) si no lo está.

> **Sin spaCy o sin el modelo todo sigue funcionando:** el contraste con NLTK se genera igual y `resultados/contraste_nlp.md` queda con la sección de spaCy marcada **«No generada»**.

---

## 3. Ejecutar el proyecto

### 3.1 Ejecutar toda la Fase 1
```bash
python run_fase1.py
```
Lanza todo en orden: pruebas automáticas, parser formal sobre un ejemplo, catálogo de fallas del español, contraste NLP y árboles en PNG. Devuelve código de salida 1 si **falla algún paso**.

### 3.2 Ejecutar solo las pruebas (modo rápido)
```bash
python run_fase1.py --rapido
```
Corre únicamente las pruebas automáticas a través del lanzador.

### 3.3 Ejecutar las pruebas directamente
```bash
python -m unittest discover -s tests -t . -v
```
Corre todas las pruebas con detalle (`-v`). Es lo mismo que el paso 1 del lanzador.

---

## 4. Parser formal (Mini-C)

### 4.1 Parser sobre el programa de ejemplo incluido
```bash
python -m tlp.formal
```
Analiza un programa de ejemplo interno y muestra el árbol de análisis.

### 4.2 Parser sobre un programa válido
```bash
python -m tlp.formal casos/formal/validos/11_euclides.mc
```
Analiza el algoritmo de Euclides escrito en Mini-C e imprime su árbol de análisis. Puedes usar cualquier archivo de `casos/formal/validos/`.

### 4.3 Parser sobre un programa con errores
```bash
python -m tlp.formal casos/formal/invalidos/02_falta_punto_y_coma.mc
```
Muestra cómo el parser rechaza el programa e indica el error con línea y columna. Puedes usar cualquier archivo de `casos/formal/invalidos/`.

### 4.4 Reportar varios errores a la vez
```bash
python -m tlp.formal casos/formal/demo_errores.mc --recuperar
```
Con `--recuperar` el parser no se detiene en el primer error, sino que sigue y lista todos. Sirve también con tus propios archivos `.mc`.

> **Código de salida de `python -m tlp.formal`:** `0` si el programa es válido, `1` si tiene errores sintácticos y `2` si el archivo no existe.

---

## 5. Extensión al español y resultados

### 5.1 Generar el catálogo de puntos de falla
```bash
python -m tlp.espanol.catalogo_fallas
```
Prueba oraciones en español contra la gramática extendida, documenta dónde y por qué falla la CFG y escribe el resultado en `resultados/fase1_fallas.md`.

### 5.2 Generar los árboles de análisis en PNG
```bash
python -m tlp.apoyo.generar_arboles
```
Dibuja los árboles del parser formal y del español y los guarda en `resultados/arboles/`.

---

## Resultado esperado
- Pruebas: `OK` con **28 pruebas** si spaCy y el modelo están instalados; **26 ejecutadas y 2 omitidas** si no lo están.
- `Gramática LL(1): SÍ (0 conflictos)`.
- `run_fase1.py` termina con `FASE 1: 5 paso(s) ejecutado(s) correctamente.` y código 0.
- Ejecutar el lanzador **regenera** `resultados/` (incluidos los PNG, cuyos bytes pueden variar con la versión de matplotlib). Si no quieres esos cambios en git, descártalos antes de hacer commit.

## Solución de problemas

| Problema | Solución |
|---|---|
| `python` no se reconoce | En Windows prueba `py` en lugar de `python`. Comprueba la versión con `py --version` (debe ser 3.10+). |
| PowerShell no deja activar el entorno | Ejecuta el comando de la sección 1.6 y vuelve a activar. |
| `ModuleNotFoundError: No module named 'spacy'` | Activa el entorno (1.5) e instala con `pip install -r requirements-spacy.txt`. |
| `OSError: [E050] Can't find model 'es_core_news_sm'` | Descarga el modelo: `python -m spacy download es_core_news_sm`. |
| `ModuleNotFoundError: No module named 'tlp'` | Estás fuera de la raíz del repositorio; haz `cd` a la carpeta que contiene `run_fase1.py`. |

## Agregar casos de prueba
- Válido: crear `casos/formal/validos/NN_nombre.mc`.
- Inválido: crear `casos/formal/invalidos/NN_nombre.mc` con primera línea `// ESPERADO: <fragmento del mensaje de error>`.

No hace falta tocar el código: `tests/test_formal.py` recorre ambas carpetas.

## Limitaciones declaradas
- El español cubre un fragmento controlado (181 formas léxicas, 3.ª persona, presente y pretérito); no es un parser general del español. Parte de lo que se rechaza queda fuera por vocabulario o por reglas no escritas, lo cual **no** prueba un límite de las CFG.
- El argumento de dependencias cruzadas («respectivamente») es teórico (requiere idealizar k ilimitado); la ejecución solo muestra un rechazo por léxico.
- NLTK se usa como motor CFG independiente; no es un analizador estadístico. La comparación con un modelo estadístico depende de spaCy.
- spaCy se probó únicamente con `es_core_news_sm` y 10 oraciones; la «detección de discordancia» es una heurística propia.
- Pendiente fuera del código: presentación oral (15–20 min) con demostración en vivo, e integrantes del grupo.
