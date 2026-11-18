"""tlp/espanol/conjunto.py - Fase 2: conjunto de prueba del español (casos/espanol/conjunto_prueba.csv).

Columnas del CSV (salida esperada de cada oración):
  id, nivel           nivel 1 = simple (la gramática debe aceptarla), 2 = intermedia (modificadores y variaciones),
                      3 = compleja (fenómenos que probablemente exceden la gramática)
  oracion
  gramatical_es       SI / NO: ¿es español correcto? (juicio humano, independiente de la gramática)
  esperado_gramatica  ACEPTA / RECHAZA: lo que debe responder el parser con esta gramática
  fenomeno            fenómeno lingüístico que se prueba
  sujeto, verbo, objeto  lemas esperados; '-' = no hay (intransitiva o sujeto tácito), '*' = cláusula o no aplica;
                         vacíos si la oración no es español correcto
"""
from __future__ import annotations

import csv
import os
from dataclasses import dataclass

from ..arbol import Node
from .gramatica_es import ParserEspanol, extraer_svo

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RUTA_CONJUNTO = os.path.join(RAIZ, "casos", "espanol", "conjunto_prueba.csv")


@dataclass(frozen=True)
class Caso:
    """Una oración del conjunto con su salida esperada."""
    id: int
    nivel: int
    oracion: str
    gramatical_es: bool
    esperado: str                          # "ACEPTA" | "RECHAZA"
    fenomeno: str
    svo: tuple[str, str, str] | None       # None si la oración no es español correcto


def cargar_conjunto(ruta: str = RUTA_CONJUNTO) -> list[Caso]:
    with open(ruta, encoding="utf-8", newline="") as f:
        return [Caso(id=int(r["id"]), nivel=int(r["nivel"]), oracion=r["oracion"],
                     gramatical_es=r["gramatical_es"] == "SI", esperado=r["esperado_gramatica"],
                     fenomeno=r["fenomeno"],
                     svo=(r["sujeto"], r["verbo"], r["objeto"]) if r["sujeto"] else None)
                for r in csv.DictReader(f)]


@dataclass
class Resultado:
    """Lo que hizo el parser con un caso."""
    caso: Caso
    arboles: list[Node]                    # todas las derivaciones; vacía si la rechazó
    diagnostico: str                       # "N derivación(es)" o la regla que falla

    @property
    def obtenido(self) -> str:
        return "ACEPTA" if self.arboles else "RECHAZA"

    @property
    def coincide(self) -> bool:
        return self.obtenido == self.caso.esperado

    @property
    def svo(self) -> tuple[str, str, str] | None:
        return extraer_svo(self.arboles[0]) if self.arboles else None


def evaluar(casos: list[Caso], parser: ParserEspanol | None = None) -> list[Resultado]:
    """Analiza cada caso con el parser propio y devuelve su resultado (el veredicto se compara con `coincide`)."""
    parser = parser or ParserEspanol()
    resultados = []
    for c in casos:
        arbol, diagnostico = parser.parse(c.oracion)
        arboles = parser.parse_todos(c.oracion) if arbol else []
        resultados.append(Resultado(c, arboles, diagnostico))
    return resultados
