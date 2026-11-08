"""Pruebas del script de apoyo (contraste con NLTK y spaCy).  Se omiten si spaCy/modelo no están instalados."""
import unittest

from tlp.apoyo.contraste_nlp import cargar_spacy, contrastar

NLP = cargar_spacy()


class TestContraste(unittest.TestCase):
    def test_parser_propio_y_nltk_coinciden(self):
        for f in contrastar(["el gato negro persigue al ratón", "los niños duerme", "el hombre ve al gato con el telescopio"]):
            self.assertEqual(f["propio"] == "ACEPTA", f["nltk"].startswith("ACEPTA"), f["oracion"])

    @unittest.skipIf(NLP is None, "modelo es_core_news_sm no instalado")
    def test_spacy_nunca_rechaza(self):
        fila = contrastar(["los niños duerme"])[0]
        self.assertEqual(fila["propio"], "RECHAZA")
        self.assertIsNotNone(fila["spacy"])                       # spaCy siempre devuelve un análisis
        self.assertTrue(fila["spacy"]["tokens"])

    @unittest.skipIf(NLP is None, "modelo es_core_news_sm no instalado")
    def test_spacy_analiza_oracion_correcta(self):
        s = contrastar(["el gato negro persigue al ratón"])[0]["spacy"]
        self.assertEqual(s["sujeto"], "gato")
        self.assertTrue(s["raiz"].startswith("persigue"))


if __name__ == "__main__":
    unittest.main()
