# TLP02-2026 — Fase 1: Parser formal (Mini-C) y extensión al español

Proyecto «Gramáticas formales y lenguaje natural: experimentando los límites de la jerarquía de Chomsky».
Este repositorio contiene **solo la Fase 1**:

1. Parser descendente recursivo LL(1) para *Mini-C* (subconjunto de C), con árbol de análisis y errores con línea/columna.
2. Intento de extender la CFG a un fragmento controlado del español (concordancia, subordinación, modificadores) y catálogo de puntos de falla.
3. Contraste con NLTK (obligatorio, sin descargas) y con spaCy (opcional).
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
Python **3.10 o superior**.

## Instalar (desde la raíz del repositorio clonado)
```bash
git clone <URL-DEL-REPOSITORIO>
cd <CARPETA-CLONADA>              # la raíz: aquí están run_fase1.py y la carpeta tlp/

python -m venv .venv
# Linux/macOS:  source .venv/bin/activate
# Windows:      .venv\Scripts\activate

pip install -r requirements.txt   # nltk + matplotlib (suficiente para toda la Fase 1)
```
Si la rama no está en tu copia: `git checkout fase1-1.0`.

### spaCy (opcional)
Solo es necesario para la comparación contra un modelo estadístico:
```bash
pip install -r requirements-spacy.txt
python -m spacy download es_core_news_sm
```
**Sin spaCy o sin el modelo:** todo funciona. Las 2 pruebas de spaCy figuran como omitidas (`skipped`), el contraste con NLTK se genera igual, y `resultados/contraste_nlp.md` queda con la sección de spaCy marcada **«No generada»**. Los resultados con spaCy del informe se obtuvieron con spaCy 3.8.18 y `es_core_news_sm` 3.8.0.

## Ejecutar
```bash
python run_fase1.py              # pruebas + demo + informes + árboles; código de salida 1 si FALLA algún paso
python run_fase1.py --rapido     # solo las pruebas automáticas

python -m unittest discover -s tests -t . -v                          # pruebas
python -m tlp.formal                                                  # parser sobre un programa de ejemplo
python -m tlp.formal casos/formal/validos/11_euclides.mc              # un programa válido (imprime el árbol)
python -m tlp.formal casos/formal/demo_errores.mc --recuperar         # varios errores a la vez (usa tu propio .mc si quieres)
python -m tlp.espanol.catalogo_fallas                                 # -> resultados/fase1_fallas.md
python -m tlp.apoyo.contraste_nlp                                     # -> resultados/contraste_nlp.md
python -m tlp.apoyo.contraste_nlp "los niños duerme"                  # una oración (no escribe informe)
python -m tlp.apoyo.generar_arboles                                   # -> resultados/arboles/*.png
```
`python -m tlp.formal` devuelve 0 si el programa es válido y 1 si tiene errores sintácticos (2 si el archivo no existe).

## Resultado esperado
- Pruebas: `OK` con **28 pruebas** si spaCy y el modelo están instalados; **26 ejecutadas y 2 omitidas** si no lo están.
- `Gramática LL(1): SÍ (0 conflictos)`.
- `run_fase1.py` termina con `FASE 1: 5 paso(s) ejecutado(s) correctamente.` y código 0.
- Ejecutar el lanzador **regenera** `resultados/` (incluidos los PNG, cuyos bytes pueden variar con la versión de matplotlib). Si no quieres esos cambios en git, descártalos antes de hacer commit.

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
