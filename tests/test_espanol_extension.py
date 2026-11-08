"""Pruebas del experimento de extensión al español.  python -m unittest tests.test_espanol_extension -v

Afirman el COMPORTAMIENTO documentado de cada fenómeno del catálogo (qué acepta, qué rechaza y por qué regla).
"""
import unittest

from tlp.espanol import ParserEspanol, acepta_nltk, cfg_nltk
from tlp.espanol.catalogo_fallas import CATALOGO, EVIDENCIA

# oración -> (¿el parser la acepta?, fragmento esperado del diagnóstico)
ESPERADO = {
    "el gato la persigue": (False, "se esperaba un verbo"),
    "come el pan": (False, "se esperaba un determinante"),
    "Juan y María leen un libro": (False, "fuera del léxico"),
    "la niña que el gato persigue corre": (False, "se esperaba un verbo"),
    "¿dónde está el gato?": (False, "fuera del léxico"),
    "el hombre ve al gato con el telescopio": (True, "2 derivación"),
    "el gato que corre persiguen al ratón": (False, "concordancia"),
    "los niños de la escuela duerme": (False, "concordancia"),
    "Juan y María son rubio y morena respectivamente": (False, "fuera del léxico"),
    "el libro come la casa": (True, "1 derivación"),
}


class TestCatalogo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = ParserEspanol()

    def test_catalogo_completo(self):
        self.assertEqual({c[0] for c in CATALOGO}, set(ESPERADO))
        self.assertEqual({c[2] for c in CATALOGO}, {"A", "B", "C", "D", "E"})

    def test_cada_fenomeno_declara_que_demuestra_la_ejecucion(self):
        self.assertEqual(set(EVIDENCIA), set(ESPERADO))
        # «respectivamente»: el rechazo es léxico; el límite de clase es argumento teórico y así debe quedar dicho
        fila = next(c for c in CATALOGO if "respectivamente" in c[0])
        self.assertIn("ARGUMENTO TEÓRICO", fila[5])
        self.assertIn("NO demuestra", EVIDENCIA[fila[0]])
        self.assertIn("fuera del léxico", self.p.parse(fila[0])[1])

    def test_comportamiento_por_fenomeno(self):
        for oracion, (acepta, fragmento) in ESPERADO.items():
            with self.subTest(oracion=oracion):
                arbol, diag = self.p.parse(oracion)
                self.assertEqual(arbol is not None, acepta)
                self.assertIn(fragmento, diag)


class TestConcordancia(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = ParserEspanol()

    def test_rechaza_discordancias(self):
        for o in ["la gatos negros persiguen al ratón", "los niños duerme", "el niña lee un libro",
                  "las niñas pequeño leen un libro"]:
            arbol, diag = self.p.parse(o)
            self.assertIsNone(arbol, o)
            self.assertIn("concordancia", diag)

    def test_acepta_concordantes(self):
        for o in ["el gato negro persigue al ratón", "las gatas negras duermen", "los niños que corren comen el pan"]:
            self.assertIsNotNone(self.p.parse(o)[0], o)

    def test_a_personal(self):
        self.assertIsNotNone(self.p.parse("Juan ve a Ana")[0])
        self.assertIsNone(self.p.parse("Juan ve Ana")[0])


class TestAmbiguedad(unittest.TestCase):
    def test_catalan_2_5_14(self):
        p = ParserEspanol()
        base = "el hombre ve al gato con el telescopio"
        self.assertEqual(len(p.parse_todos(base)), 2)
        self.assertEqual(len(p.parse_todos(base + " en el parque")), 5)
        self.assertEqual(len(p.parse_todos(base + " en el parque de la ciudad")), 14)


class TestCFGPura(unittest.TestCase):
    def test_rasgos_finitos_siguen_siendo_cf(self):
        """El parser con rasgos y la CFG pura (sin rasgos, 338 producciones) aceptan lo mismo."""
        g, n = cfg_nltk()
        self.assertGreater(n, 300)
        p = ParserEspanol()
        for o, _ in [(c[0], 0) for c in CATALOGO] + [("el gato corre", 0), ("los niños duerme", 0),
                                                       ("las gatas negras duermen", 0)]:
            with self.subTest(o=o):
                self.assertEqual(p.parse(o)[0] is not None, acepta_nltk(g, o)[0])


if __name__ == "__main__":
    unittest.main()
