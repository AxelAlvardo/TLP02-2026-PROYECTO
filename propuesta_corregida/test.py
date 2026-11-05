"""
Módulo 7: Suite de pruebas (unittest).  Ejecutar:  python -m unittest test -v

Secciones:
  1. Parser formal recursivo: entradas válidas, inválidas y recuperación de errores.
  2. Análisis LL(1) y parser dirigido por tabla (equivalencia con el recursivo).
  3. CFG del español sobre el corpus etiquetado (aciertos, rechazos correctos, falsos negativos, ambigüedad).
  4. Verificación cruzada con NLTK (chart parser independiente) y tamaño de la gramática.
  5. La CFG del español no es LL(1): conflictos de adjunción.
  6. Demostración de dependencias cruzadas (límite CFG).
"""

import unittest

import chomsky_limits as cl
from formal_parser import SyntaxErrorException, parse_code
from ll1_analysis import GRAMMAR, build_table, first_sets, follow_sets, is_ll1
from ll1_table_parser import ll1_parse
from spanish_parser import (CORPUS, SpanishCFGParser, SpanishGrammarError, build_cfg, cfg_stats,
                            grammar_growth, to_nltk_text)

try:
    from nltk import CFG, ChartParser
    HAVE_NLTK = True
except ImportError:  # pragma: no cover
    HAVE_NLTK = False

VALID_PROGRAMS = [
    "",
    "int x = 10;",
    "int x;",
    "float y = 2.5; x = y;",
    "x = -1;",
    "x = a - b - c;",
    "x = ((1 + 2) * (3 - 4)) / 5;",
    "{ }",
    "{ { x = 1; } }",
    "if (a < b) { a = 1; }",
    "if (a == b) { a = 1; } else { a = 2; }",
    "if (a < b) { a = 1; } else if (a > b) { a = 2; } else { a = 3; }",
    "int i = 0; while (i < 10) { if (i == 5) { i = i + 2; } else { i = i + 1; } }",
]

INVALID_PROGRAMS = [
    "int a = 5",                    # falta ;
    "int a = (5 + 3 * 2;",          # paréntesis sin cerrar
    "x = ;",                        # falta expresión
    "x 5;",                         # falta =
    "if (x) { }",                   # condición sin operador relacional
    "if (x < 1) x = 2;",            # el cuerpo debe ser un bloque
    "else { x = 1; }",              # else sin if
    "{ x = 1;",                     # falta }
    "x = 1; }",                     # } sobrante
    "int = 5;",                     # falta identificador
    "while x < 3 { }",              # faltan paréntesis
]


class TestFormalLanguageParser(unittest.TestCase):

    def test_valid_programs_are_accepted(self):
        for src in VALID_PROGRAMS:
            with self.subTest(src=src):
                parse_code(src)

    def test_invalid_programs_are_rejected(self):
        for src in INVALID_PROGRAMS:
            with self.subTest(src=src):
                with self.assertRaises(SyntaxErrorException):
                    parse_code(src)

    def test_arithmetic_precedence(self):
        expr = parse_code("int res = 2 + 3 * 4;").children[0].children[0]
        self.assertEqual(expr.value, "+")
        self.assertEqual(expr.children[1].value, "*")

    def test_left_associativity(self):
        expr = parse_code("x = a - b - c;").children[0].children[0]
        self.assertEqual(expr.value, "-")
        self.assertEqual(expr.children[0].node_type, "BinOp")      # (a - b) - c
        self.assertEqual(expr.children[1].value, "c")

    def test_unary_minus(self):
        expr = parse_code("x = -5;").children[0].children[0]
        self.assertEqual(expr.node_type, "UnaryOp")

    def test_declaration_without_initializer(self):
        decl = parse_code("int a;").children[0]
        self.assertEqual(decl.node_type, "DeclStmt")
        self.assertEqual(decl.children, [])

    def test_else_if_chain_nests_if_in_else(self):
        node = parse_code("if (a<b) {} else if (a>b) {} else {}").children[0]
        self.assertEqual(len(node.children), 3)
        self.assertEqual(node.children[2].node_type, "IfStmt")

    def test_control_flow_structure(self):
        ast = parse_code("int i = 0; while (i < 10) { i = i + 1; }")
        self.assertEqual([c.node_type for c in ast.children], ["DeclStmt", "WhileStmt"])

    def test_missing_semicolon_message(self):
        with self.assertRaises(SyntaxErrorException) as ctx:
            parse_code("int a = 5")
        self.assertIn("Se esperaba token de tipo 'SEMI'", str(ctx.exception))

    def test_unbalanced_parentheses_message(self):
        with self.assertRaises(SyntaxErrorException) as ctx:
            parse_code("int a = (5 + 3 * 2;")
        self.assertIn("RPAREN", str(ctx.exception))

    def test_lexical_error(self):
        with self.assertRaises(SyntaxErrorException) as ctx:
            parse_code("int a = 5 @ 3;")
        self.assertIn("Error Léxico", str(ctx.exception))

    def test_error_reports_line_and_column(self):
        with self.assertRaises(SyntaxErrorException) as ctx:
            parse_code("int a = 1;\nint b = ;")
        self.assertIn("Línea 2", str(ctx.exception))

    def test_panic_mode_collects_several_errors(self):
        src = "int a = 5\nwhile (a < 10) { a = a + 1; }\nb = (3 + ;\nx = * 2;\n"
        with self.assertRaises(SyntaxErrorException) as ctx:
            parse_code(src)
        self.assertEqual(len(ctx.exception.errors), 3)


class TestLL1(unittest.TestCase):

    def test_grammar_is_ll1(self):
        table, conflicts = build_table()
        self.assertEqual(conflicts, [])
        self.assertTrue(is_ll1())

    def test_first_and_follow_key_sets(self):
        first, follow = first_sets(), follow_sets()
        self.assertEqual(first["Factor"], {"LPAREN", "MINUS", "ID", "NUMBER"})
        self.assertEqual(first["Stmt"], {"int", "float", "if", "while", "ID", "LBRACE"})
        self.assertNotIn("else", follow["ElsePart"])           # sin "dangling else": bloques obligatorios
        self.assertEqual(follow["DeclInit"], {"SEMI"})

    def test_ambiguous_grammar_is_detected_as_not_ll1(self):
        """El detector de conflictos funciona: if sin bloque obligatorio produce el dangling else."""
        g = {
            "S": [["if", "S", "ElsePart"], ["a"]],
            "ElsePart": [["else", "S"], ["ε"]],
        }
        _, conflicts = build_table(g, start="S")
        self.assertTrue(conflicts)

    def test_table_parser_agrees_with_recursive_descent(self):
        for src in VALID_PROGRAMS + INVALID_PROGRAMS:
            with self.subTest(src=src):
                try:
                    parse_code(src)
                    rd_ok = True
                except SyntaxErrorException:
                    rd_ok = False
                try:
                    ll1_parse(src)
                    tb_ok = True
                except SyntaxErrorException:
                    tb_ok = False
                self.assertEqual(rd_ok, tb_ok)

    def test_derivation_tree_frontier_equals_input(self):
        src = "int x = 2 + 3 * 4; if (x < 20) { x = x - 1; }"
        tree = ll1_parse(src)
        self.assertEqual(tree.symbol, "Program")
        self.assertEqual("".join(tree.leaves()), src.replace(" ", ""))


class TestSpanishCFG(unittest.TestCase):

    def test_corpus_labels_hold(self):
        for e in CORPUS:
            with self.subTest(id=e["id"], text=e["text"]):
                parser = SpanishCFGParser(e["text"]) if e["expect"] == "accept" else None
                if e["expect"] == "accept":
                    self.assertEqual(parser.count_parses(), e["parses"])
                else:
                    with self.assertRaises(SpanishGrammarError) as ctx:
                        SpanishCFGParser(e["text"]).parse()
                    self.assertEqual(ctx.exception.kind, e["kind"])

    def test_false_negatives_are_valid_spanish(self):
        """Clasificación de errores del corpus: 5 falsos negativos (español válido rechazado)."""
        fn = [e for e in CORPUS if e["expect"] == "reject" and e["valid_es"]]
        tn = [e for e in CORPUS if e["expect"] == "reject" and not e["valid_es"]]
        self.assertEqual((len(fn), len(tn)), (5, 3))

    def test_ambiguity_is_hidden_by_a_deterministic_choice(self):
        trees = SpanishCFGParser("El gato ve el perro con el telescopio").parse_all()
        self.assertEqual(len(trees), 2)
        self.assertNotEqual(trees[0].pretty_print(), trees[1].pretty_print())
        first = SpanishCFGParser("El gato ve el perro con el telescopio").parse()
        self.assertEqual(first.pretty_print(), trees[0].pretty_print())   # un LL(1) solo devolvería esta

    def test_trailing_period_is_ignored(self):
        self.assertEqual(SpanishCFGParser("El gato corre.").count_parses(), 1)

    def test_empty_sentence(self):
        with self.assertRaises(SpanishGrammarError) as ctx:
            SpanishCFGParser("   ")
        self.assertEqual(ctx.exception.kind, "empty")

    def test_relative_clause_verb_agrees_with_antecedent(self):
        self.assertEqual(SpanishCFGParser("Las niñas que corren duermen").count_parses(), 1)
        with self.assertRaises(SpanishGrammarError):
            SpanishCFGParser("Las niñas que corre duermen").parse()

    def test_grammar_growth_is_multiplicative(self):
        self.assertEqual(grammar_growth({"género": 2, "número": 2}), 4)
        self.assertEqual(grammar_growth({"género": 2, "número": 2, "persona": 3}), 12)


@unittest.skipUnless(HAVE_NLTK, "NLTK no instalado")
class TestCrossCheckWithNLTK(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.split = ChartParser(CFG.fromstring(to_nltk_text(build_cfg(True))))
        cls.unsplit = ChartParser(CFG.fromstring(to_nltk_text(build_cfg(False))))

    def _count(self, parser, text):
        try:
            return len(list(parser.parse(text.lower().split())))
        except ValueError:                 # palabra fuera del léxico de la gramática
            return 0

    def test_both_parsers_count_the_same_derivations(self):
        for e in CORPUS:
            with self.subTest(id=e["id"]):
                try:
                    own = SpanishCFGParser(e["text"]).count_parses()
                except SpanishGrammarError:
                    own = 0
                self.assertEqual(own, self._count(self.split, e["text"]))

    def test_without_agreement_the_grammar_overgenerates(self):
        for e in CORPUS:
            if e["id"].startswith("B"):
                with self.subTest(id=e["id"]):
                    self.assertEqual(self._count(self.split, e["text"]), 0)
                    self.assertGreater(self._count(self.unsplit, e["text"]), 0)

    def test_agreement_inflates_the_grammar(self):
        s, u = cfg_stats(build_cfg(True)), cfg_stats(build_cfg(False))
        self.assertGreater(s["no_terminales"], 2 * u["no_terminales"])
        self.assertGreater(s["producciones_estructurales"], 2 * u["producciones_estructurales"])


class TestSpanishIsNotLL1(unittest.TestCase):

    def test_conflicts_before_and_after_left_factoring(self):
        from spanish_ll1_conflicts import SPANISH_BNF, SPANISH_BNF_FACTORED, conflicts
        self.assertEqual(len(conflicts(SPANISH_BNF)), 5)
        genuine = {(A, a) for A, a, _, _ in conflicts(SPANISH_BNF_FACTORED)}
        self.assertEqual(genuine, {("Mod", "PREP"), ("PPs", "PREP"), ("PostAdv", "ADV")})


class TestCrossSerialLimit(unittest.TestCase):

    def test_nested_cfg_vs_copy_language(self):
        nested = set(cl.enumerate_language(cl.is_nested, "mf", 4))
        copy = set(cl.enumerate_language(cl.is_copy, "mf", 4))
        self.assertEqual(sorted(nested - copy), ["fmmf", "mffm"])
        self.assertEqual(sorted(copy - nested), ["fmfm", "mfmf"])

    def test_spanish_respectivamente_pattern(self):
        self.assertTrue(cl.is_copy("mff" + "mff"))        # alto, alta, alta  -> correcto
        self.assertFalse(cl.is_nested("mff" + "mff"))     # la CFG anidada lo rechaza
        self.assertTrue(cl.is_nested("mff" + "ffm"))      # y acepta el orden inverso
        self.assertFalse(cl.is_copy("mff" + "ffm"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
