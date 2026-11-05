"""
Módulo 8: ¿Es LL(1) la CFG del español? Reutiliza el analizador de ll1_analysis.py.

Se escribe la gramática de spanish_parser.py en BNF (sin rasgos: la concordancia no cambia
FIRST/FOLLOW porque los rasgos solo dividen no terminales) y se buscan conflictos.
El conflicto esperado es el de adjunción de PP, análogo al "dangling else" que el lenguaje
formal evita con llaves obligatorias.
"""

from ll1_analysis import EPS, build_table

SPANISH_BNF = {
    'S':    [['NP', 'VP']],
    'NP':   [['DET', 'N', 'Adjs', 'Mod']],
    'Adjs': [['ADJ', 'Adjs'], [EPS]],
    'Mod':  [['PP'], ['RC'], [EPS]],
    'PP':   [['PREP', 'NP']],
    'RC':   [['que', 'VP']],
    'VP':   [['PreAdv', 'V_intr', 'PostAdv', 'PPs'],
             ['PreAdv', 'V_trans', 'NP', 'PostAdv', 'PPs'],
             ['PreAdv', 'V_comm', 'que', 'S', 'PostAdv', 'PPs']],
    'PreAdv':  [['ADV'], [EPS]],
    'PostAdv': [['ADV'], [EPS]],
    'PPs':  [['PP', 'PPs'], [EPS]],
}

# Misma gramática con el prefijo común de VP factorizado por la izquierda (arregla los conflictos
# "de escritura"; los que queden son conflictos reales de adjunción).
SPANISH_BNF_FACTORED = dict(SPANISH_BNF)
SPANISH_BNF_FACTORED['VP'] = [['PreAdv', 'VRest']]
SPANISH_BNF_FACTORED['VRest'] = [['V_intr', 'PostAdv', 'PPs'],
                                 ['V_trans', 'NP', 'PostAdv', 'PPs'],
                                 ['V_comm', 'que', 'S', 'PostAdv', 'PPs']]


def conflicts(grammar=SPANISH_BNF):
    _, c = build_table(grammar, start='S')
    return c


def report() -> str:
    lines = ["=== ¿Es LL(1) la CFG del español? ==="]
    for title, g in (("BNF directa", SPANISH_BNF), ("tras factorizar VP por la izquierda", SPANISH_BNF_FACTORED)):
        c = conflicts(g)
        lines.append(f"{title}: {len(c)} conflicto(s)")
        for A, a, p1, p2 in sorted(c):
            lines.append(f"  M[{A},{a}] : {A} -> {' '.join(p1)}   |   {A} -> {' '.join(p2)}")
    lines.append("")
    lines.append("Causa: 'PREP' pertenece a FIRST(PP) (opción Mod -> PP) y también a FOLLOW(NP) "
                 "(porque VP -> V NP PostAdv PPs), así que con 1 token no se puede decidir si el PP "
                 "modifica al sustantivo o al verbo.")
    return "\n".join(lines)


if __name__ == "__main__":
    print(report())
