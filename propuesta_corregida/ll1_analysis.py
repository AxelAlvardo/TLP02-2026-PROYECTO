"""
Módulo 2: Análisis formal LL(1) de la gramática del lenguaje formal.

Calcula anulables, FIRST, FOLLOW y la tabla predictiva M[A, a], y detecta conflictos.
Si no hay conflictos, la gramática ES LL(1) (teorema: G es LL(1) <=> para toda
A -> α | β se cumple FIRST(α) ∩ FIRST(β) = ∅ y, si α =>* ε, FIRST(β) ∩ FOLLOW(A) = ∅).

Los terminales usan los nombres de token del Lexer; las palabras clave se identifican
por su lexema ('int', 'if', ...). '$' es el fin de entrada.
"""

from typing import Dict, List, Set, Tuple

EPS = 'ε'
END = '$'
START = 'Program'

GRAMMAR: Dict[str, List[List[str]]] = {
    'Program':    [['StmtList']],
    'StmtList':   [['Stmt', 'StmtList'], [EPS]],
    'Stmt':       [['DeclStmt'], ['AssignStmt'], ['IfStmt'], ['WhileStmt'], ['Block']],
    'DeclStmt':   [['Type', 'ID', 'DeclInit', 'SEMI']],
    'Type':       [['int'], ['float']],
    'DeclInit':   [['ASSIGN', 'Expr'], [EPS]],
    'AssignStmt': [['ID', 'ASSIGN', 'Expr', 'SEMI']],
    'IfStmt':     [['if', 'LPAREN', 'Cond', 'RPAREN', 'Block', 'ElsePart']],
    'ElsePart':   [['else', 'ElseBody'], [EPS]],
    'ElseBody':   [['Block'], ['IfStmt']],
    'WhileStmt':  [['while', 'LPAREN', 'Cond', 'RPAREN', 'Block']],
    'Block':      [['LBRACE', 'StmtList', 'RBRACE']],
    'Cond':       [['Expr', 'RELOP', 'Expr']],
    'Expr':       [['Term', 'ExprTail']],
    'ExprTail':   [['PLUS', 'Term', 'ExprTail'], ['MINUS', 'Term', 'ExprTail'], [EPS]],
    'Term':       [['Factor', 'TermTail']],
    'TermTail':   [['MUL', 'Factor', 'TermTail'], ['DIV', 'Factor', 'TermTail'], [EPS]],
    'Factor':     [['LPAREN', 'Expr', 'RPAREN'], ['MINUS', 'Factor'], ['ID'], ['NUMBER']],
}


def terminals(grammar=GRAMMAR) -> Set[str]:
    return {s for rhs_list in grammar.values() for rhs in rhs_list for s in rhs
            if s not in grammar and s != EPS}


def nullable_set(grammar=GRAMMAR) -> Set[str]:
    nullable: Set[str] = set()
    changed = True
    while changed:
        changed = False
        for A, prods in grammar.items():
            if A in nullable:
                continue
            for rhs in prods:
                if rhs == [EPS] or all(s in nullable for s in rhs):
                    nullable.add(A)
                    changed = True
                    break
    return nullable


def first_sets(grammar=GRAMMAR) -> Dict[str, Set[str]]:
    nullable = nullable_set(grammar)
    first: Dict[str, Set[str]] = {A: set() for A in grammar}
    changed = True
    while changed:
        changed = False
        for A, prods in grammar.items():
            for rhs in prods:
                for s in rhs:
                    if s == EPS:
                        continue
                    add = first[s] if s in grammar else {s}
                    if not add <= first[A]:
                        first[A] |= add
                        changed = True
                    if s not in nullable:
                        break
    return first


def first_of_sequence(seq: List[str], first, nullable, grammar=GRAMMAR) -> Set[str]:
    out: Set[str] = set()
    for s in seq:
        if s == EPS:
            continue
        out |= first[s] if s in grammar else {s}
        if s not in nullable:
            return out
    out.add(EPS)
    return out


def follow_sets(grammar=GRAMMAR, start=START) -> Dict[str, Set[str]]:
    nullable = nullable_set(grammar)
    first = first_sets(grammar)
    follow: Dict[str, Set[str]] = {A: set() for A in grammar}
    follow[start].add(END)
    changed = True
    while changed:
        changed = False
        for A, prods in grammar.items():
            for rhs in prods:
                for i, B in enumerate(rhs):
                    if B not in grammar:
                        continue
                    beta_first = first_of_sequence(rhs[i + 1:], first, nullable, grammar)
                    add = beta_first - {EPS}
                    if EPS in beta_first:
                        add |= follow[A]
                    if not add <= follow[B]:
                        follow[B] |= add
                        changed = True
    return follow


def build_table(grammar=GRAMMAR, start=START):
    """Devuelve (tabla, conflictos). tabla[(A, a)] = producción (lista de símbolos)."""
    nullable = nullable_set(grammar)
    first = first_sets(grammar)
    follow = follow_sets(grammar, start)
    table: Dict[Tuple[str, str], List[str]] = {}
    conflicts: List[Tuple[str, str, List[str], List[str]]] = []
    for A, prods in grammar.items():
        for rhs in prods:
            f = first_of_sequence(rhs, first, nullable, grammar)
            lookaheads = (f - {EPS}) | (follow[A] if EPS in f else set())
            for a in lookaheads:
                if (A, a) in table and table[(A, a)] != rhs:
                    conflicts.append((A, a, table[(A, a)], rhs))
                else:
                    table[(A, a)] = rhs
    return table, conflicts


def is_ll1(grammar=GRAMMAR) -> bool:
    return not build_table(grammar)[1]


def report() -> str:
    nullable = nullable_set()
    first = first_sets()
    follow = follow_sets()
    table, conflicts = build_table()
    lines = ["=== Análisis LL(1) de la gramática del lenguaje formal ===", ""]
    lines.append(f"Anulables: {sorted(nullable)}")
    lines.append("")
    lines.append(f"{'No terminal':<11} | {'FIRST':<48} | FOLLOW")
    lines.append("-" * 110)
    for A in GRAMMAR:
        f = ", ".join(sorted(first[A]) + ([EPS] if A in nullable else []))
        fo = ", ".join(sorted(follow[A]))
        lines.append(f"{A:<11} | {f:<48} | {fo}")
    lines.append("")
    lines.append(f"Celdas de la tabla M[A,a]: {len(table)}")
    if conflicts:
        lines.append("CONFLICTOS (la gramática NO es LL(1)):")
        for A, a, p1, p2 in conflicts:
            lines.append(f"  M[{A},{a}]: {A}->{' '.join(p1)}  vs  {A}->{' '.join(p2)}")
    else:
        lines.append("Conflictos: 0  =>  la gramática ES LL(1).")
    return "\n".join(lines)


if __name__ == "__main__":
    print(report())
