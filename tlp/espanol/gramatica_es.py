"""tlp/espanol/gramatica_es.py - Gramática libre de contexto y parser para un subconjunto controlado del español.

Fases 1 y 2.  Contiene:
  * LÉXICO (con rasgos de género, número, tiempo, subcategorización y animacidad)
  * REGLAS_BNF: la gramática en texto (es EXACTAMENTE lo que se le entrega al LLM en la Fase 2)
  * ParserEspanol: descendente recursivo con retroceso, implementado con generadores para
    devolver TODAS las derivaciones (así se puede contar la ambigüedad estructural)
  * extraer_svo(): sujeto-verbo-objeto del árbol (para comparar con spaCy)
  * cfg_nltk(): la MISMA gramática expandida a una CFG pura (rasgos finitos => se multiplican los
    no terminales).  Sirve para demostrar que la concordancia con rasgos finitos sigue siendo libre
    de contexto y para validar el parser contra el ChartParser de NLTK.

Alcance (deliberado, ver informe): tercera persona; tiempos presente y pretérito perfecto simple;
oraciones con sujeto explícito; SVO, intransitivas y con cláusula completiva ("dice que ...");
adjetivos pospuestos; adverbios; sintagmas preposicionales; relativas de sujeto ("el gato que duerme").
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from ..arbol import Node

# ---------------------------------------------------------------------------
# 1. LÉXICO
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Entrada:
    cat: str            # DET N PN ADJ V ADV P QUE
    lema: str
    gen: str = ""       # m f mf
    num: str = ""       # sg pl
    tiempo: str = ""    # pres pret
    sub: str = ""       # tr intr comp
    anim: str = ""      # h (humano) a (animal) n (no animado)


LEXICO: dict[str, list[Entrada]] = {}


def _add(forma: str, e: Entrada):
    LEXICO.setdefault(forma, []).append(e)


for _f, _g, _n in [("el", "m", "sg"), ("la", "f", "sg"), ("los", "m", "pl"), ("las", "f", "pl"),
                   ("un", "m", "sg"), ("una", "f", "sg"), ("unos", "m", "pl"), ("unas", "f", "pl")]:
    _add(_f, Entrada("DET", "el" if _f in ("el", "la", "los", "las") else "un", _g, _n))

# (singular, plural, género, animacidad)
_NOMBRES = [
    ("gato", "gatos", "m", "a"), ("gata", "gatas", "f", "a"), ("perro", "perros", "m", "a"),
    ("perra", "perras", "f", "a"), ("ratón", "ratones", "m", "a"), ("pájaro", "pájaros", "m", "a"),
    ("niño", "niños", "m", "h"), ("niña", "niñas", "f", "h"), ("profesor", "profesores", "m", "h"),
    ("profesora", "profesoras", "f", "h"), ("estudiante", "estudiantes", "mf", "h"),
    ("hombre", "hombres", "m", "h"), ("mujer", "mujeres", "f", "h"),
    ("libro", "libros", "m", "n"), ("carta", "cartas", "f", "n"), ("casa", "casas", "f", "n"),
    ("mesa", "mesas", "f", "n"), ("pan", "panes", "m", "n"), ("manzana", "manzanas", "f", "n"),
    ("puerta", "puertas", "f", "n"), ("ventana", "ventanas", "f", "n"), ("sombrero", "sombreros", "m", "n"),
    ("telescopio", "telescopios", "m", "n"), ("jardín", "jardines", "m", "n"),
    ("parque", "parques", "m", "n"), ("escuela", "escuelas", "f", "n"), ("ciudad", "ciudades", "f", "n"),
    ("cocina", "cocinas", "f", "n"),
]
for _s, _p, _g, _a in _NOMBRES:
    _add(_s, Entrada("N", _s, _g, "sg", anim=_a))
    _add(_p, Entrada("N", _s, _g, "pl", anim=_a))

for _pn, _g in [("juan", "m"), ("maría", "f"), ("pedro", "m"), ("ana", "f")]:
    _add(_pn, Entrada("PN", _pn, _g, "sg", anim="h"))

# adjetivos en -o (4 formas) y de una terminación (2 formas)
for _a in ["negro", "blanco", "pequeño", "nuevo", "viejo", "rápido", "cansado", "simpático"]:
    b = _a[:-1]
    for suf, g, n in [("o", "m", "sg"), ("a", "f", "sg"), ("os", "m", "pl"), ("as", "f", "pl")]:
        _add(b + suf, Entrada("ADJ", _a, g, n))
for _s, _p in [("grande", "grandes"), ("inteligente", "inteligentes"), ("feliz", "felices"), ("joven", "jóvenes")]:
    _add(_s, Entrada("ADJ", _s, "mf", "sg"))
    _add(_p, Entrada("ADJ", _s, "mf", "pl"))

# verbos: lema -> (pres3sg, pres3pl, pret3sg, pret3pl, subcategoría)
_VERBOS = {
    "perseguir": ("persigue", "persiguen", "persiguió", "persiguieron", "tr"),
    "ver": ("ve", "ven", "vio", "vieron", "tr"),
    "comer": ("come", "comen", "comió", "comieron", "tr"),
    "leer": ("lee", "leen", "leyó", "leyeron", "tr"),
    "escribir": ("escribe", "escriben", "escribió", "escribieron", "tr"),
    "comprar": ("compra", "compran", "compró", "compraron", "tr"),
    "mirar": ("mira", "miran", "miró", "miraron", "tr"),
    "abrir": ("abre", "abren", "abrió", "abrieron", "tr"),
    "correr": ("corre", "corren", "corrió", "corrieron", "intr"),
    "dormir": ("duerme", "duermen", "durmió", "durmieron", "intr"),
    "llegar": ("llega", "llegan", "llegó", "llegaron", "intr"),
    "cantar": ("canta", "cantan", "cantó", "cantaron", "intr"),
    "trabajar": ("trabaja", "trabajan", "trabajó", "trabajaron", "intr"),
    "decir": ("dice", "dicen", "dijo", "dijeron", "comp"),
    "pensar": ("piensa", "piensan", "pensó", "pensaron", "comp"),
}
for _l, (a, b, c, d, sub) in _VERBOS.items():
    _add(a, Entrada("V", _l, num="sg", tiempo="pres", sub=sub))
    _add(b, Entrada("V", _l, num="pl", tiempo="pres", sub=sub))
    _add(c, Entrada("V", _l, num="sg", tiempo="pret", sub=sub))
    _add(d, Entrada("V", _l, num="pl", tiempo="pret", sub=sub))

for _a in ["rápidamente", "lentamente", "siempre", "tranquilamente", "hoy"]:
    _add(_a, Entrada("ADV", _a))
for _p in ["con", "en", "de", "para", "sobre", "por", "a"]:
    _add(_p, Entrada("P", _p))
_add("que", Entrada("QUE", "que"))

LEMA_DE_FORMA = {f: es[0].lema for f, es in LEXICO.items()}

# ---------------------------------------------------------------------------
# 2. GRAMÁTICA EN TEXTO (se le entrega literalmente al LLM en la Fase 2)
# ---------------------------------------------------------------------------
REGLAS_BNF = """\
O    -> SN SV                       [el número de SN y de V deben coincidir]
SN   -> PN
SN   -> Det N Adj* SP* Rel?         [Det y N concuerdan en género y número; cada Adj concuerda con N]
SP   -> P SN
Rel  -> Que SV                      [relativa de sujeto; el verbo concuerda en número con el SN antecedente]
SV   -> V Adv? SP*                  [V intransitivo (intr)]
SV   -> V Adv? Obj Adv? SP*         [V transitivo (tr); los dos Adv son opcionales]
SV   -> V Que O                     [V de tipo "comp" (decir, pensar)]
Obj  -> SN                          [solo si el núcleo de SN es no animado (n) o animal (a)]
Obj  -> A SN                        [A = la palabra "a"; solo si el núcleo es humano (h), animal (a) o PN; un objeto humano EXIGE esta forma]
Reglas de léxico: Det, N, PN, Adj, V, Adv, P, Que se reescriben en las palabras del léxico.
Restricciones: solo 3.ª persona; tiempos presente y pretérito; sujeto SIEMPRE explícito;
"al" = "a el" y "del" = "de el" (se separan antes de analizar); no hay coordinación, clíticos, negación,
interrogativas, pasivas, ni verbos copulativos."""


def lexico_para_prompt() -> str:
    """Léxico compacto y legible, para incluirlo en el prompt del LLM."""
    por_cat: dict[str, list[str]] = {}
    for forma, es in sorted(LEXICO.items()):
        for e in es:
            r = e.cat
            if e.cat in ("DET", "N", "ADJ", "PN"):
                r += f"[{e.gen},{e.num}" + (f",{e.anim}" if e.anim else "") + "]"
            elif e.cat == "V":
                r += f"[{e.tiempo},{e.num},{e.sub}]"
            por_cat.setdefault(e.cat, []).append(f"{forma}:{r.split('[')[1].rstrip(']') if '[' in r else ''}")
    return "\n".join(f"{c}: " + " ".join(x.rstrip(":") for x in v) for c, v in por_cat.items())


# ---------------------------------------------------------------------------
# 3. TOKENIZADOR
# ---------------------------------------------------------------------------
def tokenizar(oracion: str) -> list[str]:
    s = unicodedata.normalize("NFC", oracion.lower())
    s = re.sub(r"[¿?¡!.,;:]", " ", s)
    toks = []
    for w in s.split():
        if w == "al":
            toks += ["a", "el"]
        elif w == "del":
            toks += ["de", "el"]
        else:
            toks.append(w)
    return toks


def _conc(g1: str, g2: str) -> bool:
    return g1 == g2 or "mf" in (g1, g2)


class ErrorGramatical(Exception):
    pass


# ---------------------------------------------------------------------------
# 4. PARSER DESCENDENTE RECURSIVO CON RETROCESO (generadores)
# ---------------------------------------------------------------------------
class ParserEspanol:
    def __init__(self, relativas: bool = True, completivas: bool = True):
        self.relativas = relativas
        self.completivas = completivas

    # ---- infraestructura -------------------------------------------------
    def _entradas(self, pos: int, cat: str) -> list[Entrada]:
        if pos >= len(self.t):
            return []
        return [e for e in LEXICO.get(self.t[pos], []) if e.cat == cat]

    def _fallo(self, pos: int, regla: str, msg: str):
        if pos >= self._fpos:
            if pos > self._fpos:
                self._fmsgs = []
            self._fpos = pos
            self._fmsgs.append((regla, msg))

    def _palabra(self, pos: int) -> str:
        return self.t[pos] if pos < len(self.t) else "<fin de oración>"

    # ---- reglas ------------------------------------------------------------
    def _O(self, pos):
        for sn, p, g, n in self._SN(pos):
            for sv, p2 in self._SV(p, n):
                yield Node("O", [sn, sv]), p2

    def _SN(self, pos):
        """Yield (nodo, pos_siguiente, género, número)."""
        if not self._entradas(pos, "PN") and not self._entradas(pos, "DET"):
            self._fallo(pos, "SN → Det N | PN", f"se esperaba un determinante o nombre propio y llegó '{self._palabra(pos)}'")
        for e in self._entradas(pos, "PN"):
            yield Node("SN", [Node(f"PN[{e.gen},sg]", [Node(self.t[pos])])]), pos + 1, e.gen, "sg"
        for d in self._entradas(pos, "DET"):
            ns = self._entradas(pos + 1, "N")
            if not ns:
                self._fallo(pos + 1, "SN → Det N", f"se esperaba un sustantivo y llegó '{self._palabra(pos + 1)}'")
                continue
            for n in ns:
                if d.num != n.num or not _conc(d.gen, n.gen):
                    self._fallo(pos + 1, "concordancia Det–N",
                                f"'{self.t[pos]}' ({d.gen},{d.num}) no concuerda con '{self.t[pos + 1]}' ({n.gen},{n.num})")
                    continue
                gen = d.gen if n.gen == "mf" else n.gen
                base = [Node(f"Det[{d.gen},{d.num}]", [Node(self.t[pos])]),
                        Node(f"N[{n.gen},{n.num}]", [Node(self.t[pos + 1])])]
                for adjs, p in self._ADJS(pos + 2, gen, n.num):
                    for sps, p2 in self._SPS(p):
                        yield from self._cola_SN(base + adjs + sps, p2, gen, n.num, n.anim)

    def _cola_SN(self, hijos, pos, gen, num, anim):
        yield Node("SN", hijos), pos, gen, num
        if self.relativas:
            for q in self._entradas(pos, "QUE"):
                for sv, p in self._SV(pos + 1, num):
                    yield (Node("SN", hijos + [Node("Rel", [Node("Que", [Node("que")]), sv])]),
                           p, gen, num)

    def _ADJS(self, pos, gen, num):
        yield [], pos
        for a in self._entradas(pos, "ADJ"):
            if a.num != num or not _conc(a.gen, gen):
                self._fallo(pos, "concordancia N–Adj",
                            f"'{self.t[pos]}' ({a.gen},{a.num}) no concuerda con el sustantivo ({gen},{num})")
                continue
            nodo = Node(f"Adj[{a.gen},{a.num}]", [Node(self.t[pos])])
            for resto, p in self._ADJS(pos + 1, gen, num):
                yield [nodo] + resto, p

    def _SPS(self, pos):
        yield [], pos
        for sp, p in self._SP(pos):
            for resto, p2 in self._SPS(p):
                yield [sp] + resto, p2

    def _SP(self, pos):
        for pr in self._entradas(pos, "P"):
            for sn, p, g, n in self._SN(pos + 1):
                yield Node("SP", [Node("P", [Node(self.t[pos])]), sn]), p

    def _ADV(self, pos):
        """Yield ([nodos], pos): 0 o 1 adverbio."""
        yield [], pos
        for a in self._entradas(pos, "ADV"):
            yield [Node("Adv", [Node(self.t[pos])])], pos + 1

    def _SV(self, pos, num):
        if not self._entradas(pos, "V"):
            self._fallo(pos, "SV → V …", f"se esperaba un verbo y llegó '{self._palabra(pos)}'")
        for v in self._entradas(pos, "V"):
            if v.num != num:
                self._fallo(pos, "concordancia sujeto–verbo",
                            f"'{self.t[pos]}' es {v.num} pero el sujeto es {num}")
                continue
            nv = Node(f"V[{v.tiempo},{v.num}]", [Node(self.t[pos])])
            if v.sub == "intr":
                for adv, p in self._ADV(pos + 1):
                    for sps, p2 in self._SPS(p):
                        yield Node("SV", [nv] + adv + sps), p2
            elif v.sub == "tr":
                for adv1, p in self._ADV(pos + 1):
                    for obj, p2 in self._OBJ(p):
                        for adv2, p3 in self._ADV(p2):
                            for sps, p4 in self._SPS(p3):
                                yield Node("SV", [nv] + adv1 + obj + adv2 + sps), p4
            elif v.sub == "comp":
                if not self.completivas:
                    continue
                for q in self._entradas(pos + 1, "QUE"):
                    for o, p in self._O(pos + 2):
                        yield Node("SV", [nv, Node("Que", [Node("que")]), o]), p
                if not self._entradas(pos + 1, "QUE"):
                    self._fallo(pos + 1, "SV → V Que O", f"'{self.t[pos]}' exige 'que' y llegó '{self._palabra(pos + 1)}'")

    def _OBJ(self, pos):
        # Obj -> A SN   (a personal)
        for a in self._entradas(pos, "P"):
            if self.t[pos] == "a":
                for sn, p, g, n, anim in self._SN_con_anim(pos + 1):
                    if anim in ("h", "a"):
                        yield [Node("A", [Node("a")]), sn], p
        # Obj -> SN
        for sn, p, g, n, anim in self._SN_con_anim(pos):
            if anim in ("n", "a"):
                yield [sn], p
            else:
                self._fallo(pos, "a personal",
                            "un objeto directo humano exige la preposición 'a' (a personal)")

    def _SN_con_anim(self, pos):
        """Como _SN pero añade la animacidad del núcleo (necesaria para la 'a personal')."""
        for sn, p, g, n in self._SN(pos):
            nucleo = next(c for c in sn.children if c.label.startswith(("N[", "PN[")))
            forma = nucleo.children[0].label
            anim = LEXICO[forma][0].anim
            yield sn, p, g, n, anim

    # ---- API ---------------------------------------------------------------
    def parse_todos(self, oracion: str) -> list[Node]:
        self.t = tokenizar(oracion)
        self._fpos, self._fmsgs = -1, []
        vistos, res = set(), []
        for nodo, p in self._O(0):
            if p != len(self.t):
                self._fallo(p, "O", f"sobran palabras a partir de '{self._palabra(p)}'")
            if p == len(self.t):
                b = nodo.bracket()
                if b not in vistos:
                    vistos.add(b)
                    res.append(nodo)
        if not res:
            self._fallo_final = self._diagnostico()
        return res

    def _diagnostico(self) -> str:
        if not self.t:
            return "oración vacía"
        desconocidas = [w for w in self.t if w not in LEXICO]
        if desconocidas:
            return f"palabra(s) fuera del léxico: {', '.join(desconocidas)}"
        if self._fpos >= 0 and self._fmsgs:
            regla, msg = self._fmsgs[-1]
            return f"falla en la posición {self._fpos} ('{self._palabra(self._fpos)}'), regla «{regla}»: {msg}"
        if self._fpos < 0:
            return f"ninguna regla de la gramática puede comenzar con '{self.t[0]}'"
        return "la oración no pertenece al lenguaje de la gramática"

    def parse(self, oracion: str) -> tuple[Node | None, str]:
        """(primer árbol | None, diagnóstico)."""
        arboles = self.parse_todos(oracion)
        if arboles:
            return arboles[0], f"{len(arboles)} derivación(es)"
        return None, self._fallo_final


# ---------------------------------------------------------------------------
# 5. EXTRACCIÓN SVO (para comparar con otros analizadores)
# ---------------------------------------------------------------------------
def _nucleo(sn: Node) -> str:
    for c in sn.children:
        if c.label.startswith(("N[", "PN[")):
            return LEMA_DE_FORMA[c.children[0].label]
    return "?"


def extraer_svo(arbol: Node) -> tuple[str, str, str]:
    """(sujeto, verbo, objeto). objeto = '-' si es intransitivo y '*' si es cláusula completiva."""
    sn, sv = arbol.children
    verbo = next(c for c in sv.children if c.label.startswith("V["))
    lema_v = LEMA_DE_FORMA[verbo.children[0].label]
    if any(c.label == "O" for c in sv.children):
        obj = "*"
    else:
        objs = [c for c in sv.children if c.label == "SN"]
        obj = _nucleo(objs[0]) if objs else "-"
    return _nucleo(sn), lema_v, obj


# ---------------------------------------------------------------------------
# 6. CFG PURA (rasgos expandidos) para NLTK
# ---------------------------------------------------------------------------
def cfg_nltk(relativas: bool = True, completivas: bool = True):
    """Devuelve (nltk.CFG, n_producciones).  Cada combinación de rasgos pasa a ser un no terminal."""
    import nltk
    R: list[str] = []
    GEN, NUM, ANI = ["m", "f"], ["sg", "pl"], ["h", "a", "n"]
    R.append("S -> S_sg | S_pl")
    for n in NUM:
        R.append(f"S_{n} -> SN_{n} SV_{n}")
        alts = [f"SN_{g}_{n}_{a}" for g in GEN for a in ANI]
        R.append(f"SN_{n} -> " + " | ".join(alts))
    R.append("SN_sg -> PN")
    for g in GEN:
        for n in NUM:
            for a in ANI:
                nt = f"SN_{g}_{n}_{a}"
                base = f"B_{g}_{n}_{a}"
                R.append(f"{nt} -> {base}")
                if relativas:
                    R.append(f"{nt} -> {base} REL_{n}")
                core = f"Det_{g}_{n} N_{g}_{n}_{a}"
                R += [f"{base} -> {core}", f"{base} -> {core} ADJS_{g}_{n}",
                      f"{base} -> {core} SPS", f"{base} -> {core} ADJS_{g}_{n} SPS"]
            R += [f"ADJS_{g}_{n} -> Adj_{g}_{n}", f"ADJS_{g}_{n} -> Adj_{g}_{n} ADJS_{g}_{n}"]
    R += ["SPS -> SP", "SPS -> SP SPS", "SP -> P SN_sg", "SP -> P SN_pl"]
    for n in NUM:
        if relativas:
            R.append(f"REL_{n} -> Que SV_{n}")
        sv = []
        for sps in ["", " SPS"]:
            sv += [f"Vi_{n}{sps}", f"Vi_{n} Adv{sps}"]
            for x in ["", " Adv"]:
                for y in ["", " Adv"]:
                    sv.append(f"Vt_{n}{x} OBJ{y}{sps}")
        if completivas:
            sv.append(f"Vc_{n} Que S")
        R.append(f"SV_{n} -> " + " | ".join(sv))
    obj = []
    for g in GEN:
        for n in NUM:
            obj += [f"SN_{g}_{n}_n", f"SN_{g}_{n}_a", f"A SN_{g}_{n}_a", f"A SN_{g}_{n}_h"]
    obj.append("A PN")
    R.append("OBJ -> " + " | ".join(obj))
    # léxico
    lex: dict[str, set[str]] = {}
    for forma, es in LEXICO.items():
        for e in es:
            if e.cat == "DET":
                for g in (GEN if e.gen == "mf" else [e.gen]):
                    lex.setdefault(f"Det_{g}_{e.num}", set()).add(forma)
            elif e.cat == "N":
                for g in (GEN if e.gen == "mf" else [e.gen]):
                    lex.setdefault(f"N_{g}_{e.num}_{e.anim}", set()).add(forma)
            elif e.cat == "ADJ":
                for g in (GEN if e.gen == "mf" else [e.gen]):
                    lex.setdefault(f"Adj_{g}_{e.num}", set()).add(forma)
            elif e.cat == "PN":
                lex.setdefault("PN", set()).add(forma)
            elif e.cat == "V":
                k = {"intr": "Vi", "tr": "Vt", "comp": "Vc"}[e.sub]
                lex.setdefault(f"{k}_{e.num}", set()).add(forma)
            elif e.cat == "ADV":
                lex.setdefault("Adv", set()).add(forma)
            elif e.cat == "P":
                lex.setdefault("P", set()).add(forma)
                if forma == "a":
                    lex.setdefault("A", set()).add(forma)
            elif e.cat == "QUE":
                lex.setdefault("Que", set()).add(forma)
    for nt, formas in lex.items():
        R.append(f"{nt} -> " + " | ".join(f"'{f}'" for f in sorted(formas)))
    g = nltk.CFG.fromstring("\n".join(R))
    return g, len(g.productions())


def acepta_nltk(gramatica, oracion: str) -> tuple[bool, int]:
    """(¿acepta?, número de árboles) con el ChartParser de NLTK."""
    import nltk
    toks = tokenizar(oracion)
    if any(w not in LEXICO for w in toks):
        return False, 0
    n = len(list(nltk.ChartParser(gramatica).parse(toks)))
    return n > 0, n


def contar_reglas_compactas() -> int:
    return sum(1 for l in REGLAS_BNF.splitlines() if "->" in l)


if __name__ == "__main__":
    import sys
    from arbol import dibujar_arbol
    oracion = " ".join(sys.argv[1:]) or "el gato negro persigue al ratón"
    arbol, diag = ParserEspanol().parse(oracion)
    if arbol:
        print(arbol.indentado())
        print(arbol.bracket(), "|", diag, "| SVO =", extraer_svo(arbol))
    else:
        print("RECHAZADA:", diag)
