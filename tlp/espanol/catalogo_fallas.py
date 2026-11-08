"""catalogo_fallas.py - Fase 1: intento de extender la CFG al español y documentación formal de los puntos de falla.

Para cada fenómeno se muestra (1) qué hace el parser, (2) la REGLA o rasgo que falla, (3) la clase del
fenómeno y (4) su nivel en la jerarquía de Chomsky.  Distingue cinco clases de causa (A–E) para no confundir «gramática pequeña» con «límite de las CFG»:

  A. Falla del FRAGMENTO     la CFG podría cubrirlo añadiendo reglas/rasgos; el parser falla por alcance.
  B. Límite de la TÉCNICA    es libre de contexto pero rompe LL(1) o exige retroceso (ambigüedad estructural).
  C. Límite de la CLASE      no es libre de contexto (dependencias cruzadas) => requiere más que Tipo 2.
  D. Fuera de la sintaxis    anomalías semánticas: la gramática las acepta y está bien que lo haga.
  E. Bien manejada           la gramática ya resuelve el fenómeno (p. ej. concordancia a distancia).

Uso:  python -m tlp.espanol.catalogo_fallas            (imprime y escribe resultados/fase1_fallas.md)
"""
from __future__ import annotations

import os

from ..formal import analizar, verificar_ll1
from .gramatica_es import ParserEspanol, acepta_nltk, cfg_nltk, contar_reglas_compactas

DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# (oración, fenómeno, clase, nivel Chomsky, regla/rasgo que falla, explicación formal)
CATALOGO = [
    ("el gato la persigue", "pronombre clítico", "A", "Tipo 2",
     "SV → V Obj (no hay Cl antes de V)",
     "Añadir SV → Cl V con rasgos (género, número, caso) mantiene la gramática libre de contexto."),
    ("come el pan", "sujeto tácito (pro-drop)", "A", "Tipo 2",
     "O → SN SV (el sujeto es obligatorio)",
     "Basta O → SV. Lo que se pierde es el SN que fijaba el número; se recupera con el rasgo del verbo. "
     "No es un límite de las CFG."),
    ("Juan y María leen un libro", "coordinación nominal", "A", "Tipo 2",
     "SN → PN (no existe SN → SN y SN)",
     "SN → SN 'y' SN con rasgo número=pl en el resultado: CF con rasgos finitos. Introduce ambigüedad."),
    ("la niña que el gato persigue corre", "relativa de objeto (hueco)", "A", "Tipo 2",
     "Rel → Que SV (solo hueco en el sujeto)",
     "Exige categorías con hueco (SV/SN, estilo GPSG): CF mientras la profundidad de huecos sea acotada."),
    ("¿dónde está el gato?", "interrogativa y verbo copulativo", "A", "Tipo 2",
     "'dónde', 'está' fuera del léxico; sin regla de inversión",
     "Reglas adicionales y léxico; sin dependencias no acotadas."),
    ("el hombre ve al gato con el telescopio", "ambigüedad por adjunción de FP", "B", "Tipo 2 (ambigua)",
     "SN → Det N Adj* SP* y SV → V Obj SP*  (la FP puede colgar de SN o de SV)",
     "La gramática es ambigua: FIRST(SP) aparece en dos alternativas ⇒ conflicto FIRST/FOLLOW ⇒ NO es LL(1). "
     "El número de árboles crece como los números de Catalan (ver tabla)."),
    ("el gato que corre persiguen al ratón", "concordancia a distancia (relativa intercalada)", "E", "Tipo 2",
     "concordancia sujeto–verbo",
     "El parser SÍ rechaza correctamente: el rasgo número se propaga por la estructura (anidada, no cruzada). "
     "Con rasgos finitos sigue siendo libre de contexto aunque la distancia sea arbitraria."),
    ("los niños de la escuela duerme", "concordancia con atractor", "E", "Tipo 2",
     "concordancia sujeto–verbo",
     "Rechazada correctamente: el núcleo del SN sujeto es 'niños' (pl). Un modelo puramente estadístico puede "
     "dejarse atraer por 'escuela' (sg)."),
    ("Juan y María son rubio y morena respectivamente", "dependencias cruzadas (respectivamente)", "C",
     "Tipo 1 / suavemente sensible al contexto (argumento teórico)",
     "ninguna regla concreta: el parser ni siquiera llega a aplicar reglas (vocabulario fuera del léxico)",
     "ARGUMENTO TEÓRICO (no lo demuestra el parser). Con k pares el patrón x1…xk y1…yk exige xi~yi (concordancia "
     "cruzada, como la copia {ww}). Intersectado con un lenguaje regular se obtiene {ww}, que no es libre de contexto "
     "(lema de bombeo); como las CFG se cierran bajo intersección con regulares, el fenómeno no sería CF si k no se acota. "
     "Es un argumento análogo al de Shieber (1985) para el alemán suizo, pero aquí descansa en una idealización "
     "(k ilimitado) y no es un hecho empírico establecido para el español. Para k acotado (p. ej. k ≤ 2) basta una CFG "
     "con reglas explícitas, así que ninguna oración corta de prueba puede refutar a las CFG."),
    ("el libro come la casa", "anomalía semántica", "D", "—",
     "ninguna (la gramática la ACEPTA)",
     "Las restricciones de selección ('comer' pide sujeto animado) son semánticas. Una CFG no debe resolverlas; "
     "spaCy tampoco las rechaza."),
]

# Qué demuestra EJECUTAR el parser sobre cada oración (no es lo mismo que el análisis formal de arriba).
EVIDENCIA = {
    "el gato la persigue": "Rechazo por regla ausente (SV → V …): falla del fragmento, no de la clase.",
    "come el pan": "Rechazo por regla ausente (O → SN SV): falla del fragmento, no de la clase.",
    "Juan y María leen un libro": "Rechazo por léxico (falta «y»): NO prueba nada sobre las CFG.",
    "la niña que el gato persigue corre": "Rechazo por regla ausente (relativa de objeto): falla del fragmento.",
    "¿dónde está el gato?": "Rechazo por léxico («dónde», «está»): NO prueba nada sobre las CFG.",
    "el hombre ve al gato con el telescopio": "Acepta con 2 árboles: demuestra la ambigüedad (ver §4). Que no sea LL(1) es argumento teórico.",
    "el gato que corre persiguen al ratón": "Rechazo por la regla de concordancia: la gramática resuelve el fenómeno.",
    "los niños de la escuela duerme": "Rechazo por la regla de concordancia: la gramática resuelve el fenómeno.",
    "Juan y María son rubio y morena respectivamente": "Rechazo por léxico (6 palabras fuera del léxico): NO demuestra ningún límite de las CFG; el límite de clase es solo el argumento teórico.",
    "el libro come la casa": "Acepta (1 árbol): la anomalía es semántica, no sintáctica.",
}


def contar_derivaciones():
    p = ParserEspanol()
    oraciones = ["el hombre ve al gato con el telescopio",
                 "el hombre ve al gato con el telescopio en el parque",
                 "el hombre ve al gato con el telescopio en el parque de la ciudad"]
    g, _ = cfg_nltk()
    return [(len(o.split()), len(p.parse_todos(o)), acepta_nltk(g, o)[1]) for o in oraciones]


def main():
    out = ["# Fase 1 — Puntos de falla de la CFG al extenderla al español", ""]
    p = ParserEspanol()
    out += ["## 1. Catálogo de fallas", "",
            "| # | Oración | Fenómeno | Clase | Nivel | ¿Parser acepta? | Diagnóstico del parser | Qué demuestra la ejecución |",
            "|---|---|---|---|---|---|---|---|"]
    for i, (o, fen, cl, niv, regla, _) in enumerate(CATALOGO, 1):
        arbol, diag = p.parse(o)
        out.append(f"| {i} | `{o}` | {fen} | {cl} | {niv} | {'SÍ' if arbol else 'NO'} | {diag} | {EVIDENCIA[o]} |")
    out += ["", "Clases: A = falla del fragmento (la CFG podría cubrirlo) · B = límite de la técnica (ambigüedad, no LL(1)) · "
            "C = límite de la clase (no libre de contexto; solo como argumento teórico) · D = fuera de la sintaxis · E = bien manejada: la gramática la resuelve correctamente.", "", "**Lectura honesta de la columna «Qué demuestra la ejecución»:** un rechazo por vocabulario fuera del léxico (filas 3, 5 y 9) o por una regla que simplemente no se escribió (filas 1, 2 y 4) no demuestra que una CFG sea insuficiente. Solo las filas 6–8 y 10 muestran un comportamiento de la gramática ejecutada que sustenta una afirmación; el límite de clase (fila 9) es un argumento teórico.", "", "## 2. Análisis formal por fenómeno", ""]
    for i, (o, fen, cl, niv, regla, expl) in enumerate(CATALOGO, 1):
        out += [f"**{i}. {fen}** (`{o}`) — Clase {cl}, {niv}. Regla/rasgo implicado: {regla}.", "", expl, ""]

    nred = contar_reglas_compactas()
    _, npura = cfg_nltk()
    out += ["## 3. La concordancia con rasgos finitos NO sale de Tipo 2", "",
            f"La gramática compacta tiene {nred} reglas con rasgos. Expandida a una CFG pura (cada combinación "
            f"género×número×animacidad×… pasa a ser un no terminal) tiene **{npura} producciones**. La concordancia cuesta "
            "tamaño de gramática, no poder expresivo: por eso ‘concordancia de género y número’ no es el punto donde la "
            "CFG se rompe. El parser recursivo descendente y el ChartParser de NLTK sobre esa CFG pura aceptan las mismas "
            "oraciones (verificado en `tests/test_espanol_extension.py`).", "",
            "## 4. Ambigüedad estructural (adjunción de frases preposicionales)", "",
            "| Palabras | Árboles (parser propio) | Árboles (NLTK, CFG pura) |", "|---|---|---|"]
    for n, a, b in contar_derivaciones():
        out.append(f"| {n} | {a} | {b} |")
    out += ["", "Secuencia 2, 5, 14: números de Catalan. Una CFG da todas las lecturas pero no elige entre ellas; "
            "elegir exige información semántica o estadística (lo que aportan los modelos de NLP).", "",
            "## 5. Conexión con el lenguaje formal", "",
            f"La gramática de Mini-C es LL(1) (conflictos encontrados: {len(verificar_ll1())}). Los paréntesis anidados "
            "exigen una pila: el lenguaje no es regular (Tipo 3) pero sí libre de contexto (Tipo 2). "]
    arbol, _ = analizar("int x = " + "(" * 40 + "1" + ")" * 40 + ";")
    out.append(f"Prueba: 40 niveles de paréntesis anidados se analizan correctamente: {arbol is not None}. "
               "El fragmento de español con rasgos finitos implementado queda también en Tipo 2; lo que podría excederlo (dependencias cruzadas no acotadas) es un argumento teórico, no algo que esta ejecución demuestre.")
    texto = "\n".join(out) + "\n"
    os.makedirs(os.path.join(DIR, "resultados"), exist_ok=True)
    with open(os.path.join(DIR, "resultados", "fase1_fallas.md"), "w", encoding="utf-8") as f:
        f.write(texto)
    print(texto)


if __name__ == "__main__":
    main()
