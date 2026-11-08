"""python -m tlp.formal [archivo.mc] [--recuperar]   -> verifica LL(1) e imprime el árbol de análisis."""
import sys

from . import analizar, verificar_ll1
from .lexer import ErrorSintactico

DEFECTO = "int x = 5 + 3 * 2;\nif (x > 10) { print(x); } else { x = x - 1; }\nwhile (x > 0) { x = x - 1; }\n"


def main(argv):
    recuperar = "--recuperar" in argv
    args = [a for a in argv if not a.startswith("--")]
    if args:
        try:
            with open(args[0], encoding="utf-8") as fh:
                fuente = fh.read()
        except FileNotFoundError:
            print(f"No existe el archivo '{args[0]}'. Prueba con: casos/formal/demo_errores.mc")
            return 2
    else:
        fuente = DEFECTO
    conflictos = verificar_ll1()
    print("Gramática LL(1):", "SÍ (0 conflictos)" if not conflictos else conflictos)
    try:
        arbol, errores = analizar(fuente, recuperar=recuperar)
    except ErrorSintactico as e:
        print("ERROR SINTÁCTICO:", e)
        return 1
    for e in errores:
        print("ERROR (recuperado):", e)
    print(arbol.indentado())
    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
