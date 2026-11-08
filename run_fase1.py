"""run_fase1.py - Ejecuta TODA la Fase 1 y genera los entregables en resultados/.

    python run_fase1.py            # pruebas + demo formal + catálogo de fallas + contraste NLP + árboles
    python run_fase1.py --rapido   # solo pruebas
"""
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.abspath(__file__))


def paso(titulo, cmd):
    print(f"\n{'#' * 78}\n# {titulo}\n{'#' * 78}", flush=True)
    r = subprocess.run([sys.executable, *cmd], cwd=RAIZ)
    if r.returncode != 0:
        print(f"[!] El paso «{titulo}» terminó con código {r.returncode}")
    return r.returncode


def main():
    fallos = paso("1. Pruebas automáticas (formal + español + contraste)", ["-m", "unittest", "discover", "-s", "tests", "-t", ".", "-v"])
    if "--rapido" in sys.argv:
        return fallos
    paso("2. Parser formal sobre un programa de ejemplo", ["-m", "tlp.formal", "casos/formal/validos/11_euclides.mc"])
    paso("3. Catálogo de fallas del español -> resultados/fase1_fallas.md", ["-m", "tlp.espanol.catalogo_fallas"])
    paso("4. Contraste con NLTK y spaCy -> resultados/contraste_nlp.md", ["-m", "tlp.apoyo.contraste_nlp"])
    paso("5. Árboles de análisis (PNG) -> resultados/arboles/", ["-m", "tlp.apoyo.generar_arboles"])
    return fallos


if __name__ == "__main__":
    sys.exit(main())
