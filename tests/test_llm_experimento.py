"""Pruebas del experimento con LLM (Fase 2, punto 6) con un LLM SIMULADO: no se llama a ninguna API.
python -m unittest tests.test_llm_experimento -v"""
import importlib.util
import json
import os
import tempfile
import unittest
from collections import Counter
from datetime import datetime
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


def _prompts():
    return {v: le.leer_prompt(le.ruta_prompt(v)) for v in le.VARIANTES}


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


class TestPrompts(unittest.TestCase):
    def test_cuatro_variantes(self):
        """sin_ejemplos: ni instrucciones ni ejemplos; zero_shot: instrucciones; few_shot: ejemplos; combinado: ambos."""
        esperado = {"sin_ejemplos": (False, 0), "zero_shot": (True, 0), "few_shot": (False, 6), "combinado": (True, 6)}
        for v, (sistema, plantilla) in _prompts().items():
            with self.subTest(variante=v):
                self.assertEqual((bool(sistema), le.contar_ejemplos(plantilla)), esperado[v])

    def test_diseno_dos_por_dos(self):
        """Las variantes solo difieren en las instrucciones de sistema y en los ejemplos; el resto es idéntico."""
        p = _prompts()
        self.assertEqual(p["sin_ejemplos"][1], p["zero_shot"][1])
        self.assertEqual(p["few_shot"][1], p["combinado"][1])
        self.assertEqual(p["zero_shot"][0], p["combinado"][0])
        self.assertIn("analizador sintáctico FORMAL", p["zero_shot"][0])
        con_ejemplos = p["few_shot"][1]
        sin_bloque = (con_ejemplos[:con_ejemplos.index("EJEMPLOS RESUELTOS:")]
                      + con_ejemplos[con_ejemplos.index("Analiza esta oración:"):])
        self.assertEqual(sin_bloque, p["sin_ejemplos"][1])

    def test_mensaje_completo(self):
        for v, (_, plantilla) in _prompts().items():
            with self.subTest(variante=v):
                mensaje = le.completar(plantilla, "el gato corre")
                self.assertIn(REGLAS_BNF, mensaje)
                self.assertTrue(mensaje.endswith("Oración: el gato corre"))
                for marca in ("{gramatica}", "{lexico}", "{oracion}"):
                    self.assertNotIn(marca, mensaje)

    def test_ejemplos_fuera_del_conjunto(self):
        corpus = {c.oracion for c in cargar_conjunto()}
        for v in ("few_shot", "combinado"):
            _, plantilla = le.leer_prompt(le.ruta_prompt(v))
            ejemplos = {l.split(":", 1)[1].strip() for l in plantilla.splitlines()
                        if l.startswith("Oración:") and "{oracion}" not in l}
            self.assertEqual(len(ejemplos), 6)
            self.assertFalse(ejemplos & corpus)

    def test_prompts_invalidos(self):
        self.assertEqual(le.leer_prompt(_archivo("=== SISTEMA ===\n=== USUARIO ===\nOración: {oracion}\n", "p.txt")),
                         ("", "Oración: {oracion}"))
        for texto in ("=== SISTEMA ===\nS\n=== USUARIO ===\nsin marca\n", "solo texto {oracion}\n"):
            with self.subTest(texto=texto), self.assertRaises(le.ErrorConfiguracion):
                le.leer_prompt(_archivo(texto, "p.txt"))
        with self.assertRaises(le.ErrorConfiguracion):
            le.leer_prompt(os.path.join(_TEMPORAL.name, "no-existe.txt"))


class TestRespuestas(unittest.TestCase):
    def test_veredicto(self):
        self.assertTrue(le.veredicto(le.extraer_json('```json\n{"acepta": true, "arbol": null}\n```')))
        self.assertFalse(le.veredicto(le.extraer_json('{"acepta": "false"}')))
        self.assertIsNone(le.veredicto(le.extraer_json("no sé")))


class TestExperimentoSimulado(unittest.TestCase):
    def test_llm_que_piensa_en_espanol(self):
        casos = cargar_conjunto()
        por_oracion = {c.oracion: c for c in casos}

        def falso(sistema, mensaje):                 # acepta todo lo que es español correcto, ignora la gramática
            oracion = mensaje.rsplit("Oración: ", 1)[1].strip()
            return le.Llamada(json.dumps({"acepta": por_oracion[oracion].gramatical_es, "arbol": None}), 0,
                              "modelo-falso-001")

        sistema, plantilla = le.leer_prompt(le.ruta_prompt("zero_shot"))
        meta = {"variante": "zero_shot", "proveedor": "simulado", "modelo": "falso", "sdk": "ninguno 0.0",
                "prompt_archivo": "casos/espanol/prompts/zero_shot.txt", "log": "logs/llm_zero_shot.jsonl"}
        with tempfile.TemporaryDirectory() as d:
            ruta_log = os.path.join(d, "logs", "llm_zero_shot.jsonl")
            respuestas = le.ejecutar(casos, falso, sistema, plantilla, progreso=lambda _: None,
                                     ruta_log=ruta_log, meta=meta)
            with open(ruta_log, encoding="utf-8") as f:
                registros = [json.loads(l) for l in f]
            ruta = le.escribir_md(respuestas, meta, sistema, plantilla, os.path.join(d, "r.md"))
            with open(ruta, encoding="utf-8") as f:
                texto = f.read()
        cuenta = Counter(r.resultado for r in respuestas)
        self.assertEqual((cuenta["coincide"], cuenta["desviación hacia el español"]), (52, 19))
        # log bruto: una línea por llamada, con timestamp, modelo, parámetros, prompt enviado y respuesta cruda
        self.assertEqual([r["id"] for r in registros], [c.id for c in casos])
        marcas = [datetime.fromisoformat(r["timestamp"]) for r in registros]
        self.assertEqual(marcas, sorted(marcas))
        for r, c in zip(registros, casos):
            self.assertEqual((r["variante"], r["oracion"], r["modelo"], r["modelo_respuesta"]),
                             ("zero_shot", c.oracion, "falso", "modelo-falso-001"))
            self.assertEqual(r["parametros"], {"temperature": 0, "max_tokens": le.MAX_TOKENS})
            self.assertEqual(r["prompt_sistema"], sistema)
            self.assertTrue(r["prompt_usuario"].endswith(f"Oración: {c.oracion}"))
            self.assertEqual(json.loads(r["respuesta"])["acepta"], c.gramatical_es)
        # resumen legible
        self.assertIn("| Coincide con la gramática | 52/71 |", texto)
        self.assertIn("es español correcto) | 19 |", texto)
        self.assertIn("temperature = 0", texto)
        self.assertIn("la API reporta: modelo-falso-001", texto)
        self.assertEqual(texto.count("\n### ["), 71)
        self.assertEqual(texto.count("\n- Llamada: "), 71)
        self.assertIn(REGLAS_BNF, texto)

    def test_primera_llamada_fallida_detiene(self):
        def roto(sistema, mensaje):
            raise RuntimeError("401 invalid api key")
        with self.assertRaises(le.ErrorConfiguracion):
            le.ejecutar(cargar_conjunto()[:3], roto, "S", "Oración: {oracion}", progreso=lambda _: None)

    def test_variante_obligatoria(self):
        with mock.patch("sys.stderr"), self.assertRaises(SystemExit):
            le.main([])


@unittest.skipUnless(all(importlib.util.find_spec(m) for m in ("anthropic", "openai", "google.genai")),
                     "faltan los SDK de los proveedores")
class TestClientes(unittest.TestCase):
    def test_se_crean_sin_conexion(self):
        for proveedor in ("claude", "chatgpt", "gemini"):
            with self.subTest(proveedor=proveedor):
                self.assertTrue(callable(le.crear_cliente(proveedor, "clave-falsa", "modelo-falso")))

    def _claude_falso(self, llamadas, rechaza_temperatura=False, fallos=()):
        pendientes = list(fallos)                             # errores que da antes de responder bien

        def create(**kw):
            llamadas.append(kw)
            if rechaza_temperatura and "temperature" in kw:
                raise RuntimeError("temperature is not supported for this model")
            if pendientes:
                raise RuntimeError(pendientes.pop(0))
            return SimpleNamespace(content=[SimpleNamespace(type="text", text='{"acepta": true}')], model="claude-x")
        return SimpleNamespace(messages=SimpleNamespace(create=create))

    def test_reintenta_sin_temperatura_y_lo_recuerda(self):
        llamadas = []
        with mock.patch("anthropic.Anthropic", return_value=self._claude_falso(llamadas, rechaza_temperatura=True)):
            llamar = le.crear_cliente("claude", "clave", "modelo")
            primera, segunda = llamar("S", "M"), llamar("S", "M")
        self.assertEqual((primera.texto, primera.temperature, primera.modelo_respuesta), ('{"acepta": true}', None,
                                                                                          "claude-x"))
        self.assertIn("temperature", primera.nota)
        self.assertEqual(len(llamadas), 3)                    # 1.ª: con y sin temperatura; 2.ª: directo sin ella
        self.assertIsNone(segunda.temperature)

    def test_sin_sistema_no_se_envia(self):
        llamadas = []
        with mock.patch("anthropic.Anthropic", return_value=self._claude_falso(llamadas)):
            llamar = le.crear_cliente("claude", "clave", "modelo")
            llamar("", "M")
            llamar("S", "M")
        self.assertNotIn("system", llamadas[0])
        self.assertEqual(llamadas[1]["system"], "S")
        self.assertEqual(llamadas[0]["temperature"], 0)

    def test_reintenta_si_el_servidor_esta_saturado(self):
        """Un 503 se reintenta tras esperar y la oración queda guardada sin error. Si el proveedor sigue saturado,
        el mensaje lo dice y no manda a revisar el .env. No espera de verdad: time.sleep está simulado."""
        llamadas, saturado = [], "503 UNAVAILABLE. This model is currently experiencing high demand."
        casos = cargar_conjunto()[:1]
        with tempfile.TemporaryDirectory() as d, mock.patch.object(le.time, "sleep") as dormir, \
                mock.patch("anthropic.Anthropic", return_value=self._claude_falso(llamadas, fallos=[saturado])):
            ruta_log = os.path.join(d, "llm_few_shot.jsonl")
            (r,) = le.ejecutar(casos, le.crear_cliente("claude", "clave", "modelo"), "S", "Oración: {oracion}",
                               progreso=lambda _: None, ruta_log=ruta_log)
            with open(ruta_log, encoding="utf-8") as f:
                registro = json.loads(f.readline())
        self.assertEqual(len(llamadas), 2)                    # la que dio 503 y el reintento
        dormir.assert_called_once_with(le.ESPERAS_LIMITE[0])
        self.assertEqual((r.error, r.llm), ("", True))
        self.assertEqual((registro["error"], registro["respuesta"]), ("", '{"acepta": true}'))

        with mock.patch.object(le.time, "sleep"), \
                mock.patch("anthropic.Anthropic", return_value=self._claude_falso([], fallos=[saturado] * 10)), \
                self.assertRaises(le.ErrorConfiguracion) as error:
            le.ejecutar(casos, le.crear_cliente("claude", "clave", "modelo"), "S", "Oración: {oracion}",
                        progreso=lambda _: None)
        self.assertIn("saturado", str(error.exception))
        self.assertNotIn(".env", str(error.exception))


if __name__ == "__main__":
    unittest.main()
