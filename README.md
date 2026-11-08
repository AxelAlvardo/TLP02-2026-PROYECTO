# Cómo ejecutar el proyecto

## 1. Preparar el entorno

Abre una terminal en la carpeta del proyecto y crea un entorno virtual:

```bash
python -m venv .venv
```

Actívalo:

```bash
# macOS / Linux
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Instala las dependencias:

```bash
python -m pip install -r requirements.txt
```

En macOS o Linux, si el comando `python` no existe, usa `python3`.

## 2. Ejecutar las demostraciones

Ejecuta cada comando desde la carpeta del proyecto:

```bash
python demo.py formal
```

Muestra el parser Mini-C.

```bash
python demo.py espanol
```

Muestra el parser del español y guarda sus árboles en `resultados/arboles/`.

```bash
python demo.py espanol "la niña pequeña lee un libro nuevo"
```

Analiza una oración específica.

```bash
python demo.py fase1
```

Genera el reporte `resultados/fase1_fallas.md`.

## 3. Comprobar que funciona

```bash
python -m unittest discover -s tests -v
```

La ejecución termina con `OK` si todas las pruebas pasan.

## Opcional: comparación con spaCy

Descarga los modelos una vez:

```bash
python -m spacy download es_core_news_sm
python -m spacy download es_core_news_md
```

Luego ejecuta:

```bash
python comparacion_nlp.py
```

## Opcional: experimento con LLM

Este paso requiere una clave de API de Anthropic y puede generar costos. Configura la variable
`ANTHROPIC_API_KEY` en tu terminal y ejecuta:

```bash
python llm_experimento.py --limite 10
```

Para generar los prompts sin llamar a la API:

```bash
python llm_experimento.py --dry-run
```
