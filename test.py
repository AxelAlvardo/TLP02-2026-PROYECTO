"""
Módulo 4: Suite de Pruebas Unitarias (unittest).
Valida el parser formal LL(1) y documenta sistemáticamente los fallos de la CFG en español.
"""

import unittest
from formal_parser import parse_code, SyntaxErrorException
from spanish_parser import SpanishCFGParser, SpanishGrammarError


class TestFormalLanguageParser(unittest.TestCase):
    """Pruebas para el compilador del lenguaje formal LL(1)."""

    def test_valid_arithmetic_precedence(self):
        """Verifica que la multiplicación tenga mayor precedencia que la suma en el AST."""
        code = "int res = 2 + 3 * 4;"
        ast = parse_code(code)
        self.assertEqual(ast.node_type, "Program")
        decl = ast.children[0]
        self.assertEqual(decl.node_type, "DeclStmt")
        # El nodo raíz de la expresión debe ser '+' y su hijo derecho '*'
        expr_root = decl.children[0]
        self.assertEqual(expr_root.value, "+")
        self.assertEqual(expr_root.children[1].value, "*")

    def test_valid_control_flow(self):
        """Verifica bloques if-else y bucles while anidados."""
        code = """
        int i = 0;
        while (i < 10) {
            if (i == 5) {
                i = i + 2;
            } else {
                i = i + 1;
            }
        }
        """
        ast = parse_code(code)
        self.assertEqual(len(ast.children), 2)
        self.assertEqual(ast.children[1].node_type, "WhileStmt")

    def test_invalid_missing_semicolon(self):
        """Verifica que la falta de punto y coma dispare SyntaxErrorException."""
        code = "int a = 5"
        with self.assertRaises(SyntaxErrorException) as ctx:
            parse_code(code)
        self.assertIn("Se esperaba token de tipo 'SEMI'", str(ctx.exception))

    def test_invalid_unbalanced_parentheses(self):
        """Verifica el rechazo de paréntesis desbalanceados."""
        code = "int a = (5 + 3 * 2;"
        with self.assertRaises(SyntaxErrorException) as ctx:
            parse_code(code)
        self.assertIn("RPAREN", str(ctx.exception))

    def test_lexical_error(self):
        """Verifica la detección de caracteres ilegales como '@' o '$'."""
        code = "int a = 5 @ 3;"
        with self.assertRaises(SyntaxErrorException) as ctx:
            parse_code(code)
        self.assertIn("Error Léxico", str(ctx.exception))


class TestSpanishCFGParserLimits(unittest.TestCase):
    """Pruebas que documentan el comportamiento y los límites de las CFG en español."""

    def test_canonical_sentence_succeeds(self):
        """Una oración estrictamente SVO con concordancia exacta debe ser aceptada."""
        sentence = "El gato negro persigue un ratón"
        parser = SpanishCFGParser(sentence)
        ast = parser.parse()
        self.assertEqual(ast.node_type, "Oración (S)")

    def test_gender_number_disagreement_fails(self):
        """Verifica que la discordancia 'La (f_sg) gatos (m_pl)' lance excepción."""
        sentence = "La gatos negros persigue un ratón"
        parser = SpanishCFGParser(sentence)
        with self.assertRaises(SpanishGrammarError) as ctx:
            parser.parse()
        self.assertIn("Fallo de Concordancia Gramatical", str(ctx.exception))

    def test_subject_verb_disagreement_fails(self):
        """Verifica que sujeto singular con verbo plural ('El gato persiguen') falle."""
        sentence = "El gato negro persiguen un ratón"
        parser = SpanishCFGParser(sentence)
        with self.assertRaises(SpanishGrammarError) as ctx:
            parser.parse()
        self.assertIn("Fallo de Concordancia Sujeto-Verbo", str(ctx.exception))

    def test_pro_drop_null_subject_limit(self):
        """Documenta el fallo de la CFG ante oraciones con sujeto tácito (válidas en español)."""
        sentence = "Persigue un ratón en el parque"
        parser = SpanishCFGParser(sentence)
        with self.assertRaises(SpanishGrammarError) as ctx:
            parser.parse()
        self.assertIn("No soporta sujeto tácito", str(ctx.exception))

    def test_free_word_order_prenominal_adjective_limit(self):
        """Documenta el fallo ante adjetivos pre-nominales ('El rápido gato')."""
        sentence = "El rápido gato persigue un ratón"
        parser = SpanishCFGParser(sentence)
        with self.assertRaises(SpanishGrammarError) as ctx:
            parser.parse()
        self.assertIn("Fallo Sintáctico / Rigidez de Orden", str(ctx.exception))

    def test_subordinate_clause_and_pp_attachment_limit(self):
        """Documenta el colapso de LL(1) en cláusulas subordinadas transitivas y múltiples PP."""
        sentence = "La niña que ve el perro con el telescopio corre en el parque"
        parser = SpanishCFGParser(sentence)
        with self.assertRaises(SpanishGrammarError):
            parser.parse()


if __name__ == "__main__":
    unittest.main(verbosity=2)