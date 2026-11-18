"""Pruebas de la Fase 2 (gramática, parser y conjunto de prueba).  python -m unittest tests.test_fase2_espanol -v"""
import contextlib
import io
import os
import tempfile
import unittest

from tlp.espanol import ParserEspanol
from tlp.espanol.conjunto import cargar_conjunto, evaluar
from tlp.espanol.visualizar import dibujar_derivaciones, visualizar_oracion


class TestConjuntoDePrueba(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.casos = cargar_conjunto()
        cls.resultados = evaluar(cls.casos)

    def test_tamano_y_niveles(self):
        self.assertGreaterEqual(len(self.casos), 60)
        self.assertEqual({c.nivel for c in self.casos}, {1, 2, 3})
        self.assertEqual(len({c.id for c in self.casos}), len(self.casos))

    def test_salida_esperada_etiquetada(self):
        for c in self.casos:
            with self.subTest(id=c.id):
                self.assertIn(c.esperado, ("ACEPTA", "RECHAZA"))
                self.assertTrue(c.fenomeno)
                if c.esperado == "ACEPTA":
                    self.assertIsNotNone(c.svo)

    def test_parser_coincide_con_salida_esperada(self):
        for r in self.resultados:
            with self.subTest(id=r.caso.id, oracion=r.caso.oracion):
                self.assertEqual(r.obtenido, r.caso.esperado, r.diagnostico)

    def test_svo_coincide_en_las_aceptadas(self):
        for r in self.resultados:
            if r.arboles:
                with self.subTest(id=r.caso.id, oracion=r.caso.oracion):
                    self.assertEqual(r.svo, r.caso.svo)


class TestVisualizacion(unittest.TestCase):
    def test_un_png_por_derivacion(self):
        arboles = ParserEspanol().parse_todos("el hombre ve al gato con el telescopio")
        with tempfile.TemporaryDirectory() as d:
            rutas = dibujar_derivaciones(arboles, "ambigua", "prueba", d)
            self.assertEqual(len(rutas), 2)
            for ruta in rutas:
                self.assertGreater(os.path.getsize(ruta), 0)

    def test_oracion_aceptada_dibuja_y_rechazada_no(self):
        with tempfile.TemporaryDirectory() as d, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(visualizar_oracion("el gato negro persigue al ratón", d), 0)
            self.assertEqual(visualizar_oracion("los niños duerme", d), 1)
            self.assertEqual(os.listdir(d), ["oracion_el_gato_negro_persigue_al_raton.png"])


if __name__ == "__main__":
    unittest.main()
