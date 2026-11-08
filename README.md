# TLP02-2026 — Fase 1: Parser formal (Mini-C) y extensión al español

Proyecto «Gramáticas formales y lenguaje natural: experimentando los límites de la jerarquía de Chomsky».
Esta carpeta contiene **solo la Fase 1**: (1) parser descendente recursivo LL(1) para un subconjunto de C,
(2) intento de extender la gramática al español con documentación de los puntos de falla y (3) contraste con NLTK y spaCy.

## Estructura
```
fase1/
├── README.md · requirements.txt · run_fase1.py     # entrada única: python run_fase1.py
├── tlp/
│   ├── arbol.py                  # Node (árbol de análisis) + dibujo PNG
│   ├── formal/                   # LENGUAJE FORMAL
│   │   ├── gramatica.py          #   BNF, FIRST/FOLLOW, verificar_ll1()
│   │   ├── lexer.py              #   tokenizador (error en carácter ilegal)
│   │   ├── parser.py             #   descenso recursivo + recuperación en modo pánico
│   │   └── __main__.py           #   python -m tlp.formal archivo.mc
│   ├── espanol/                  # EXTENSIÓN AL ESPAÑOL
│   │   ├── gramatica_es.py       #   léxico, reglas, ParserEspanol, CFG pura para NLTK
│   │   └── catalogo_fallas.py    #   10 fenómenos: regla que falla + nivel de Chomsky
│   └── apoyo/                    # SCRIPTS DE APOYO
│       ├── contraste_nlp.py      #   parser propio vs NLTK vs spaCy
│       └── generar_arboles.py    #   PNG de árboles
├── casos/formal/{validos,invalidos}/*.mc   # casos de prueba como archivos (12 válidos, 13 inválidos)
├── tests/                        # test_formal · test_espanol_extension · test_contraste_nlp
├── docs/                         # 01_gramatica_minic.md · 02_extension_espanol.md
└── resultados/                   # fase1_fallas.md · contraste_nlp.md · arboles/*.png (se generan)
```

## Requisitos
Python 3.10 o superior. (El código usa anotaciones `list[str]`/`X | None`.)

## Clonar e instalar
```bash
git clone <URL-DEL-REPOSITORIO>
cd <REPOSITORIO>/fase1

python -m venv .venv
# Linux/macOS:  source .venv/bin/activate
# Windows:      .venv\Scripts\activate

pip install -r requirements.txt
python -m spacy download es_core_news_sm
```
Sin el modelo de spaCy todo funciona salvo el contraste con spaCy (esas pruebas se omiten con aviso).

## Ejecutar
```bash
python run_fase1.py              # pruebas + demo + informes + árboles (todo)
python run_fase1.py --rapido     # solo pruebas

python -m unittest discover -s tests -t . -v      # pruebas
python -m tlp.formal                              # parser sobre un programa de ejemplo
python -m tlp.formal casos/formal/validos/11_euclides.mc
python -m tlp.formal casos/formal/demo_errores.mc --recuperar   # varios errores a la vez (cambia la ruta por tu propio .mc)
python -m tlp.espanol.catalogo_fallas             # -> resultados/fase1_fallas.md
python -m tlp.apoyo.contraste_nlp                 # -> resultados/contraste_nlp.md
python -m tlp.apoyo.contraste_nlp "los niños duerme"
```

## Resultado esperado
- `Ran 23 tests ... OK` (con modelo spaCy instalado; sin él, 2 pruebas figuran como omitidas).
- `Gramática LL(1): SÍ (0 conflictos)`.
- `resultados/fase1_fallas.md` con los 10 fenómenos y `resultados/contraste_nlp.md` con la comparación.

## Cómo agregar casos de prueba
- Válido: crear `casos/formal/validos/NN_nombre.mc`.
- Inválido: crear `casos/formal/invalidos/NN_nombre.mc` con primera línea `// ESPERADO: <fragmento del mensaje de error>`.
No hace falta tocar el código: `tests/test_formal.py` recorre ambas carpetas.

## Limitaciones declaradas
- El español cubre un fragmento controlado (181 formas léxicas, 3.ª persona); el rechazo de lo que queda fuera es en parte por construcción.
- El argumento de dependencias cruzadas («respectivamente») es teórico, no una demostración empírica para el español.
- spaCy se evaluó solo con `es_core_news_sm`; la «detección de discordancia» es una heurística propia.
