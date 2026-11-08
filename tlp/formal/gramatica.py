"""gramatica.py - Gramática BNF de Mini-C y verificación formal de que es LL(1).

Es la fuente de verdad: `verificar_ll1()` calcula FIRST/FOLLOW sobre ESTE diccionario.
"""
from __future__ import annotations

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
