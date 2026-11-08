"""generar_arboles.py - Dibuja en PNG los árboles de análisis del programa formal y de oraciones en español."""
import os

from ..arbol import dibujar_arbol
from ..espanol import ParserEspanol
from ..formal import analizar

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    destino = os.path.join(RAIZ, "resultados", "arboles")
    os.makedirs(destino, exist_ok=True)
    with open(os.path.join(RAIZ, "casos", "formal", "validos", "11_euclides.mc"), encoding="utf-8") as f:
        arbol, _ = analizar(f.read())
    print(dibujar_arbol(arbol, os.path.join(destino, "formal_euclides.png"), "Mini-C: algoritmo de Euclides"))
    p = ParserEspanol()
    for nombre, o in [("es_simple", "el gato negro persigue al ratón"), ("es_subordinada", "Pedro dice que Ana piensa que el gato duerme")]:
        a, _ = p.parse(o)
        print(dibujar_arbol(a, os.path.join(destino, f"{nombre}.png"), o))
    for k, a in enumerate(p.parse_todos("el hombre ve al gato con el telescopio"), 1):
        print(dibujar_arbol(a, os.path.join(destino, f"es_ambigua_lectura{k}.png"), f"Lectura {k}: el hombre ve al gato con el telescopio"))


if __name__ == "__main__":
    main()
