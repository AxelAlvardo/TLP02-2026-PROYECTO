"""Pruebas de la comparación con NLP (Fase 2, puntos 4 y 5).  python -m unittest tests.test_comparacion_nlp -v"""
import importlib.util
import math
import unittest

from tlp.espanol.comparacion_nlp import Analisis, Sistema, analizar_propio, metricas, reglas_upos, wilson
from tlp.espanol.conjunto import Caso, cargar_conjunto


def _hay(*modulos):
    return all(importlib.util.find_spec(m) for m in modulos)


def _caso(i, gramatical):
    return Caso(id=i, nivel=1, oracion="el gato persigue al ratón", gramatical_es=gramatical, esperado="ACEPTA",
                fenomeno="prueba", svo=("gato", "perseguir", "ratón") if gramatical else None)


class TestMetricas(unittest.TestCase):
    def test_wilson(self):
        lo, hi = wilson(5, 10)
        self.assertAlmostEqual(lo, 0.2366, places=4)
        self.assertAlmostEqual(hi, 0.7634, places=4)
        self.assertTrue(all(math.isnan(x) for x in wilson(0, 0)))

    def test_matriz_de_confusion_y_proporciones(self):
        casos = [_caso(1, True), _caso(2, True), _caso(3, False), _caso(4, False)]
        sistema = Sistema("prueba", [Analisis(True, svo=("gato", "perseguir", "ratón")), Analisis(False, "regla"),
                                     Analisis(True), Analisis(False, "regla")], 0.0, da_svo=True, da_categorias=False)
        m, errores = metricas(casos, sistema)
        self.assertEqual((m["TP"], m["FP"], m["FN"], m["TN"]), (1, 1, 1, 1))
        self.assertEqual((m["precision"][0], m["cobertura"][0], m["rechazo_correcto"][0]), (0.5, 0.5, 0.5))
        self.assertEqual(sorted(e["tipo"] for e in errores), ["falso negativo", "falso positivo"])

    def test_errores_de_etiquetado(self):
        sistema = Sistema("prueba", [Analisis(True, svo=("perro", "perseguir", "ratón"), categorias=(4, 5),
                                              mal_etiquetadas="persigue=NOUN")], 0.0, da_svo=True, da_categorias=True)
        m, errores = metricas([_caso(1, True)], sistema)
        self.assertEqual((m["err_svo"], m["err_cat"]), (1, 1))
        self.assertEqual(m["exactitud_svo"], 0.0)
        self.assertEqual(m["exactitud_categorias"], 0.8)
        self.assertEqual({e["tipo"] for e in errores},
                         {"error de etiquetado (S-V-O)", "error de etiquetado (categorías)"})


class TestReglasUpos(unittest.TestCase):
    def test_acepta(self):
        self.assertEqual(reglas_upos(["el", "gato", "persigue", "al", "ratón"], ["DET", "NOUN", "VERB", "ADP", "NOUN"]), "")

    def test_rechaza_cada_regla(self):
        casos = [(["el", "gato"], ["DET", "NOUN"], "R1"),
                 (["el", "gato", "zzz"], ["DET", "NOUN", "X"], "R1"),
                 (["el", "gato", "come", "zzz"], ["DET", "NOUN", "VERB", "X"], "R2"),
                 (["gato", "el", "persigue", "ratón", "el"], ["NOUN", "DET", "VERB", "NOUN", "DET"], "R3"),
                 (["el", "persigue", "gato"], ["DET", "VERB", "NOUN"], "R3"),
                 (["el", "gato", "corre", "con", "con"], ["DET", "NOUN", "VERB", "ADP", "ADP"], "R4")]
        for palabras, etiquetas, regla in casos:
            with self.subTest(palabras=palabras):
                self.assertTrue(reglas_upos(palabras, etiquetas).startswith(regla))


class TestParserPropio(unittest.TestCase):
    def test_conjunto_completo(self):
        casos = cargar_conjunto()
        m, _ = metricas(casos, analizar_propio(casos))
        self.assertEqual((m["TP"], m["FP"], m["FN"], m["TN"]), (37, 0, 19, 15))
        self.assertEqual((m["precision"][0], m["rechazo_correcto"][0]), (1.0, 1.0))


@unittest.skipUnless(_hay("spacy", "es_core_news_sm"), "spaCy o es_core_news_sm no están instalados")
class TestSpacy(unittest.TestCase):
    def test_crudo_acepta_todo(self):
        from tlp.espanol.comparacion_nlp import analizar_spacy
        casos = cargar_conjunto()[:5]
        (crudo, concordancia), _ = analizar_spacy(casos, "sm")
        self.assertEqual(len(crudo.analisis), 5)
        self.assertTrue(all(a.acepta for a in crudo.analisis))
        self.assertEqual(len(concordancia.analisis), 5)


@unittest.skipUnless(_hay("transformers", "torch"), "transformers o torch no están instalados")
class TestHuggingFace(unittest.TestCase):
    def test_una_etiqueta_por_palabra(self):
        from tlp.espanol.comparacion_nlp import EtiquetadorHF
        try:
            etiquetador = EtiquetadorHF()
        except OSError as e:                                  # sin conexión y sin el modelo en caché
            self.skipTest(str(e))
        etiquetas = etiquetador.etiquetar(["el", "gato", "duerme"])
        self.assertEqual(len(etiquetas), 3)
        self.assertTrue(set(etiquetas) <= set(etiquetador.modelo.config.id2label.values()))


if __name__ == "__main__":
    unittest.main()
