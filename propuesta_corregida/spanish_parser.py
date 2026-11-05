"""
Módulo 4: Intento de CFG para un subconjunto del español (Fase 1) y diagnóstico de sus límites.

Fenómenos cubiertos (requisitos del enunciado):
  * Concordancia determinante-sustantivo-adjetivo (género y número) y sujeto-verbo (número).
  * Subordinadas: relativa de sujeto  (NP -> ... 'que' VP)  y completiva  (VP -> V_decir 'que' S).
  * Modificadores: adjetivos postnominales (0..n), adverbios (antes/después del verbo),
    frases preposicionales (dentro del NP o adjuntas al VP).

Diseño:
  * `SpanishCFGParser` es un descendente recursivo con retroceso que ENUMERA TODAS las
    derivaciones (parse_all). Un LL(1) determinista elegiría una sola y ocultaría la ambigüedad.
  * La concordancia se expresa como unificación de rasgos finitos (género, número). Es
    equivalente a dividir los no terminales por rasgos: `build_cfg()` genera esa CFG explícita,
    que se usa para (a) medir su tamaño y (b) verificar el parser con un chart parser
    independiente (NLTK) en test.py.
"""

import re
from typing import Dict, List, Optional, Tuple

from formal_parser import ASTNode, SyntaxErrorException


class SpanishGrammarError(SyntaxErrorException):
    """Fallo de la CFG. `kind` ∈ {empty, oov, agreement, structure, trailing}."""

    def __init__(self, message: str, kind: str = "structure", position: Optional[int] = None,
                 rule: Optional[str] = None):
        super().__init__(message)
        self.kind = kind
        self.position = position
        self.rule = rule


# ----------------------------------------------------------------------------- léxico
GENDERS = ("m", "f")
NUMBERS = ("sg", "pl")
SUBCATS = ("intr", "trans", "comm")

LEXICON: Dict[str, Tuple[str, Dict[str, str]]] = {}


def _add(cat: str, words, **feats):
    for w in words if isinstance(words, (list, tuple)) else [words]:
        LEXICON[w] = (cat, dict(feats))


for _w, _g, _n in [("el", "m", "sg"), ("la", "f", "sg"), ("los", "m", "pl"), ("las", "f", "pl"),
                   ("un", "m", "sg"), ("una", "f", "sg"), ("unos", "m", "pl"), ("unas", "f", "pl")]:
    _add("DET", _w, gender=_g, number=_n)

for _w, _g, _n in [("gato", "m", "sg"), ("gata", "f", "sg"), ("gatos", "m", "pl"), ("gatas", "f", "pl"),
                   ("perro", "m", "sg"), ("perra", "f", "sg"), ("perros", "m", "pl"), ("perras", "f", "pl"),
                   ("niño", "m", "sg"), ("niña", "f", "sg"), ("niños", "m", "pl"), ("niñas", "f", "pl"),
                   ("ratón", "m", "sg"), ("ratones", "m", "pl"),
                   ("telescopio", "m", "sg"), ("telescopios", "m", "pl"),
                   ("parque", "m", "sg"), ("parques", "m", "pl")]:
    _add("N", _w, gender=_g, number=_n)

for _stem in ("negr", "pequeñ", "rápid"):
    for _suf, _g, _n in [("o", "m", "sg"), ("a", "f", "sg"), ("os", "m", "pl"), ("as", "f", "pl")]:
        _add("ADJ", _stem + _suf, gender=_g, number=_n)
_add("ADJ", "veloz", number="sg")        # género subespecificado (invariable): se unifica con m o f
_add("ADJ", "veloces", number="pl")

_add("ADV", ["rápidamente", "lentamente", "ayer", "siempre"])
_add("PREP", ["con", "en", "de", "desde", "sobre", "a"])

for _sg, _pl, _tense, _sub in [
    ("persigue", "persiguen", "pres", "trans"), ("persiguió", "persiguieron", "pret", "trans"),
    ("ve", "ven", "pres", "trans"), ("vio", "vieron", "pret", "trans"),
    ("duerme", "duermen", "pres", "intr"), ("durmió", "durmieron", "pret", "intr"),
    ("corre", "corren", "pres", "intr"), ("corrió", "corrieron", "pret", "intr"),
    ("dice", "dicen", "pres", "comm"), ("dijo", "dijeron", "pret", "comm"),
]:
    _add("V", _sg, number="sg", tense=_tense, subcat=_sub)
    _add("V", _pl, number="pl", tense=_tense, subcat=_sub)

_add("QUE", "que")
_add("CONJ", "y")      # está en el léxico pero NINGUNA regla la usa: aísla el fallo de coordinación


def unify(a: Dict[str, str], b: Dict[str, str], keys=("gender", "number")) -> Optional[Dict[str, str]]:
    """Unificación de rasgos: None si hay conflicto; un rasgo ausente es compatible con todo."""
    out: Dict[str, str] = {}
    for k in keys:
        x, y = a.get(k), b.get(k)
        if x and y and x != y:
            return None
        v = x or y
        if v:
            out[k] = v
    return out


# ----------------------------------------------------------------------------- parser
class _Tok:
    __slots__ = ("word", "cat", "feats")

    def __init__(self, word, cat, feats):
        self.word, self.cat, self.feats = word, cat, feats


_EOF = _Tok("<fin>", "EOF", {})


class SpanishCFGParser:
    """
    Gramática implementada (cada no terminal NP/VP lleva sus rasgos; ver build_cfg()):
        S    -> NP[n] VP[n]
        NP   -> DET N ADJ* | DET N ADJ* PP | DET N ADJ* RC[n]      (DET, N, ADJ concuerdan en g, n)
        RC   -> 'que' VP[n]                                        (relativa de sujeto)
        PP   -> PREP NP
        VP   -> ADV? V C ADV? PP{0,2}                              (V concuerda en n con el sujeto)
        C    -> ε            si V es intransitivo
              | NP           si V es transitivo
              | 'que' S      si V es de comunicación (completiva)
    """

    def __init__(self, sentence: str):
        self.raw_sentence = sentence
        self.words = re.findall(r"[a-záéíóúñü]+|[^\sa-záéíóúñü]", sentence.lower().strip().rstrip(".!?"))
        self.tokens: List[_Tok] = []
        self._fails: Dict[int, List[Tuple[str, str, str]]] = {}
        self._tokenize()

    # -- léxico ---------------------------------------------------------------
    def _tokenize(self):
        if not self.words:
            raise SpanishGrammarError("Oración vacía.", kind="empty")
        for idx, w in enumerate(self.words):
            if w not in LEXICON:
                raise SpanishGrammarError(
                    f"Fallo de cobertura léxica (OOV) en la posición {idx + 1}: '{w}' no está en el léxico finito. "
                    f"Una CFG enumera su vocabulario; el lenguaje natural tiene vocabulario abierto.",
                    kind="oov", position=idx, rule="Léxico (DET|N|ADJ|ADV|PREP|V -> palabra)")
            cat, feats = LEXICON[w]
            self.tokens.append(_Tok(w, cat, feats))

    def _tok(self, i: int) -> _Tok:
        return self.tokens[i] if i < len(self.tokens) else _EOF

    def _fail(self, i: int, kind: str, rule: str, msg: str):
        self._fails.setdefault(i, []).append((kind, rule, msg))

    @staticmethod
    def _leaf(tok: _Tok) -> ASTNode:
        feats = "_".join(v for k, v in tok.feats.items() if k in ("gender", "number") and v)
        return ASTNode(f"{tok.cat} ({feats})" if feats else tok.cat, value=tok.word)

    # -- no terminales (cada uno devuelve TODAS las alternativas) ------------------
    def _s(self, i: int):
        out = []
        for np_node, j, f in self._np(i):
            for vp_node, k in self._vp(j, f["number"]):
                out.append((ASTNode("S", children=[np_node, vp_node]), k))
        return out

    def _np(self, i: int):
        d, n = self._tok(i), self._tok(i + 1)
        if d.cat != "DET":
            self._fail(i, "structure", "NP -> DET N ADJ*",
                       f"se esperaba un determinante (DET) pero aparece '{d.word}' ({d.cat}). "
                       f"La regla S -> NP VP exige NP explícito: no admite sujeto tácito (pro-drop) ni inversión V-S.")
            return []
        if n.cat != "N":
            self._fail(i + 1, "structure", "NP -> DET N ADJ*",
                       f"se esperaba un sustantivo (N) después de '{d.word}' pero aparece '{n.word}' ({n.cat}). "
                       f"La posición del adjetivo está fijada (solo postnominal).")
            return []
        f = unify(d.feats, n.feats)
        if f is None:
            self._fail(i + 1, "agreement", "NP -> DET[g,n] N[g,n] ADJ*",
                       f"discordancia determinante-sustantivo: '{d.word}' ({d.feats['gender']}_{d.feats['number']}) "
                       f"vs '{n.word}' ({n.feats['gender']}_{n.feats['number']}).")
            return []
        base = [self._leaf(d), self._leaf(n)]
        states = [(base, i + 2)]
        j, cur = i + 2, base
        while True:
            a = self._tok(j)
            if a.cat != "ADJ":
                break
            u = unify(f, a.feats)
            if u is None:
                self._fail(j, "agreement", "NP -> DET N ADJ[g,n]*",
                           f"discordancia sustantivo-adjetivo: NP ({f['gender']}_{f['number']}) vs "
                           f"'{a.word}' ({a.feats.get('gender', '*')}_{a.feats['number']}).")
                break
            cur = cur + [self._leaf(a)]
            j += 1
            states.append((cur, j))
        out = []
        for children, k in states:
            out.append((ASTNode(f"NP ({f['gender']}_{f['number']})", children=list(children)), k, f))
            for pp_node, k2 in self._pp(k):
                out.append((ASTNode(f"NP ({f['gender']}_{f['number']})", children=list(children) + [pp_node]), k2, f))
            for rc_node, k2 in self._rc(k, f["number"]):
                out.append((ASTNode(f"NP ({f['gender']}_{f['number']})", children=list(children) + [rc_node]), k2, f))
        return out

    def _pp(self, i: int):
        p = self._tok(i)
        if p.cat != "PREP":
            return []
        return [(ASTNode("PP", value=p.word, children=[np_node]), j) for np_node, j, _ in self._np(i + 1)]

    def _rc(self, i: int, number: str):
        if self._tok(i).cat != "QUE":
            return []
        return [(ASTNode("RC (relativa)", value="que", children=[vp]), j) for vp, j in self._vp(i + 1, number)]

    def _vp(self, i: int, number: str):
        out = []
        pre = [(None, i)]
        if self._tok(i).cat == "ADV":
            pre.append((self._leaf(self._tok(i)), i + 1))
        for adv_pre, p in pre:
            v = self._tok(p)
            if v.cat != "V":
                self._fail(p, "structure", "VP -> ADV? V C ADV? PP*",
                           f"se esperaba un verbo (V) pero aparece '{v.word}' ({v.cat}).")
                continue
            if v.feats["number"] != number:
                self._fail(p, "agreement", "S -> NP[n] VP[n]",
                           f"discordancia sujeto-verbo: el sujeto es '{number}' pero '{v.word}' es '{v.feats['number']}'.")
                continue
            for comp_nodes, j in self._complement(v, p + 1):
                post = [(None, j)]
                if self._tok(j).cat == "ADV":
                    post.append((self._leaf(self._tok(j)), j + 1))
                for adv_post, q in post:
                    states = [([], q)]
                    frontier = [([], q)]
                    for _ in range(2):                      # hasta 2 PP adjuntos al VP
                        nxt = []
                        for nodes, k in frontier:
                            for pp_node, k2 in self._pp(k):
                                nxt.append((nodes + [pp_node], k2))
                        states += nxt
                        frontier = nxt
                    for pps, k in states:
                        kids = ([adv_pre] if adv_pre else []) + [self._leaf(v)] + comp_nodes \
                               + ([adv_post] if adv_post else []) + pps
                        out.append((ASTNode(f"VP ({number})", children=kids), k))
        return out

    def _complement(self, v: _Tok, i: int):
        sub = v.feats["subcat"]
        if sub == "intr":
            return [([], i)]
        if sub == "trans":
            res = [([np_node], j) for np_node, j, _ in self._np(i)]
            if not res:
                self._fail(i, "structure", "C -> NP (V transitivo)",
                           f"el verbo transitivo '{v.word}' exige un objeto directo (NP).")
            return res
        if self._tok(i).cat != "QUE":
            self._fail(i, "structure", "C -> 'que' S (V de comunicación)",
                       f"'{v.word}' exige una completiva introducida por 'que'.")
            return []
        return [([ASTNode("CP (completiva)", value="que", children=[s])], j) for s, j in self._s(i + 1)]

    # -- API pública ----------------------------------------------------------------------
    def parse_all(self) -> List[ASTNode]:
        n = len(self.tokens)
        trees = []
        for node, k in self._s(0):
            if k == n:
                trees.append(node)
            else:
                self._fail(k, "trailing", "S", f"quedaron palabras sin analizar desde '{self._tok(k).word}'.")
        return trees

    def count_parses(self) -> int:
        return len(self.parse_all())

    def parse(self) -> ASTNode:
        """Primera derivación (lo que haría un parser determinista). Lanza SpanishGrammarError si no hay."""
        trees = self.parse_all()
        if trees:
            return trees[0]
        pos = max(self._fails) if self._fails else 0
        kinds = self._fails.get(pos, [("structure", "S", "no se pudo derivar la oración.")])
        order = {"agreement": 0, "trailing": 1, "structure": 2}
        kind, rule, msg = sorted(kinds, key=lambda t: order.get(t[0], 3))[0]
        label = {"agreement": "Fallo de concordancia", "structure": "Fallo estructural",
                 "trailing": "Fallo por cobertura estructural"}[kind]
        raise SpanishGrammarError(f"{label} (palabra {pos + 1}, '{self._tok(pos).word}'; regla {rule}): {msg}",
                                  kind=kind, position=pos, rule=rule)


# ----------------------------------------------------------------------------- CFG explícita
Rule = Tuple[str, Tuple[str, ...]]


def build_cfg(split_agreement: bool = True) -> List[Rule]:
    """
    Genera la CFG explícita equivalente al parser.
    split_agreement=True  : concordancia codificada dividiendo no terminales (NP_m_sg, VP_pl, ...).
    split_agreement=False : misma gramática SIN concordancia (baseline; sobre-genera).
    Los terminales van entre comillas simples (formato NLTK). No hay producciones ε.
    """
    R: List[Rule] = []

    def add(lhs, *rhs):
        R.append((lhs, tuple(rhs)))

    nums = NUMBERS if split_agreement else ("",)
    gens = GENDERS if split_agreement else ("",)

    def sfx(*parts):
        return "".join("_" + p for p in parts if p)

    # S, NP, RC
    for n in nums:
        add("S", f"NP{sfx(n)}", f"VP{sfx(n)}")
        for g in gens:
            if split_agreement:
                add(f"NP{sfx(n)}", f"NP{sfx(g, n)}")
            gn = sfx(g, n)
            core = (f"DET{gn}", f"N{gn}")
            adjs = (f"ADJS{gn}",)
            rc = (f"RC{sfx(n)}",)
            for tail in [(), adjs, ("PP",), adjs + ("PP",), rc, adjs + rc]:
                add(f"NP{gn}", *(core + tail))
            add(f"ADJS{gn}", f"ADJ{gn}")
            add(f"ADJS{gn}", f"ADJ{gn}", f"ADJS{gn}")
        add(f"RC{sfx(n)}", "'que'", f"VP{sfx(n)}")
    if split_agreement:
        for n in NUMBERS:
            add("NP_any", f"NP_{n}")
        obj = "NP_any"
    else:
        obj = "NP"
    add("PP", "PREP", obj)
    for n in nums:
        vp, vadv, vc = f"VP{sfx(n)}", f"VADV{sfx(n)}", f"VC{sfx(n)}"
        add(vp, vadv)
        add(vp, vadv, "PP")
        add(vp, vadv, "PP", "PP")
        add(vadv, vc)
        add(vadv, "ADV", vc)
        add(vadv, vc, "ADV")
        add(vadv, "ADV", vc, "ADV")
        add(vc, f"V{sfx(n)}_intr")
        add(vc, f"V{sfx(n)}_trans", obj)
        add(vc, f"V{sfx(n)}_comm", "'que'", "S")
    # léxico
    for w, (cat, f) in sorted(LEXICON.items()):
        if cat == "DET" or cat == "N":
            add(f"{cat}{sfx(f['gender'], f['number']) if split_agreement else ''}", f"'{w}'")
        elif cat == "ADJ":
            for g in (GENDERS if "gender" not in f else (f["gender"],)):
                add(f"ADJ{sfx(g, f['number']) if split_agreement else ''}", f"'{w}'")
        elif cat == "V":
            add(f"V{sfx(f['number']) if split_agreement else ''}_{f['subcat']}", f"'{w}'")
        elif cat in ("ADV", "PREP"):
            add(cat, f"'{w}'")
    # sin duplicados, preservando orden
    seen, uniq = set(), []
    for r in R:
        if r not in seen:
            seen.add(r)
            uniq.append(r)
    return uniq


def cfg_stats(rules: List[Rule]) -> Dict[str, int]:
    lexical = [r for r in rules if len(r[1]) == 1 and r[1][0].startswith("'")]
    return {
        "no_terminales": len({lhs for lhs, _ in rules}),
        "producciones_estructurales": len(rules) - len(lexical),
        "producciones_lexicas": len(lexical),
        "producciones_total": len(rules),
    }


def to_nltk_text(rules: List[Rule]) -> str:
    return "\n".join(f"{lhs} -> {' '.join(rhs)}" for lhs, rhs in rules)


def grammar_growth(domains: Dict[str, int]) -> int:
    """Nº de variantes por categoría si cada rasgo finito se codifica en el no terminal: ∏|dominio|."""
    total = 1
    for size in domains.values():
        total *= size
    return total


# ----------------------------------------------------------------------------- corpus de Fase 1
# Cada entrada: id, texto, esperado ('accept'|'reject'), parses (si accept) o kind (si reject),
# fenómeno y qué clase de límite ilustra. Una entrada 'reject' con válida_en_español=True es un
# falso negativo de la CFG; con False es un rechazo correcto.
CORPUS = [
    # --- A. Aceptadas (la CFG acierta)
    dict(id="A1", text="El gato negro persigue un ratón", expect="accept", parses=1,
         phenomenon="SVO + concordancia N-ADJ y S-V", valid_es=True),
    dict(id="A2", text="Las niñas pequeñas ven unos perros negros", expect="accept", parses=1,
         phenomenon="concordancia fem/pl en NP sujeto y objeto", valid_es=True),
    dict(id="A3", text="El gato siempre corre rápidamente en el parque", expect="accept", parses=1,
         phenomenon="adverbios + PP", valid_es=True),
    dict(id="A4", text="El gato persiguió un ratón ayer", expect="accept", parses=1,
         phenomenon="segundo tiempo verbal (pretérito) + adverbio", valid_es=True),
    dict(id="A5", text="La niña que corre duerme", expect="accept", parses=1,
         phenomenon="subordinada relativa (concuerda con el antecedente)", valid_es=True),
    dict(id="A6", text="El niño dice que el gato duerme", expect="accept", parses=1,
         phenomenon="subordinada completiva (recursión S dentro de VP)", valid_es=True),
    # --- B. Rechazos correctos (agramaticales)
    dict(id="B1", text="La gatos negros persigue un ratón", expect="reject", kind="agreement",
         phenomenon="discordancia DET-N (género y número)", valid_es=False),
    dict(id="B2", text="El gato negro persiguen un ratón", expect="reject", kind="agreement",
         phenomenon="discordancia sujeto-verbo", valid_es=False),
    dict(id="B3", text="Los gatos negra corren", expect="reject", kind="agreement",
         phenomenon="discordancia N-ADJ", valid_es=False),
    # --- C. Falsos negativos: español válido que esta CFG rechaza
    dict(id="C1", text="Persigue un ratón en el parque", expect="reject", kind="structure",
         phenomenon="sujeto tácito (pro-drop)", valid_es=True),
    dict(id="C2", text="El veloz perro persigue un ratón", expect="reject", kind="structure",
         phenomenon="adjetivo antepuesto (orden libre)", valid_es=True),
    dict(id="C3", text="Corre el gato", expect="reject", kind="structure",
         phenomenon="inversión verbo-sujeto", valid_es=True),
    dict(id="C4", text="El gato y el perro duermen", expect="reject", kind="structure",
         phenomenon="coordinación (concordancia por resolución sg+sg=pl)", valid_es=True),
    dict(id="C5", text="El gato observa las aves", expect="reject", kind="oov",
         phenomenon="vocabulario abierto (OOV)", valid_es=True),
    # --- D. Ambigüedad estructural (la CFG acepta, pero hay >1 derivación)
    dict(id="D1", text="El gato ve el perro con el telescopio", expect="accept", parses=2,
         phenomenon="ambigüedad de adjunción de PP (NP vs VP)", valid_es=True),
    dict(id="D2", text="La niña que ve el perro con el telescopio corre en el parque", expect="accept", parses=2,
         phenomenon="relativa + PP ambiguo (oración 5 original)", valid_es=True),
    dict(id="D3", text="El niño ve el gato con el perro en el parque", expect="accept", parses=4,
         phenomenon="dos PP encadenados: 4 árboles (cada PP extra multiplica las adjunciones posibles)", valid_es=True),
]


if __name__ == "__main__":
    print("=== Intento de CFG para español: resultados sobre el corpus de Fase 1 ===\n")
    for e in CORPUS:
        print(f"[{e['id']}] {e['text']!r}  ({e['phenomenon']})")
        try:
            p = SpanishCFGParser(e["text"])
            trees = p.parse_all()
            if trees:
                print(f"   ACEPTA  -> {len(trees)} derivación(es). Primera:")
                print(trees[0].pretty_print(level=3))
            else:
                p.parse()
        except SpanishGrammarError as exc:
            print(f"   RECHAZA [{exc.kind}] {exc}\n")
