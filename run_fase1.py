"""run_fase1.py - Ejecuta la Fase 1 y genera los entregables en resultados/.

    python run_fase1.py            # pruebas + demo formal + catálogo de fallas + contraste NLP + árboles
    python run_fase1.py --rapido   # SOLO las pruebas automáticas

Código de salida: 0 si todos los pasos ejecutados terminaron bien; 1 si falló alguno (se listan al final).
El contraste con spaCy es opcional: si no está instalado el paso NO falla, pero el informe lo declara «no generada».
"""
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.abspath(__file__))

PRUEBAS = ("1. Pruebas automáticas (formal + español + contraste)",
           ["-m", "unittest", "discover", "-s", "tests", "-t", ".", "-v"])
PASOS_COMPLETOS = [
    ("2. Parser formal sobre un programa de ejemplo", ["-m", "tlp.formal", "casos/formal/validos/11_euclides.mc"]),
    ("3. Catálogo de fallas del español -> resultados/fase1_fallas.md", ["-m", "tlp.espanol.catalogo_fallas"]),
    ("4. Contraste con NLTK (y spaCy si está instalado) -> resultados/contraste_nlp.md", ["-m", "tlp.apoyo.contraste_nlp"]),
    ("5. Árboles de análisis (PNG) -> resultados/arboles/", ["-m", "tlp.apoyo.generar_arboles"]),
]


def paso(titulo, args):
    """Ejecuta `python <args>` en la raíz del repo y devuelve su código de salida."""
    print(f"\n{'#' * 78}\n# {titulo}\n{'#' * 78}", flush=True)
    codigo = subprocess.run([sys.executable, *args], cwd=RAIZ).returncode
    if codigo != 0:
        print(f"[!] FALLÓ el paso «{titulo}» (código {codigo})", flush=True)
    return codigo


def ejecutar(pasos):
    """Corre todos los pasos (no se detiene en el primero que falla) y devuelve los títulos de los que fallaron."""
    return [titulo for titulo, args in pasos if paso(titulo, args) != 0]


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    pasos = [PRUEBAS] if "--rapido" in argv else [PRUEBAS, *PASOS_COMPLETOS]
    fallidos = ejecutar(pasos)
    print("\n" + "=" * 78)
    if fallidos:
        print(f"FASE 1: {len(fallidos)} paso(s) fallido(s):")
        for t in fallidos:
            print("  -", t)
        return 1
    print(f"FASE 1: {len(pasos)} paso(s) ejecutado(s) correctamente.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
