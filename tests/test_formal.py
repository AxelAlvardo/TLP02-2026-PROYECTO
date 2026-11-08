"""Pruebas del lenguaje formal (Mini-C).  Desde la raíz de fase1/:  python -m unittest tests.test_formal -v

Los casos de entrada viven como archivos en casos/formal/validos/*.mc (deben ACEPTARSE) y
casos/formal/invalidos/*.mc (deben RECHAZARSE; la 1.ª línea `// ESPERADO: <fragmento>` indica el mensaje).
"""
import glob
import os
import re
import unittest

from tlp.formal import ErrorSintactico, analizar, tokenizar, verificar_ll1

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _leer(ruta):
    with open(ruta, encoding="utf-8") as f:
        return f.read()


def _archivos(sub):
    return sorted(glob.glob(os.path.join(RAIZ, "casos", "formal", sub, "*.mc")))


class TestGramatica(unittest.TestCase):
    def test_gramatica_es_ll1(self):
        self.assertEqual(verificar_ll1(), [])

    def test_hay_casos_suficientes(self):
        self.assertGreaterEqual(len(_archivos("validos")), 10)
        self.assertGreaterEqual(len(_archivos("invalidos")), 10)


class TestCasosEnArchivos(unittest.TestCase):
    def test_validos_se_aceptan(self):
        for ruta in _archivos("validos"):
            with self.subTest(caso=os.path.basename(ruta)):
                arbol, errores = analizar(_leer(ruta))
                self.assertIsNotNone(arbol)
                self.assertEqual(errores, [])

    def test_invalidos_se_rechazan_con_mensaje_y_posicion(self):
        for ruta in _archivos("invalidos"):
            texto = _leer(ruta)
            esperado = re.match(r"// ESPERADO: (.+)", texto).group(1).strip()
            with self.subTest(caso=os.path.basename(ruta)):
                with self.assertRaises(ErrorSintactico) as cm:
                    analizar(texto)
                self.assertIn(esperado, str(cm.exception))
                self.assertGreaterEqual(cm.exception.linea, 1)
                self.assertGreaterEqual(cm.exception.col, 1)


class TestArbol(unittest.TestCase):
    def test_precedencia(self):
        a, _ = analizar("x = 2 + 3 * 4;")
        suma = a.children[0].children[1]
        self.assertEqual(suma.label, "Op(+)")
        self.assertEqual(suma.children[1].label, "Op(*)")

    def test_asociatividad_izquierda(self):
        a, _ = analizar("x = 8 - 3 - 2;")                    # (8-3)-2
        raiz = a.children[0].children[1]
        self.assertEqual((raiz.children[0].label, raiz.children[1].label), ("Op(-)", "2"))

    def test_estructura_if_else(self):
        a, _ = analizar("if (x < 1) { y = 1; } else { y = 2; }")
        self.assertEqual([c.label for c in a.children[0].children], ["Cond(<)", "Bloque", "Bloque"])

    def test_else_pertenece_al_if_mas_cercano(self):
        a, _ = analizar("if (a) { if (b) { x = 1; } else { x = 2; } }")
        externo = a.children[0]
        self.assertEqual(len(externo.children), 2)             # el if externo NO tiene else
        self.assertEqual(len(externo.children[1].children[0].children), 3)

    def test_anidamiento_profundo_requiere_pila(self):
        a, _ = analizar("x = " + "(" * 200 + "1" + ")" * 200 + ";")
        self.assertIsNotNone(a)

    def test_exportaciones(self):
        a, _ = analizar("x = 1;")
        self.assertIn("Asignacion", a.bracket())
        self.assertIn("Programa", a.to_dict())


class TestErrores(unittest.TestCase):
    def test_posicion_multilinea(self):
        with self.assertRaises(ErrorSintactico) as cm:
            analizar("x = 1;\ny = 2 +;\n")
        self.assertEqual((cm.exception.linea, cm.exception.col), (2, 8))

    def test_caracter_ilegal_no_se_descarta(self):
        with self.assertRaises(ErrorSintactico):
            tokenizar("x = 1 @ 2;")

    def test_recuperacion_en_modo_panico(self):
        a, errs = analizar("x = ; y = 2; z = 3 4; w = 1;", recuperar=True)
        self.assertEqual(len(errs), 2)
        self.assertEqual(len(a.children), 2)                   # y = 2;  y  w = 1;


if __name__ == "__main__":
    unittest.main()
