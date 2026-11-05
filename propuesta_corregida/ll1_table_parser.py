"""
Módulo 3: Parser LL(1) dirigido por tabla (con pila explícita).

Usa la tabla M[A, a] de `ll1_analysis.py` y produce el ÁRBOL DE DERIVACIÓN CONCRETO
(con todos los no terminales, incluidos ExprTail/TermTail/ε), que es el "árbol de
análisis sintáctico" de la teoría; el parser recursivo de `formal_parser.py` produce
el AST (abstracto). Ambos deben aceptar/rechazar exactamente las mismas entradas
(se verifica en test.py).
"""

from dataclasses import dataclass, field
from typing import List, Optional

from formal_parser import Lexer, SyntaxErrorException, Token
from ll1_analysis import EPS, END, GRAMMAR, START, build_table


@dataclass
class ParseNode:
    symbol: str
    token: Optional[Token] = None
    children: List['ParseNode'] = field(default_factory=list)

    def pretty_print(self, level: int = 0) -> str:
        indent = "  " * level
        label = self.symbol if self.token is None else f"{self.symbol} '{self.token.value}'"
        out = f"{indent}{label}\n"
        for c in self.children:
            out += c.pretty_print(level + 1)
        return out

    def leaves(self) -> List[str]:
        """Frontera del árbol (lexemas) — debe coincidir con la entrada."""
        if self.token is not None:
            return [self.token.value]
        out: List[str] = []
        for c in self.children:
            out += c.leaves()
        return out

    def to_dot(self) -> str:
        """Exporta a Graphviz DOT (dot -Tpng arbol.dot -o arbol.png)."""
        lines = ["digraph parse_tree {", "  node [shape=box, fontname=Helvetica];"]
        counter = [0]

        def walk(node: 'ParseNode') -> int:
            counter[0] += 1
            me = counter[0]
            label = node.symbol if node.token is None else f"{node.symbol}\\n{node.token.value}"
            lines.append(f'  n{me} [label="{label}"];')
            for c in node.children:
                lines.append(f"  n{me} -> n{walk(c)};")
            return me

        walk(self)
        lines.append("}")
        return "\n".join(lines)


_TABLE, _CONFLICTS = build_table()
assert not _CONFLICTS, "La gramática no es LL(1)"


def terminal_of(tok: Token) -> str:
    if tok.type == 'KEYWORD':
        return tok.value
    if tok.type == 'EOF':
        return END
    return tok.type


def ll1_parse(source: str) -> ParseNode:
    tokens = Lexer(source).tokens
    pos = 0
    root = ParseNode(START)
    stack: List[ParseNode] = [ParseNode(END), root]

    while stack:
        top = stack.pop()
        tok = tokens[pos]
        a = terminal_of(tok)

        if top.symbol in GRAMMAR:                          # no terminal: expandir con la tabla
            rhs = _TABLE.get((top.symbol, a))
            if rhs is None:
                expected = sorted(x for (A, x) in _TABLE if A == top.symbol)
                raise SyntaxErrorException(
                    f"Error Sintáctico LL(1) (Línea {tok.line}, Col {tok.column}): "
                    f"token inesperado '{tok.value}' al expandir <{top.symbol}>; "
                    f"se esperaba uno de {expected}."
                )
            if rhs == [EPS]:
                top.children = [ParseNode(EPS)]
            else:
                top.children = [ParseNode(s) for s in rhs]
                stack.extend(reversed(top.children))
        else:                                              # terminal: emparejar
            if top.symbol != a:
                raise SyntaxErrorException(
                    f"Error Sintáctico LL(1) (Línea {tok.line}, Col {tok.column}): "
                    f"se esperaba '{top.symbol}' pero se encontró '{tok.value}'."
                )
            top.token = tok
            pos += 1
    return root


if __name__ == "__main__":
    tree = ll1_parse("int x = 2 + 3 * 4;")
    print(tree.pretty_print())
