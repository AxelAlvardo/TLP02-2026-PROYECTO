"""parser.py - Parser descendente recursivo (una función por no terminal, lookahead 1 => LL(1)).

Construye el árbol de análisis (colapsa ExprR/TermR en nodos binarios asociativos por la izquierda),
reporta errores con línea y columna y ofrece recuperación en modo pánico.
"""
from __future__ import annotations

from ..arbol import Node
from .lexer import ErrorSintactico, Token, tokenizar


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
