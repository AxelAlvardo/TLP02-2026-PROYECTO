"""tlp/espanol/visualizar.py - Fase 2: script de visualización de árboles de análisis del español.

Valida cada oración con ParserEspanol y dibuja su árbol en PNG (matplotlib, tlp/arbol.py). Si la oración es
ambigua se dibuja UNA imagen por derivación; si se rechaza se informa la regla que falla y no se dibuja nada.

Uso:  python -m tlp.espanol.visualizar "el gato negro persigue al ratón"   # una oración
      python -m tlp.espanol.visualizar --conjunto                          # casos/espanol/conjunto_prueba.csv
Las imágenes se guardan en resultados/fase2/arboles/.
Código de salida: una oración -> 0 si se acepta, 1 si se rechaza;  --conjunto -> 0 si todas coinciden con la
salida esperada, 1 si alguna discrepa;  2 si faltan argumentos.
"""
from __future__ import annotations

import os
import re
import sys
import unicodedata

from ..arbol import Node, dibujar_arbol
from .conjunto import RAIZ, cargar_conjunto, evaluar
from .gramatica_es import ParserEspanol, extraer_svo

DESTINO = os.path.join(RAIZ, "resultados", "fase2", "arboles")


def _nombre_archivo(oracion: str) -> str:
    """'el ratón corre' -> 'el_raton_corre' (sin tildes ni signos, apto para nombre de archivo)."""
    s = unicodedata.normalize("NFKD", oracion.lower()).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_") or "oracion"


def dibujar_derivaciones(arboles: list[Node], base: str, titulo: str, destino: str = DESTINO) -> list[str]:
    """Un PNG por derivación: <base>.png si hay una sola, <base>_lectura<k>.png si es ambigua. Devuelve las rutas."""
    os.makedirs(destino, exist_ok=True)
    if len(arboles) == 1:
        return [dibujar_arbol(arboles[0], os.path.join(destino, f"{base}.png"), titulo)]
    return [dibujar_arbol(a, os.path.join(destino, f"{base}_lectura{k}.png"), f"Lectura {k}: {titulo}")
            for k, a in enumerate(arboles, 1)]


def visualizar_oracion(oracion: str, destino: str = DESTINO) -> int:
    parser = ParserEspanol()
    arbol, diagnostico = parser.parse(oracion)
    if arbol is None:
        print(f"RECHAZADA: {oracion}\n  {diagnostico}")
        return 1
    arboles = parser.parse_todos(oracion)
    print(f"ACEPTADA: {oracion}  ({diagnostico})  S-V-O = {extraer_svo(arbol)}")
    rutas = dibujar_derivaciones(arboles, "oracion_" + _nombre_archivo(oracion), oracion, destino)
    for a, ruta in zip(arboles, rutas):
        print(a.indentado())
        print("  PNG:", ruta)
    return 0


def visualizar_conjunto(destino: str = DESTINO) -> int:
    resultados = evaluar(cargar_conjunto())
    discrepan, n_png = 0, 0
    for r in resultados:
        c = r.caso
        rutas = []
        if r.arboles:
            rutas = dibujar_derivaciones(r.arboles, f"conjunto_{c.id:02d}", f"[{c.id}] {c.oracion}", destino)
        n_png += len(rutas)
        if not r.coincide:
            discrepan += 1
        print(f"[{c.id:02d}] nivel {c.nivel} | esperado {c.esperado:7} | obtenido {r.obtenido:7} | "
              f"{'OK' if r.coincide else 'DISCREPA':8} | {len(rutas)} PNG | {c.oracion}")
    print(f"\n{len(resultados) - discrepan}/{len(resultados)} oraciones coinciden con la salida esperada; "
          f"{n_png} árboles en {destino}")
    return 1 if discrepan else 0


def main(argv: list[str]) -> int:
    if argv == ["--conjunto"]:
        return visualizar_conjunto()
    if not argv or argv[0].startswith("--"):
        print(__doc__)
        return 2
    return visualizar_oracion(" ".join(argv))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
