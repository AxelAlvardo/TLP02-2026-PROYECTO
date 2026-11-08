"""lexer.py - Analizador léxico de Mini-C. Un carácter ilegal es un ERROR, nunca se descarta en silencio."""
from __future__ import annotations

import re
from collections import namedtuple

from .gramatica import RELOPS, PALABRAS_CLAVE

Token = namedtuple("Token", "tipo valor linea col")


class ErrorSintactico(Exception):
    def __init__(self, mensaje: str, linea: int, col: int):
        super().__init__(f"Línea {linea}, col {col}: {mensaje}")
        self.mensaje, self.linea, self.col = mensaje, linea, col


_PATRON = re.compile(r"""
    (?P<ESP>[ \t\r]+) | (?P<NL>\n) | (?P<COM>//[^\n]*) |
    (?P<NUM>\d+) | (?P<ID>[A-Za-z_][A-Za-z_0-9]*) |
    (?P<OP>==|!=|<=|>=|[-+*/=<>(){};])
""", re.VERBOSE)


def tokenizar(codigo: str) -> list[Token]:
    """Convierte texto en tokens. Un carácter ilegal es un ERROR (no se descarta en silencio)."""
    toks, i, linea, col0 = [], 0, 1, 0
    while i < len(codigo):
        m = _PATRON.match(codigo, i)
        if not m:
            raise ErrorSintactico(f"carácter ilegal {codigo[i]!r}", linea, i - col0 + 1)
        k, v = m.lastgroup, m.group()
        col = i - col0 + 1
        if k == "NL":
            linea, col0 = linea + 1, m.end()
        elif k in ("NUM", "OP"):
            toks.append(Token("RELOP" if v in RELOPS else v if k == "OP" else "NUM", v, linea, col))
        elif k == "ID":
            toks.append(Token(v if v in PALABRAS_CLAVE else "ID", v, linea, col))
        i = m.end()
    toks.append(Token("$", "fin de entrada", linea, len(codigo) - col0 + 1))
    return toks
