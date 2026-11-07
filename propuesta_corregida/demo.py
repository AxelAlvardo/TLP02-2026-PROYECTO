"""demo.py - Demostración en vivo (sirve para la presentación).

    python demo.py formal            # parser Mini-C: válidos, inválidos con línea/columna, verificación LL(1)
    python demo.py espanol           # parser del español: árboles en consola y PNG en resultados/arboles/
    python demo.py espanol "la niña pequeña lee un libro nuevo"
    python demo.py fase1             # puntos de falla de la CFG (escribe resultados/fase1_fallas.md)
    python demo.py todo              # los tres anteriores
"""
import os
import sys

from arbol import dibujar_arbol
from formal_parser import ErrorSintactico, analizar, verificar_ll1
from spanish_cfg import ParserEspanol, extraer_svo

DIR = os.path.dirname(os.path.abspath(__file__))
CODIGO_OK = """int n = 10;
int s = 0;
while (n > 0) {
    s = s + n * 2;
    n = n - 1;
}
if (s >= 100) { print(s); } else { print(0); }
"""
CODIGOS_MAL = ["x = 2 + * 4;", "x = (2 + 3;", "if (x > 1) y = 2;", "x = 2 $ 3;", "while (x < 3) { x = x + 1;"]
ORACIONES = ["el gato negro persigue al ratón", "la niña pequeña lee un libro nuevo",
             "el hombre ve al gato con el telescopio", "María dice que el gato corre",
             "la gata que duerme come el pan", "los niños duerme", "come el pan"]


def formal():
    print("== Mini-C ==  ¿Gramática LL(1)? ->", "SÍ (sin conflictos FIRST/FOLLOW)" if not verificar_ll1() else verificar_ll1())
    print(CODIGO_OK)
    arbol, _ = analizar(CODIGO_OK)
    print(arbol.indentado())
    os.makedirs(os.path.join(DIR, "resultados", "arboles"), exist_ok=True)
    dibujar_arbol(arbol, os.path.join(DIR, "resultados", "arboles", "formal_minic.png"), "Mini-C")
    print("\n-- Entradas inválidas --")
    for c in CODIGOS_MAL:
        try:
            analizar(c)
            print(f"{c!r:32} -> ACEPTADA (no debería)")
        except ErrorSintactico as e:
            print(f"{c!r:32} -> RECHAZADA: {e}")


def espanol(oraciones=None):
    p = ParserEspanol()
    carpeta = os.path.join(DIR, "resultados", "arboles")
    os.makedirs(carpeta, exist_ok=True)
    for i, o in enumerate(oraciones or ORACIONES, 1):
        arboles = p.parse_todos(o)
        print("=" * 70, f"\n{o}")
        if not arboles:
            print("RECHAZADA —", p._fallo_final)
            continue
        print(f"ACEPTADA con {len(arboles)} derivación(es); SVO = {extraer_svo(arboles[0])}")
        print(arboles[0].indentado())
        for k, a in enumerate(arboles, 1):
            ruta = os.path.join(carpeta, f"oracion_{i:02d}" + (f"_lectura{k}" if len(arboles) > 1 else "") + ".png")
            dibujar_arbol(a, ruta, o)
            print("  árbol guardado en", os.path.relpath(ruta, DIR))


if __name__ == "__main__":
    modo = sys.argv[1] if len(sys.argv) > 1 else "todo"
    if modo in ("formal", "todo"):
        formal()
    if modo in ("espanol", "todo"):
        espanol(sys.argv[2:3] if modo == "espanol" and len(sys.argv) > 2 else None)
    if modo in ("fase1", "todo"):
        import fase1_limites
        fase1_limites.main()
