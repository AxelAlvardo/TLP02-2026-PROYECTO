"""
Módulo 2: Analizador Sintáctico CFG LL(1) para Español.
Diseñado para demostrar las limitaciones estructurales de las Gramáticas Libres de Contexto
(explosión combinatoria de reglas, rigidez posicional, ambigüedad y falta de cobertura).
"""

import re
from typing import List, Dict, Tuple
from formal_parser import ASTNode, SyntaxErrorException


class SpanishGrammarError(SyntaxErrorException):
    """Excepción que documenta fallos inherentes al usar CFG deterministas en lenguaje natural."""
    pass


class SpanishCFGParser:
    """
    Intento de CFG LL(1) con concordancia estricta codificada en los no-terminales:
        S         -> NP_sg VP_sg | NP_pl VP_pl
        NP_sg     -> NP_m_sg | NP_f_sg
        NP_pl     -> NP_m_pl | NP_f_pl
        
        NP_m_sg   -> DET_m_sg N_m_sg (ADJ_m_sg)? (RC)?
        NP_f_sg   -> DET_f_sg N_f_sg (ADJ_f_sg)? (RC)?
        NP_m_pl   -> DET_m_pl N_m_pl (ADJ_m_pl)? (RC)?
        NP_f_pl   -> DET_f_pl N_f_pl (ADJ_f_pl)? (RC)?
        
        RC        -> 'que' VP_any          # Cláusula subordinada relativa (pierde rastro de número en CFG simple)
        VP_sg     -> V_sg (NP_any)? (PP)?
        VP_pl     -> V_pl (NP_any)? (PP)?
        PP        -> PREP NP_any
    """

    LEXICON: Dict[str, Tuple[str, str]] = {
        # Determinantes
        "el": ("DET", "m_sg"), "la": ("DET", "f_sg"),
        "los": ("DET", "m_pl"), "las": ("DET", "f_pl"),
        "un": ("DET", "m_sg"), "una": ("DET", "f_sg"),
        # Sustantivos
        "gato": ("N", "m_sg"), "gata": ("N", "f_sg"),
        "gatos": ("N", "m_pl"), "gatas": ("N", "f_pl"),
        "perro": ("N", "m_sg"), "perros": ("N", "m_pl"),
        "niña": ("N", "f_sg"), "niñas": ("N", "f_pl"),
        "ratón": ("N", "m_sg"), "ratones": ("N", "m_pl"),
        "telescopio": ("N", "m_sg"), "parque": ("N", "m_sg"),
        # Adjetivos
        "negro": ("ADJ", "m_sg"), "negra": ("ADJ", "f_sg"),
        "negros": ("ADJ", "m_pl"), "negras": ("ADJ", "f_pl"),
        "rápido": ("ADJ", "m_sg"), "rápidos": ("ADJ", "m_pl"),
        "pequeña": ("ADJ", "f_sg"), "pequeñas": ("ADJ", "f_pl"),
        # Verbos
        "persigue": ("V", "sg"), "persiguen": ("V", "pl"),
        "ve": ("V", "sg"), "ven": ("V", "pl"),
        "duerme": ("V", "sg"), "duermen": ("V", "pl"),
        "corre": ("V", "sg"), "corren": ("V", "pl"),
        # Preposiciones y pronombres relativos
        "con": ("PREP", "inv"), "en": ("PREP", "inv"), "a": ("PREP", "inv"),
        "que": ("REL", "inv"),
    }

    def __init__(self, sentence: str):
        self.raw_sentence = sentence
        self.words = re.findall(r'[a-záéíóúñü]+', sentence.lower())
        self.tokens: List[Tuple[str, str, str]] = []
        self.pos = 0
        self._tokenize()

    def _tokenize(self):
        if not self.words:
            raise SpanishGrammarError("Oración vacía.")
        for w in self.words:
            if w not in self.LEXICON:
                raise SpanishGrammarError(
                    f"Fallo de Cobertura Léxica (OOV): La palabra '{w}' no existe en el léxico rígido de la CFG."
                )
            pos_tag, feat = self.LEXICON[w]
            self.tokens.append((w, pos_tag, feat))
        self.tokens.append(("EOF", "EOF", "EOF"))

    @property
    def current(self) -> Tuple[str, str, str]:
        return self.tokens[self.pos]

    def consume(self, expected_pos: str, expected_feat: str = None) -> Tuple[str, str, str]:
        word, pos_tag, feat = self.current
        if pos_tag != expected_pos:
            raise SpanishGrammarError(
                f"Fallo Sintáctico / Rigidez de Orden: Se esperaba categoría '{expected_pos}', "
                f"pero se encontró '{word}' ({pos_tag}). Las CFG LL(1) no toleran inversión de sujeto, "
                f"sujeto tácito (pro-drop) ni adverbios en posiciones libres."
            )
        if expected_feat and feat != expected_feat:
            raise SpanishGrammarError(
                f"Fallo de Concordancia Gramatical: Se esperaba rasgo '{expected_feat}' para '{expected_pos}', "
                f"pero '{word}' tiene rasgo '{feat}'."
            )
        self.pos += 1
        return word, pos_tag, feat

    def parse(self) -> ASTNode:
        # S -> NP VP
        np_node, num_feat = self.parse_np()
        vp_node = self.parse_vp(expected_num=num_feat)

        if self.current[1] != "EOF":
            rem_word = self.current[0]
            raise SpanishGrammarError(
                f"Fallo por Complejidad Estructural: Quedaron tokens sin procesar a partir de '{rem_word}'. "
                f"La gramática no logra adjuntar múltiples modificadores o cláusulas anidadas."
            )

        return ASTNode("Oración (S)", children=[np_node, vp_node])

    def parse_np(self) -> Tuple[ASTNode, str]:
        """Analiza un Sintagma Nominal forzando concordancia estricta DET + N + ADJ."""
        word, pos_tag, feat = self.current
        if pos_tag != "DET":
            raise SpanishGrammarError(
                f"Fallo Sintáctico: La regla S -> NP VP exige un Determinante al inicio del NP, "
                f"pero se encontró '{word}' ({pos_tag}). No soporta sujeto tácito ni nombres sin artículo."
            )

        det_word, _, det_feat = self.consume("DET")
        gender, number = det_feat.split("_")

        # Forzar que el sustantivo coincida exactamente en género y número con el determinante
        n_word, _, _ = self.consume("N", expected_feat=det_feat)
        children = [
            ASTNode(f"DET ({det_feat})", value=det_word),
            ASTNode(f"N ({det_feat})", value=n_word)
        ]

        # Modificador adjetival opcional (solo post-nominal en esta CFG rígida)
        if self.current[1] == "ADJ":
            adj_word, _, _ = self.consume("ADJ", expected_feat=det_feat)
            children.append(ASTNode(f"ADJ ({det_feat})", value=adj_word))

        # Cláusula subordinada relativa opcional: RC -> 'que' VP
        if self.current[1] == "REL":
            rel_word, _, _ = self.consume("REL")
            # Límite clásico de CFG: validar concordancia de larga distancia dentro de la cláusula
            sub_vp = self.parse_vp(expected_num=number)
            children.append(ASTNode("CláusulaRelativa (RC)", value=rel_word, children=[sub_vp]))

        return ASTNode(f"NP ({det_feat})", children=children), number

    def parse_vp(self, expected_num: str) -> ASTNode:
        """Analiza un Sintagma Verbal verificando concordancia de número con el núcleo del sujeto."""
        word, pos_tag, feat = self.current
        if pos_tag != "V":
            raise SpanishGrammarError(
                f"Fallo Sintáctico: Se esperaba un Verbo (V_{expected_num}), pero se encontró '{word}' ({pos_tag})."
            )
        if feat != expected_num:
            raise SpanishGrammarError(
                f"Fallo de Concordancia Sujeto-Verbo: El sujeto es '{expected_num}', "
                f"pero el verbo '{word}' es '{feat}'."
            )

        v_word, _, _ = self.consume("V", expected_feat=expected_num)
        children = [ASTNode(f"V ({expected_num})", value=v_word)]

        # Objeto directo opcional (en español suele llevar preposición 'a' si es animado, lo que confunde a LL(1))
        if self.current[1] == "DET":
            obj_np, _ = self.parse_np()
            children.append(obj_np)

        # Sintagma Preposicional opcional (Ambigüedad clásica de adjunción PP: ¿modifica al verbo o al sustantivo?)
        if self.current[1] == "PREP":
            prep_word, _, _ = self.consume("PREP")
            prep_np, _ = self.parse_np()
            children.append(ASTNode("PP (Adjunto al VP por defecto)", value=prep_word, children=[prep_np]))

        return ASTNode(f"VP ({expected_num})", children=children)


# Corpus de prueba compartido con el módulo NLP
TEST_SENTENCES = [
    # 1. Oración canónica simple (Diseñada para pasar en la CFG)
    "El gato negro persigue un ratón",
    # 2. Discordancia de género/número (Falla correctamente por gramática inválida)
    "La gatos negros persigue un ratón",
    # 3. Sujeto tácito / Pro-drop + Preposición 'a' de objeto directo animado (Falla en CFG: válido en español)
    "Persigue a los gatos negros en el parque",
    # 4. Inversión de adjetivo (epíteto pre-nominal) y vocabulario fuera del léxico (Falla en CFG: válido en español)
    "El veloz perro observa las aves desde la colina",
    # 5. Cláusulas subordinadas múltiples y ambigüedad de adjunción preposicional (Falla en CFG)
    "La niña que ve el perro con el telescopio corre en el parque"
]


if __name__ == "__main__":
    print("=== Demostración de Límites de CFG en Español ===\n")
    for idx, sent in enumerate(TEST_SENTENCES, 1):
        print(f"Oración {idx}: '{sent}'")
        try:
            parser = SpanishCFGParser(sent)
            tree = parser.parse()
            print("  [ÉXITO CFG] Árbol generado:")
            print(tree.pretty_print(level=2))
        except SpanishGrammarError as e:
            print(f"  [FALLO CFG] {e}\n")