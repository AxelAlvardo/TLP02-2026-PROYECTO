"""Pruebas del script de evaluación (Fase 2, punto 5): métricas leídas SOLO de los logs, con un LLM SIMULADO.
python -m unittest tests.test_evaluar -v"""
import filecmp
import importlib.util
import json
import math
import os
import tempfile
import unittest
from unittest import mock

from tlp.espanol import evaluar as ev
from tlp.espanol import llm_experimento as le
from tlp.espanol.comparacion_nlp import analizar_propio, escribir_log
from tlp.espanol.conjunto import Caso, cargar_conjunto
from tlp.espanol.gramatica_es import ParserEspanol, extraer_svo


def _caso(i, gramatical, deriva=None):
    return Caso(id=i, nivel=1, oracion=f"oración {i}", gramatical_es=gramatical,
                esperado="ACEPTA" if (gramatical if deriva is None else deriva) else "RECHAZA",
                fenomeno="prueba", svo=("gato", "perseguir", "ratón") if gramatical else None)


def _sistema(salidas, **kw):
    return ev.Sistema("prueba", "prueba.jsonl", "", {i: s for i, s in enumerate(salidas, 1)},
                      kw.get("da_svo", True), kw.get("da_categorias", False), kw.get("da_sin_respuesta", False))


def _logs_completos(d):
    """Log real del parser + log de un LLM simulado que acepta todo lo que es español correcto y copia el árbol
    del parser cuando la gramática lo deriva."""
    casos, parser = cargar_conjunto(), ParserEspanol()
    escribir_log(analizar_propio(casos), os.path.join(d, "parser.jsonl"))
    por_oracion = {c.oracion: c for c in casos}

    def falso(sistema, mensaje):
        c = por_oracion[mensaje.rsplit("Oración: ", 1)[1].strip()]
        arbol = parser.parse(c.oracion)[0]
        return le.Llamada(json.dumps({"acepta": c.gramatical_es, "arbol": arbol.bracket() if arbol else None}), 0,
                          "falso-001")
    sistema, plantilla = le.leer_prompt(le.ruta_prompt("few_shot"))
    le.ejecutar(casos, falso, sistema, plantilla, progreso=lambda _: None,
                ruta_log=os.path.join(d, "llm_few_shot.jsonl"),
                meta={"variante": "few_shot", "proveedor": "simulado", "modelo": "falso", "sdk": "ninguno 0.0",
                      "prompt_archivo": "casos/espanol/prompts/few_shot.txt"})


class TestMetricas(unittest.TestCase):
    def test_wilson(self):
        lo, hi = ev.wilson(5, 10)
        self.assertAlmostEqual(lo, 0.2366, places=4)
        self.assertAlmostEqual(hi, 0.7634, places=4)
        self.assertTrue(all(math.isnan(x) for x in ev.wilson(0, 0)))

    def test_dos_referencias(self):
        # 1: español y la gramática la deriva; 2: español que la gramática rechaza; 3 y 4: agramaticales
        casos = [_caso(1, True), _caso(2, True, deriva=False), _caso(3, False), _caso(4, False)]
        s = _sistema([ev.Salida(True), ev.Salida(True), ev.Salida(True), ev.Salida(False, "regla")])
        es, _ = ev.metricas(casos, s, "español")
        gr, _ = ev.metricas(casos, s, "gramática")
        self.assertEqual((es["TP"], es["FP"], es["FN"], es["TN"]), (2, 1, 0, 1))
        self.assertEqual((gr["TP"], gr["FP"], gr["FN"], gr["TN"]), (1, 2, 0, 1))
        self.assertEqual((gr["desviacion_es"], gr["acepta_agramatical"]), (1, 1))
        self.assertEqual((es["precision"][0], es["cobertura"][0], es["rechazo_correcto"][0]), (2 / 3, 1.0, 0.5))

    def test_sin_respuesta_no_entra_en_la_matriz(self):
        casos = [_caso(1, True), _caso(2, False)]
        s = _sistema([ev.Salida(None, "sin JSON"), ev.Salida(False, "regla")], da_sin_respuesta=True)
        m, errores = ev.metricas(casos, s, "español")
        self.assertEqual((m["n"], m["sin_respuesta"], m["TP"] + m["FP"] + m["FN"], m["TN"]), (2, 1, 0, 1))
        self.assertEqual([e["tipo"] for e in errores], ["sin respuesta válida"])

    def test_errores_de_etiquetado(self):
        s = _sistema([ev.Salida(True, svo=("perro", "perseguir", "ratón"), palabras=["el", "gato", "persigue"],
                                etiquetas=["DET", "NOUN", "NOUN"])], da_categorias=True)
        m, errores = ev.etiquetado([_caso(1, True)], s)
        self.assertEqual((m["err_svo"], m["err_cat"], m["exactitud_svo"]), (1, 1, 0.0))
        self.assertAlmostEqual(m["exactitud_categorias"], 2 / 3)
        self.assertEqual({e["tipo"] for e in errores},
                         {"error de etiquetado (S-V-O)", "error de etiquetado (categorías)"})

    def test_parser_contra_ambas_referencias(self):
        with tempfile.TemporaryDirectory() as d:
            escribir_log(analizar_propio(cargar_conjunto()), os.path.join(d, "parser.jsonl"))
            (r,) = ev.evaluar(cargar_conjunto(), ev.cargar_sistemas(d))
        es, gr = r.por_referencia["español"], r.por_referencia["gramática"]
        self.assertEqual((es["TP"], es["FP"], es["FN"], es["TN"]), (37, 0, 19, 15))
        self.assertEqual((gr["TP"], gr["FP"], gr["FN"], gr["TN"]), (37, 0, 0, 34))
        self.assertEqual(r.etiquetado["err_svo"], 0)


class TestSvoDelLLM(unittest.TestCase):
    def test_arbol_con_obj(self):
        arbol = ("(O (SN (Det[m,sg] el) (N[m,sg] gato)) (SV (V[pres,sg] persigue) "
                 "(Obj (A a) (SN (Det[m,sg] el) (N[m,sg] ratón)))))")
        self.assertEqual(ev.svo_de_arbol(arbol), ("gato", "perseguir", "ratón"))

    def test_intransitiva_completiva_e_ilegible(self):
        self.assertEqual(ev.svo_de_arbol("(O (SN (PN[f,sg] maría)) (SV (V[pres,sg] corre)))"), ("maría", "correr", "-"))
        self.assertEqual(ev.svo_de_arbol("(O (SN (PN[f,sg] maría)) (SV (V[pres,sg] dice) (Que que) "
                                         "(O (SN (Det[m,sg] el) (N[m,sg] gato)) (SV (V[pres,sg] corre)))))")[2], "*")
        for malo in (None, "", "(O (SN (N gato)", "(O (SV (V corre)))", "no es un árbol"):
            with self.subTest(arbol=malo):
                self.assertIsNone(ev.svo_de_arbol(malo))

    def test_coincide_con_el_parser(self):
        """Con los árboles del parser, svo_de_arbol da lo mismo que extraer_svo del propio parser."""
        parser = ParserEspanol()
        for c in cargar_conjunto():
            arbol = parser.parse(c.oracion)[0]
            if arbol:
                with self.subTest(oracion=c.oracion):
                    self.assertEqual(ev.svo_de_arbol(arbol.bracket()), extraer_svo(arbol))


class TestLogsDelLLM(unittest.TestCase):
    def test_lee_el_log_del_llm(self):
        with tempfile.TemporaryDirectory() as d:
            _logs_completos(d)
            sistemas = ev.cargar_sistemas(d)
            parser, llm = ev.evaluar(cargar_conjunto(), sistemas)
        self.assertEqual((parser.sistema.nombre, llm.sistema.nombre), ("Parser propio (CFG)", "LLM few-shot"))
        self.assertIn("modelo falso (la API reporta: falso-001)", llm.sistema.descripcion)
        es, gr = llm.por_referencia["español"], llm.por_referencia["gramática"]
        self.assertEqual((es["TP"], es["FP"], es["FN"], es["TN"]), (56, 0, 0, 15))
        self.assertEqual((gr["desviacion_es"], gr["acepta_agramatical"], gr["FN"]), (19, 0, 0))
        # aceptó sin árbol las que la gramática no deriva: error de S-V-O en las que tienen S-V-O evaluable
        sin_arbol = [c for c in cargar_conjunto() if c.gramatical_es and c.esperado == "RECHAZA"
                     and c.svo and any(x != "*" for x in c.svo)]
        self.assertEqual(llm.etiquetado["err_svo"], len(sin_arbol))


@unittest.skipUnless(importlib.util.find_spec("matplotlib"), "falta matplotlib")
class TestReproducible(unittest.TestCase):
    def test_mismos_logs_mismos_archivos(self):
        with tempfile.TemporaryDirectory() as d:
            logs, a, b = (os.path.join(d, x) for x in ("logs", "a", "b"))
            os.makedirs(logs)
            _logs_completos(logs)
            for salida in (a, b):
                with mock.patch("sys.stdout"):
                    self.assertEqual(ev.main(["--logs", logs, "--salida", salida]), 0)
            archivos = ["tablas.md", "metricas_globales.csv", "errores_detalle.csv", "grafica_metricas.png",
                        "grafica_errores.png"]
            iguales, distintos, _ = filecmp.cmpfiles(a, b, archivos, shallow=False)
        self.assertEqual((sorted(iguales), distintos), (sorted(archivos), []))

    def test_sin_logs(self):
        with tempfile.TemporaryDirectory() as d, mock.patch("sys.stderr"):
            self.assertEqual(ev.main(["--logs", os.path.join(d, "vacio"), "--salida", d]), 2)


if __name__ == "__main__":
    unittest.main()
