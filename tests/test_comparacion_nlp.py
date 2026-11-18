"""Pruebas de la corrida de parser propio, spaCy y HuggingFace y de sus logs (Fase 2, puntos 4 y 5).
python -m unittest tests.test_comparacion_nlp -v"""
import importlib.util
import json
import os
import tempfile
import unittest

from tlp.espanol.comparacion_nlp import analizar_propio, escribir_log, palabras_de, reglas_upos
from tlp.espanol.conjunto import cargar_conjunto

CAMPOS_COMUNES = ["sistema", "version", "id", "nivel", "oracion", "acepta", "motivo", "svo", "palabras", "etiquetas",
                  "ms"]


def _hay(*modulos):
    return all(importlib.util.find_spec(m) for m in modulos)


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

    def test_palabras_sin_puntuacion(self):
        self.assertEqual(palabras_de("María dice que el gato corre."), ["María", "dice", "que", "el", "gato", "corre"])


class TestLogParser(unittest.TestCase):
    def test_una_linea_por_oracion(self):
        casos = cargar_conjunto()
        registros = analizar_propio(casos)
        self.assertEqual([r["id"] for r in registros], [c.id for c in casos])
        self.assertEqual(sum(r["acepta"] for r in registros), 37)
        for r, c in zip(registros, casos):
            self.assertEqual(list(r)[:len(CAMPOS_COMUNES)], CAMPOS_COMUNES)
            self.assertEqual(r["acepta"], c.esperado == "ACEPTA")
            if r["acepta"]:
                self.assertTrue(r["derivaciones"] >= 1 and r["motivo"] == "")
                self.assertEqual(len(r["arboles"]), r["derivaciones"])         # un árbol por derivación
                self.assertTrue(all(a.startswith("(O ") for a in r["arboles"]))
                self.assertEqual(len(r["svo"]), 3)
            else:
                self.assertTrue(r["arboles"] == [] and r["derivaciones"] == 0 and r["motivo"])
        # las ambiguas guardan sus dos lecturas, distintas entre sí
        ambiguas = {r["id"]: r["arboles"] for r in registros if r["derivaciones"] > 1}
        self.assertEqual(sorted(ambiguas), [28, 29, 30, 35])
        for arboles in ambiguas.values():
            self.assertEqual(len(set(arboles)), 2)

    def test_el_log_se_relee_igual(self):
        registros = analizar_propio(cargar_conjunto()[:5])
        with tempfile.TemporaryDirectory() as d:
            ruta = escribir_log(registros, os.path.join(d, "logs", "parser.jsonl"))
            with open(ruta, encoding="utf-8") as f:
                self.assertEqual([json.loads(l) for l in f], registros)


@unittest.skipUnless(_hay("spacy", "es_core_news_sm"), "spaCy o es_core_news_sm no están instalados")
class TestSpacy(unittest.TestCase):
    def test_crudo_acepta_todo(self):
        from tlp.espanol.comparacion_nlp import analizar_spacy
        crudo, concordancia = analizar_spacy(cargar_conjunto()[:5], "sm")
        self.assertEqual((len(crudo), len(concordancia)), (5, 5))
        self.assertTrue(all(r["acepta"] for r in crudo))
        for r in crudo + concordancia:
            self.assertEqual(list(r)[:len(CAMPOS_COMUNES)], CAMPOS_COMUNES)
            self.assertTrue(r["tokens"] and {"texto", "lema", "upos", "dep", "cabeza", "morfologia"} <= set(r["tokens"][0]))


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
