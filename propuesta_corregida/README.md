# TLP02-2026 — Gramáticas formales y lenguaje natural (versión corregida)

Parser LL(1) para *Mini-C*, parser con retroceso para un fragmento del español (con árboles visuales),
comparación cuantitativa con spaCy y experimento con un LLM. Documento completo: `PROPUESTA_CORREGIDA.md`.

## 1. Instalación (Windows / PowerShell; en Linux/macOS cambie la activación)

```powershell
cd D:\TEO\Nueva carpeta\TLP02-2026-PROYECTO\propuesta_corregida
python -m venv .venv
.venv\Scripts\Activate.ps1            # Linux/macOS:  source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download es_core_news_sm
python -m spacy download es_core_news_md
```
Requiere Python 3.9 o superior (probado con 3.10). `graphviz` NO es necesario: los árboles se dibujan con matplotlib.

## 2. Verificar que todo funciona

```powershell
python -m unittest discover -s tests -v       # 17 pruebas; deben pasar todas
```

## 3. Demos (para la presentación)

| Comando | Qué muestra |
|---|---|
| `python demo.py formal` | Mini-C: verificación LL(1), árbol, entradas inválidas con línea/columna |
| `python demo.py espanol` | Parser del español: oraciones aceptadas/rechazadas, árboles en consola y PNG en `resultados/arboles/` |
| `python demo.py espanol "la niña pequeña lee un libro nuevo"` | Una oración propia |
| `python demo.py fase1` | Catálogo de puntos de falla (escribe `resultados/fase1_fallas.md`) |
| `python nlp_demo.py` | Parser propio y spaCy lado a lado sobre las mismas oraciones |
| `python formal_parser.py archivo.c` | Analiza un archivo Mini-C |

## 4. Experimentos de la Fase 2

```powershell
python comparacion_nlp.py                     # métricas, tablas y gráficas -> resultados/
python comparacion_nlp.py --modelos sm        # solo es_core_news_sm
python comparacion_nlp.py --hf-model <modelo> # opcional: modelo HuggingFace de token-classification con etiquetas UPOS (solo etiquetado)
```
Archivos generados: `metricas_globales.csv`, `errores_detalle.csv`, `tablas.md`, `grafica_metricas.png`, `grafica_por_nivel.png`.

### Experimento con LLM (requiere clave de API)
```powershell
$env:ANTHROPIC_API_KEY = "su-clave"           # Linux/macOS: export ANTHROPIC_API_KEY=...
python llm_experimento.py --dry-run           # solo genera los prompts (sin costo)
python llm_experimento.py --limite 10         # prueba barata
python llm_experimento.py                     # 71 oraciones x 2 condiciones (zero-shot y few-shot) = 142 llamadas
python llm_experimento.py --analizar          # recalcula el resumen desde el log
```
Salidas: `resultados/llm_logs.jsonl` (prompt y respuesta de cada llamada: es el "archivo de logs" que pide el PDF) y `resultados/llm_resumen.md`.
Modelo por defecto `claude-sonnet-5-5`; se cambia con `--modelo` o con la variable `LLM_MODEL`. Para otro proveedor, reemplace `llamar_llm()`.

## 5. Estructura

```
formal_parser.py      Mini-C: gramática BNF, FIRST/FOLLOW, lexer, parser descendente recursivo, errores con posición
spanish_cfg.py        Léxico, gramática del español, parser con retroceso, extracción S-V-O, CFG pura para NLTK
arbol.py              Clase Node + dibujo de árboles (matplotlib)
fase1_limites.py      Catálogo formal de fallas de la CFG (Fase 1)
comparacion_nlp.py    Métricas vs spaCy / HuggingFace (Fase 2)
llm_experimento.py    Experimento zero-shot vs few-shot con un LLM (Fase 2)
nlp_demo.py, demo.py  Demos en vivo
dataset/test_set.csv  71 oraciones, 3 niveles, con etiquetas
tests/test_suite.py   17 pruebas
resultados/           Salidas generadas
```

## 6. Limitaciones conocidas
- La comparación con HuggingFace está implementada pero no fue ejecutada en el entorno de desarrollo (sin acceso a huggingface.co).
- El experimento con LLM no fue ejecutado contra la API real; su pipeline está probado con un LLM simulado.
Ver secciones 10 y 11 de `PROPUESTA_CORREGIDA.md`.
