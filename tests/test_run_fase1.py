"""Verifica que el lanzador propaga los fallos de CUALQUIER paso (no solo de las pruebas)."""
import contextlib
import io
import unittest

import run_fase1

OK = ("paso ok", ["-c", "pass"])
MAL = ("paso que falla", ["-c", "import sys; sys.exit(3)"])


def _silencio(f, *a):
    """Ejecuta f(*a) sin ensuciar la salida del lanzador real (los avisos de los pasos simulados son esperados)."""
    with contextlib.redirect_stdout(io.StringIO()):
        return f(*a)


class TestLanzador(unittest.TestCase):
    def test_todo_ok(self):
        self.assertEqual(_silencio(run_fase1.ejecutar, [OK, OK]), [])

    def test_un_fallo_se_reporta_y_no_detiene_los_demas(self):
        self.assertEqual(_silencio(run_fase1.ejecutar, [OK, MAL, OK, MAL]), ["paso que falla", "paso que falla"])

    def test_main_devuelve_distinto_de_cero_si_falla_un_paso_posterior(self):
        original = run_fase1.PRUEBAS, run_fase1.PASOS_COMPLETOS
        try:
            run_fase1.PRUEBAS, run_fase1.PASOS_COMPLETOS = OK, [OK, MAL]
            self.assertEqual(_silencio(run_fase1.main, []), 1)
            run_fase1.PASOS_COMPLETOS = [OK]
            self.assertEqual(_silencio(run_fase1.main, []), 0)
        finally:
            run_fase1.PRUEBAS, run_fase1.PASOS_COMPLETOS = original

    def test_rapido_solo_ejecuta_pruebas(self):
        original = run_fase1.PRUEBAS, run_fase1.PASOS_COMPLETOS
        try:
            run_fase1.PRUEBAS, run_fase1.PASOS_COMPLETOS = OK, [MAL]
            self.assertEqual(_silencio(run_fase1.main, ["--rapido"]), 0)      # el paso MAL no se ejecuta
        finally:
            run_fase1.PRUEBAS, run_fase1.PASOS_COMPLETOS = original


if __name__ == "__main__":
    unittest.main()
