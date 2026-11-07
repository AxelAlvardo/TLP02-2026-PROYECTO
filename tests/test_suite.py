"""Pruebas del proyecto.  Ejecutar desde la raíz:   python -m unittest discover -s tests -v"""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import formal_parser as fp
import spanish_cfg as sc
from comparacion_nlp import cargar_dataset, gold_triple


class TestParserFormal(unittest.TestCase):
    VALIDOS = [
        "int x;", "int x = 5 + 3 * 2;", "x = (1 + 2) * 3;", "x = -y + 4;", "print(x);",
        "if (x > 1) { y = 2; }", "if (x == 1) { y = 2; } else { y = 3; }",
        "while (i < 10) { i = i + 1; }", "{ int a = 1; { a = a - 1; } }",
        "// comentario\nint z = 1; // otro", "while (a != b) { if (a > b) { a = a - b; } else { b = b - a; } }",
        "",
    ]
    INVALIDOS = [
        ("x = 2 + * 4;", "se esperaba número"),
        ("x = 2 + 3", "se esperaba ';'"),
        ("x = (2 + 3;", "se esperaba ')'"),
        ("x = 2 $ 3;", "carácter ilegal"),
        ("x = 2 3;", "se esperaba ';'"),
        ("if x > 1 { y = 2; }", "se esperaba '('"),
        ("if (x > 1) y = 2;", "se esperaba '{'"),
        ("while (x) { x = 1; ", "se esperaba '}'"),
        ("5 = x;", "no puede comenzar"),
        ("int = 3;", "se esperaba 'ID'"),
        ("x = ;", "se esperaba número"),
        ("} x = 1;", "sin su '{'"),
        ("else { x = 1; }", "no puede comenzar"),
    ]

    def test_gramatica_es_ll1(self):
        self.assertEqual(fp.verificar_ll1(), [])

    def test_validos(self):
        for c in self.VALIDOS:
            with self.subTest(c=c):
                a, errs = fp.analizar(c)
                self.assertIsNotNone(a)
                self.assertEqual(errs, [])

    def test_invalidos_se_rechazan_con_mensaje_y_posicion(self):
        for c, frag in self.INVALIDOS:
            with self.subTest(c=c):
                with self.assertRaises(fp.ErrorSintactico) as cm:
                    fp.analizar(c)
                self.assertIn(frag, str(cm.exception))
                self.assertGreaterEqual(cm.exception.linea, 1)

    def test_precedencia_y_asociatividad(self):
        a, _ = fp.analizar("x = 2 + 3 * 4;")
        self.assertEqual(a.children[0].children[1].label, "Op(+)")
        self.assertEqual(a.children[0].children[1].children[1].label, "Op(*)")
        a, _ = fp.analizar("x = 8 - 3 - 2;")            # asociatividad izquierda: (8-3)-2
        raiz = a.children[0].children[1]
        self.assertEqual(raiz.children[0].label, "Op(-)")
        self.assertEqual(raiz.children[1].label, "2")

    def test_estructura_if_else(self):
        a, _ = fp.analizar("if (x < 1) { y = 1; } else { y = 2; }")
        self.assertEqual([c.label for c in a.children[0].children], ["Cond(<)", "Bloque", "Bloque"])

    def test_recuperacion_reporta_varios_errores(self):
        a, errs = fp.analizar("x = ; y = 2; z = 3 4; w = 1;", recuperar=True)
        self.assertEqual(len(errs), 2)
        self.assertEqual(len(a.children), 2)            # y = 2; y w = 1; se analizaron

    def test_anidamiento_profundo(self):
        a, _ = fp.analizar("x = " + "(" * 200 + "1" + ")" * 200 + ";")
        self.assertIsNotNone(a)

    def test_posicion_de_error_multilinea(self):
        with self.assertRaises(fp.ErrorSintactico) as cm:
            fp.analizar("x = 1;\ny = 2 +;\n")
        self.assertEqual((cm.exception.linea, cm.exception.col), (2, 8))


class TestEspanol(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = sc.ParserEspanol()
        cls.rows = cargar_dataset()

    def test_dataset_tamano_y_niveles(self):
        self.assertGreaterEqual(len(self.rows), 60)
        self.assertEqual({r["nivel"] for r in self.rows}, {"1", "2", "3"})
        for r in self.rows:
            self.assertIn(r["gramatical_es"], ("SI", "NO"))
            self.assertIn(r["esperado_gramatica"], ("ACEPTA", "RECHAZA"))

    def test_veredicto_esperado_en_todo_el_dataset(self):
        for r in self.rows:
            with self.subTest(id=r["id"], o=r["oracion"]):
                arbol, _ = self.p.parse(r["oracion"])
                self.assertEqual(arbol is not None, r["esperado_gramatica"] == "ACEPTA")

    def test_tripletas_svo(self):
        for r in self.rows:
            if r["esperado_gramatica"] == "ACEPTA" and r["sujeto"] != "*":
                arbol, _ = self.p.parse(r["oracion"])
                s, v, o = sc.extraer_svo(arbol)
                g = gold_triple(r)
                with self.subTest(id=r["id"]):
                    self.assertEqual((s, v), g[:2])
                    if g[2] != "*":
                        self.assertEqual(o, g[2])

    def test_concordancias(self):
        for o in ["la gatos negros persiguen al ratón", "los niños duerme", "el niña lee un libro",
                  "las niñas pequeño leen un libro"]:
            arbol, diag = self.p.parse(o)
            self.assertIsNone(arbol, o)
            self.assertIn("concordancia", diag)

    def test_a_personal(self):
        self.assertIsNotNone(self.p.parse("Juan ve a Ana")[0])
        self.assertIsNone(self.p.parse("Juan ve Ana")[0])

    def test_ambiguedad_catalan(self):
        base = "el hombre ve al gato con el telescopio"
        self.assertEqual(len(self.p.parse_todos(base)), 2)
        self.assertEqual(len(self.p.parse_todos(base + " en el parque")), 5)
        self.assertEqual(len(self.p.parse_todos(base + " en el parque de la ciudad")), 14)

    def test_equivalencia_con_cfg_pura_nltk(self):
        """El parser recursivo (con rasgos) acepta exactamente lo mismo que la CFG pura expandida."""
        g, n = sc.cfg_nltk()
        self.assertGreater(n, 100)
        extra = ["el gato corre", "un gato corre", "las gatas negras duermen", "la estudiante lee un libro",
                 "el estudiante lee una carta", "Pedro dice que Ana piensa que el gato duerme",
                 "los niños que corren comen el pan"]
        for o in [r["oracion"] for r in self.rows] + extra:
            with self.subTest(o=o):
                propio = self.p.parse(o)[0] is not None
                acepta, ntree = sc.acepta_nltk(g, o)
                self.assertEqual(propio, acepta)
                if propio:
                    self.assertEqual(len(self.p.parse_todos(o)) > 1, ntree > 1)

    def test_visualizacion_png(self):
        from arbol import dibujar_arbol
        arbol, _ = self.p.parse("la niña pequeña lee un libro nuevo")
        with tempfile.TemporaryDirectory() as d:
            ruta = dibujar_arbol(arbol, os.path.join(d, "a.png"))
            self.assertGreater(os.path.getsize(ruta), 3000)


class TestLLMPipeline(unittest.TestCase):
    """Valida construcción de prompts y análisis con un LLM SIMULADO (no se llama a ninguna API)."""

    def test_prompts_y_analisis(self):
        import llm_experimento as le
        z = le.construir_prompt("el gato corre", few_shot=False)
        f = le.construir_prompt("el gato corre", few_shot=True)
        self.assertIn("GRAMÁTICA", z)
        self.assertNotIn("EJEMPLOS RESUELTOS", z)
        self.assertIn("EJEMPLOS RESUELTOS", f)
        for e in le.EJEMPLOS:                                    # los ejemplos no se filtran al test
            self.assertNotIn(e, [r["oracion"] for r in cargar_dataset()])

        p = sc.ParserEspanol()

        def falso(prompt, modelo):                               # acepta todo lo que sea español correcto
            o = prompt.rsplit("Oración: ", 1)[1].strip()
            fila = next(r for r in cargar_dataset() if r["oracion"] == o)
            a, _ = p.parse(o)
            acepta = fila["gramatical_es"] == "SI"
            return json.dumps({"acepta": acepta, "arbol": a.bracket() if a else None})

        with tempfile.TemporaryDirectory() as d:
            le.LOG, le.RESUMEN = os.path.join(d, "log.jsonl"), os.path.join(d, "r.md")
            original, le.llamar_llm = le.llamar_llm, falso
            try:
                class A: modelo, limite, pausa, dry_run = "x", 0, 0, False
                le.correr(A)
                le.analizar()
            finally:
                le.llamar_llm = original
            with open(le.RESUMEN, encoding="utf-8") as f:
                texto = f.read()
            self.assertIn("zero-shot", texto)
            # un LLM que se guía por el español debe desviarse exactamente en los 19 casos de nivel 3 válidos fuera de la gramática
            self.assertIn("| 19 |", texto)


if __name__ == "__main__":
    unittest.main()
