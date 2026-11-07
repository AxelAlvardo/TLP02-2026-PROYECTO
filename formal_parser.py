"""formal_parser.py - Parser LL(1) / descendente recursivo para "Mini-C".

Subconjunto de C soportado (Fase 1, objetivo 1):
    declaraciones   int x;   int x = expr;
    asignaciones    x = expr;
    condicionales   if (cond) { ... } else { ... }
    ciclos          while (cond) { ... }
    salida          print(expr);
    bloques         { ... }
    expresiones     + - * /  paréntesis, negación unaria, comparaciones == != < > <= >=
    comentarios     // hasta fin de línea

Gramática BNF (sin recursión izquierda y factorizada => LL(1)).  Es la fuente de verdad:
`verificar_ll1()` calcula FIRST/FOLLOW sobre ESTE diccionario y comprueba que no hay conflictos.
Las llaves son obligatorias en if/while, lo que elimina la ambigüedad del "else colgante".

El analizador produce un árbol de análisis (colapsa las cadenas ExprR/TermR en nodos
binarios asociativos por la izquierda) y reporta errores con línea y columna.
"""
from __future__ import annotations

import re
import sys
from collections import namedtuple

from arbol import Node

EPS = "ε"
GRAMATICA: dict[str, list[list[str]]] = {
    "Programa": [["Stmts"]],
    "Stmts":    [["Stmt", "Stmts"], [EPS]],
    "Stmt":     [["int", "ID", "Init", ";"],
                 ["ID", "=", "Expr", ";"],
                 ["if", "(", "Cond", ")", "Bloque", "Else"],
                 ["while", "(", "Cond", ")", "Bloque"],
                 ["print", "(", "Expr", ")", ";"],
                 ["Bloque"]],
    "Init":     [["=", "Expr"], [EPS]],
    "Else":     [["else", "Bloque"], [EPS]],
    "Bloque":   [["{", "Stmts", "}"]],
    "Cond":     [["Expr", "CondR"]],
    "CondR":    [["RELOP", "Expr"], [EPS]],
    "Expr":     [["Term", "ExprR"]],
    "ExprR":    [["+", "Term", "ExprR"], ["-", "Term", "ExprR"], [EPS]],
    "Term":     [["Factor", "TermR"]],
    "TermR":    [["*", "Factor", "TermR"], ["/", "Factor", "TermR"], [EPS]],
    "Factor":   [["NUM"], ["ID"], ["(", "Expr", ")"], ["-", "Factor"]],
}
RELOPS = {"==", "!=", "<", ">", "<=", ">="}
PALABRAS_CLAVE = {"int", "if", "else", "while", "print"}


# ---------------------------------------------------------------------------
# Verificación formal de que la gramática es LL(1)
# ---------------------------------------------------------------------------
def _terminal_de(simbolo: str) -> str:
    return "RELOP" if simbolo in RELOPS else simbolo


def calcular_first_follow(gram=GRAMATICA, inicio="Programa"):
    first = {nt: set() for nt in gram}

    def first_seq(seq):
        res = set()
        for s in seq:
            if s == EPS:
                continue
            if s not in gram:
                res.add(s)
                return res
            res |= first[s] - {EPS}
            if EPS not in first[s]:
                return res
        res.add(EPS)
        return res

    cambio = True
    while cambio:
        cambio = False
        for nt, prods in gram.items():
            for p in prods:
                nuevo = first_seq(p)
                if not nuevo <= first[nt]:
                    first[nt] |= nuevo
                    cambio = True
    follow = {nt: set() for nt in gram}
    follow[inicio].add("$")
    cambio = True
    while cambio:
        cambio = False
        for nt, prods in gram.items():
            for p in prods:
                for i, s in enumerate(p):
                    if s not in gram:
                        continue
                    resto = first_seq(p[i + 1:])
                    nuevo = resto - {EPS}
                    if EPS in resto:
                        nuevo |= follow[nt]
                    if not nuevo <= follow[s]:
                        follow[s] |= nuevo
                        cambio = True
    return first, follow, first_seq


def verificar_ll1(gram=GRAMATICA) -> list[str]:
    """Devuelve la lista de conflictos LL(1). Lista vacía == la gramática es LL(1)."""
    first, follow, first_seq = calcular_first_follow(gram)
    conflictos = []
    for nt, prods in gram.items():
        for i in range(len(prods)):
            for j in range(i + 1, len(prods)):
                fi, fj = first_seq(prods[i]), first_seq(prods[j])
                inter = (fi - {EPS}) & (fj - {EPS})
                if inter:
                    conflictos.append(f"{nt}: FIRST({prods[i]}) ∩ FIRST({prods[j]}) = {inter}")
                if EPS in fi and (fj - {EPS}) & follow[nt]:
                    conflictos.append(f"{nt}: FIRST({prods[j]}) ∩ FOLLOW({nt}) ≠ ∅")
                if EPS in fj and (fi - {EPS}) & follow[nt]:
                    conflictos.append(f"{nt}: FIRST({prods[i]}) ∩ FOLLOW({nt}) ≠ ∅")
    return conflictos


# ---------------------------------------------------------------------------
# Léxico
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Parser descendente recursivo (una función por no terminal)
# ---------------------------------------------------------------------------
class FormalParser:
    def __init__(self, codigo: str):
        self.toks = tokenizar(codigo)
        self.i = 0
        self.errores: list[ErrorSintactico] = []

    # utilidades
    @property
    def la(self) -> Token:          # lookahead de 1 token => LL(1)
        return self.toks[self.i]

    def consumir(self, tipo: str) -> Token:
        t = self.la
        if t.tipo != tipo:
            raise ErrorSintactico(f"se esperaba '{tipo}' pero llegó '{t.valor}'", t.linea, t.col)
        self.i += 1
        return t

    # Programa -> Stmts
    def programa(self, recuperar: bool = False) -> Node:
        hijos = []
        while self.la.tipo not in ("$", "}"):
            try:
                hijos.append(self.stmt())
            except ErrorSintactico as e:
                if not recuperar:
                    raise
                self.errores.append(e)
                self._sincronizar()
        if self.la.tipo != "$":
            t = self.la
            err = ErrorSintactico(f"'}}' sin su '{{' correspondiente", t.linea, t.col)
            if not recuperar:
                raise err
            self.errores.append(err)
        return Node("Programa", hijos)

    def _sincronizar(self):
        """Recuperación en modo pánico: salta hasta después del próximo ';' (o antes de '}' / fin)."""
        while self.la.tipo not in ("$", "}"):
            if self.la.tipo == ";":
                self.i += 1
                return
            self.i += 1

    def stmts_hasta_llave(self) -> list[Node]:
        hijos = []
        while self.la.tipo not in ("$", "}"):
            hijos.append(self.stmt())
        return hijos

    def stmt(self) -> Node:
        t = self.la.tipo
        if t == "int":
            self.consumir("int")
            nombre = self.consumir("ID").valor
            hijos = [Node(nombre)]
            if self.la.tipo == "=":            # Init -> = Expr | ε
                self.consumir("=")
                hijos.append(self.expr())
            self.consumir(";")
            return Node("Declaracion", hijos)
        if t == "ID":
            nombre = self.consumir("ID").valor
            self.consumir("=")
            valor = self.expr()
            self.consumir(";")
            return Node("Asignacion", [Node(nombre), valor])
        if t == "if":
            self.consumir("if"); self.consumir("(")
            cond = self.cond()
            self.consumir(")")
            hijos = [cond, self.bloque()]
            if self.la.tipo == "else":         # Else -> else Bloque | ε
                self.consumir("else")
                hijos.append(self.bloque())
            return Node("If", hijos)
        if t == "while":
            self.consumir("while"); self.consumir("(")
            cond = self.cond()
            self.consumir(")")
            return Node("While", [cond, self.bloque()])
        if t == "print":
            self.consumir("print"); self.consumir("(")
            e = self.expr()
            self.consumir(")"); self.consumir(";")
            return Node("Print", [e])
        if t == "{":
            return self.bloque()
        tk = self.la
        raise ErrorSintactico(f"no puede comenzar una sentencia con '{tk.valor}'", tk.linea, tk.col)

    def bloque(self) -> Node:
        self.consumir("{")
        hijos = self.stmts_hasta_llave()
        self.consumir("}")
        return Node("Bloque", hijos)

    def cond(self) -> Node:
        izq = self.expr()
        if self.la.tipo == "RELOP":            # CondR -> RELOP Expr | ε
            op = self.consumir("RELOP").valor
            return Node(f"Cond({op})", [izq, self.expr()])
        return Node("Cond", [izq])

    def expr(self) -> Node:                    # Expr -> Term ExprR
        nodo = self.term()
        while self.la.tipo in ("+", "-"):
            op = self.consumir(self.la.tipo).tipo
            nodo = Node(f"Op({op})", [nodo, self.term()])
        return nodo

    def term(self) -> Node:                    # Term -> Factor TermR
        nodo = self.factor()
        while self.la.tipo in ("*", "/"):
            op = self.consumir(self.la.tipo).tipo
            nodo = Node(f"Op({op})", [nodo, self.factor()])
        return nodo

    def factor(self) -> Node:
        t = self.la
        if t.tipo == "NUM":
            return Node(self.consumir("NUM").valor)
        if t.tipo == "ID":
            return Node(self.consumir("ID").valor)
        if t.tipo == "(":
            self.consumir("(")
            e = self.expr()
            self.consumir(")")
            return e
        if t.tipo == "-":
            self.consumir("-")
            return Node("Neg", [self.factor()])
        raise ErrorSintactico(f"se esperaba número, variable, '(' o '-' pero llegó '{t.valor}'", t.linea, t.col)


def analizar(codigo: str, recuperar: bool = False) -> tuple[Node | None, list[ErrorSintactico]]:
    """API principal. Devuelve (árbol, errores). Sin `recuperar`, el primer error se lanza."""
    p = FormalParser(codigo)
    arbol = p.programa(recuperar=recuperar)
    return arbol, p.errores


if __name__ == "__main__":
    fuente = open(sys.argv[1], encoding="utf-8").read() if len(sys.argv) > 1 else \
        "int x = 5 + 3 * 2;\nif (x > 10) { print(x); } else { x = x - 1; }\nwhile (x > 0) { x = x - 1; }\n"
    print("Gramática LL(1):", "SÍ" if not verificar_ll1() else verificar_ll1())
    arbol, _ = analizar(fuente)
    print(arbol.indentado())
