"""Pruebas del experimento con LLM (Fase 2, punto 6) con un LLM SIMULADO: no se llama a ninguna API.
python -m unittest tests.test_llm_experimento -v"""
import importlib.util
import json
import os
import tempfile
import unittest
from collections import Counter
from types import SimpleNamespace
from unittest import mock

from tlp.espanol import llm_experimento as le
from tlp.espanol.conjunto import cargar_conjunto
from tlp.espanol.gramatica_es import REGLAS_BNF


_TEMPORAL = tempfile.TemporaryDirectory()            # se borra al terminar las pruebas


def _archivo(contenido, nombre):
    d = tempfile.mkdtemp(dir=_TEMPORAL.name)
    ruta = os.path.join(d, nombre)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(contenido)
    return ruta


class TestConfiguracion(unittest.TestCase):
    def test_una_clave_elige_el_proveedor(self):
        for variable, proveedor in le.PROVEEDORES.items():
            with self.subTest(variable=variable):
                valores = le.leer_env(_archivo(f"# comentario\n{variable}=abc123\nLLM_MODELO=modelo-x\n", ".env"))
                self.assertEqual(le.elegir_proveedor(valores), (proveedor, "abc123", "modelo-x"))

    def test_errores_de_configuracion(self):
        for texto in ("LLM_MODELO=m\n",                                        # ninguna clave
                      "OPENAI_API_KEY=a\nGEMINI_API_KEY=b\nLLM_MODELO=m\n",    # dos claves
                      "OPENAI_API_KEY=a\nLLM_MODELO=\n"):                      # sin modelo
            with self.subTest(texto=texto), self.assertRaises(le.ErrorConfiguracion):
                le.elegir_proveedor(le.leer_env(_archivo(texto, ".env")))
        with self.assertRaises(le.ErrorConfiguracion):
            le.leer_env(os.path.join(_TEMPORAL.name, "no-existe", ".env"))

    def test_plantilla_env_sin_claves(self):
        valores = le.leer_env(os.path.join(le.RAIZ, ".env.ejemplo"))
        self.assertEqual(valores, {"ANTHROPIC_API_KEY": "", "OPENAI_API_KEY": "", "GEMINI_API_KEY": "", "LLM_MODELO": ""})


class TestPrompt(unittest.TestCase):
    def test_prompt_del_proyecto(self):
        sistema, plantilla = le.leer_prompt()
        self.assertIn("analizador sintáctico FORMAL", sistema)
        mensaje = le.completar(plantilla, "el gato corre")
        self.assertIn(REGLAS_BNF, mensaje)
        self.assertTrue(mensaje.endswith("Oración: el gato corre"))
        for marca in ("{gramatica}", "{lexico}", "{oracion}"):
            self.assertNotIn(marca, mensaje)
        self.assertEqual(le.contar_ejemplos(plantilla), 6)

    def test_ejemplos_fuera_del_conjunto(self):
        _, plantilla = le.leer_prompt()
        ejemplos = {l.split(":", 1)[1].strip() for l in plantilla.splitlines()
                    if l.startswith("Oración:") and "{oracion}" not in l}
        self.assertFalse(ejemplos & {c.oracion for c in cargar_conjunto()})

    def test_zero_shot_y_prompts_invalidos(self):
        sistema, plantilla = le.leer_prompt(_archivo("# nota\n=== SISTEMA ===\nS\n=== USUARIO ===\n{gramatica}\n"
                                                     "Oración: {oracion}\n", "p.txt"))
        self.assertEqual((sistema, le.contar_ejemplos(plantilla)), ("S", 0))
        for texto in ("=== SISTEMA ===\nS\n=== USUARIO ===\nsin marca\n", "solo texto {oracion}\n"):
            with self.subTest(texto=texto), self.assertRaises(le.ErrorConfiguracion):
                le.leer_prompt(_archivo(texto, "p.txt"))


class TestRespuestas(unittest.TestCase):
    def test_veredicto(self):
        self.assertTrue(le._veredicto(le.extraer_json('```json\n{"acepta": true, "arbol": null}\n```')))
        self.assertFalse(le._veredicto(le.extraer_json('{"acepta": "false"}')))
        self.assertIsNone(le._veredicto(le.extraer_json("no sé")))


class TestExperimentoSimulado(unittest.TestCase):
    def test_llm_que_piensa_en_espanol(self):
        casos = cargar_conjunto()
        por_oracion = {c.oracion: c for c in casos}

        def falso(sistema, mensaje):                 # acepta todo lo que es español correcto, ignora la gramática
            oracion = mensaje.rsplit("Oración: ", 1)[1].strip()
            return json.dumps({"acepta": por_oracion[oracion].gramatical_es, "arbol": None}), ""

        sistema, plantilla = le.leer_prompt()
        respuestas = le.ejecutar(casos, falso, sistema, plantilla, progreso=lambda _: None)
        cuenta = Counter(r.resultado for r in respuestas)
        self.assertEqual((cuenta["coincide"], cuenta["desviación hacia el español"]), (52, 19))
        with tempfile.TemporaryDirectory() as d:
            ruta = le.escribir_md(respuestas, "simulado", "falso", sistema, plantilla, os.path.join(d, "r.md"))
            with open(ruta, encoding="utf-8") as f:
                texto = f.read()
        self.assertIn("| Coincide con la gramática | 52/71 |", texto)
        self.assertIn("es español correcto) | 19 |", texto)
        self.assertEqual(texto.count("\n### ["), 71)
        self.assertIn(REGLAS_BNF, texto)

    def test_primera_llamada_fallida_detiene(self):
        def roto(sistema, mensaje):
            raise RuntimeError("401 invalid api key")
        with self.assertRaises(le.ErrorConfiguracion):
            le.ejecutar(cargar_conjunto()[:3], roto, "S", "Oración: {oracion}", progreso=lambda _: None)


@unittest.skipUnless(all(importlib.util.find_spec(m) for m in ("anthropic", "openai", "google.genai")),
                     "faltan los SDK de los proveedores")
class TestClientes(unittest.TestCase):
    def test_se_crean_sin_conexion(self):
        for proveedor in ("claude", "chatgpt", "gemini"):
            with self.subTest(proveedor=proveedor):
                self.assertTrue(callable(le.crear_cliente(proveedor, "clave-falsa", "modelo-falso")))

    def test_reintenta_sin_temperatura(self):
        def create(**kw):
            if "temperature" in kw:
                raise RuntimeError("temperature is not supported for this model")
            return SimpleNamespace(content=[SimpleNamespace(type="text", text='{"acepta": true}')])

        falso = SimpleNamespace(messages=SimpleNamespace(create=create))
        with mock.patch("anthropic.Anthropic", return_value=falso):
            texto, nota = le.crear_cliente("claude", "clave", "modelo")("S", "M")
        self.assertEqual(texto, '{"acepta": true}')
        self.assertIn("temperature", nota)


if __name__ == "__main__":
    unittest.main()
