import unittest
from formal_parser import FormalParser
from spanish_parser import SpanishParser

class TestParsers(unittest.TestCase):

    # --- Pruebas del Lenguaje Formal ---
    def test_formal_valido(self):
        arbol = FormalParser("x = 2 + 3 * 4").parse()
        self.assertEqual(arbol['Valor']['Op'], '+') # '+' está arriba, '*' se evalúa primero abajo

    def test_formal_invalido(self):
        with self.assertRaises(SyntaxError):
            FormalParser("x = 2 + * 4").parse() # Dos operadores seguidos deben fallar

    # --- Pruebas de Español (CFG) ---
    def test_espanol_basico_funciona(self):
        arbol = SpanishParser("el gato negro persigue un ratón").parse()
        self.assertIn('Oracion', arbol)

    def test_espanol_discordancia_falla(self):
        with self.assertRaises(SyntaxError):
            SpanishParser("la gatos negros persigue un ratón").parse()

    def test_espanol_sujeto_tacito_falla(self):
        # Demuestra el límite de la CFG ante sujeto omitido ("persigue un ratón")
        with self.assertRaises(SyntaxError):
            SpanishParser("persigue un ratón").parse()

if __name__ == "__main__":
    unittest.main()