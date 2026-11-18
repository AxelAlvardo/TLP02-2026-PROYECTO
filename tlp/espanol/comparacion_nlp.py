"""tlp/espanol/comparacion_nlp.py - Fase 2 (puntos 4 y 5): corre el parser propio, spaCy y HuggingFace.

Procesa el conjunto de prueba (casos/espanol/conjunto_prueba.csv) con cada sistema, decide si ACEPTA o RECHAZA cada
oración y escribe la salida bruta de cada sistema en resultados/fase2/logs/ (un archivo JSONL por sistema, una línea
JSON por oración):
  parser.jsonl                    parser propio: veredicto, regla que falla, árbol (paréntesis), derivaciones, S-V-O
  spacy_<modelo>_crudo.jsonl      spaCy: tokens (lema, categoría, dependencia, cabeza, morfología), S-V-O, veredicto
  spacy_<modelo>_concordancia.jsonl
  huggingface.jsonl               HuggingFace: categoría UPOS de cada palabra, veredicto y regla que falla
Campos comunes de cada línea: sistema, version, id, nivel, oracion, acepta, motivo, svo, palabras, etiquetas, ms.
Las métricas, tablas y gráficas las calcula, leyendo SOLO estos logs:  python -m tlp.espanol.evaluar

Uso:  python -m tlp.espanol.comparacion_nlp
      python -m tlp.espanol.comparacion_nlp --modelos sm md     # modelos es_core_news_* (los no instalados se omiten)
      python -m tlp.espanol.comparacion_nlp --hf-modelo <id>    # otro etiquetador UPOS de HuggingFace

Criterio de aceptación de cada sistema:
  Parser propio           acepta si la gramática da al menos una derivación.
  spaCy (crudo)           acepta siempre: un modelo estadístico nunca rechaza (línea base).
  spaCy + concordancia    rechaza si la raíz no es verbo, si no coincide el número sujeto-verbo o si no coinciden
                          género/número entre determinante o adjetivo y sustantivo, según los rasgos que predice el
                          propio spaCy (heurística propia, no es una función de spaCy).
  HuggingFace + reglas    etiqueta cada palabra (UPOS, sin signos de puntuación) y rechaza si:
                          R1 no hay verbo (VERB/AUX);  R2 alguna palabra es X (categoría desconocida);
                          R3 tras un determinante no viene NOUN/PROPN/ADJ/NUM/DET, o el determinante queda al final;
                          R4 tras una preposición no viene DET/NOUN/PROPN/PRON/NUM/ADJ/VERB, o queda al final.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import unicodedata

from .conjunto import RAIZ, Caso, cargar_conjunto
from .gramatica_es import LEMA_DE_FORMA, ParserEspanol, extraer_svo

DIR_LOGS = os.path.join(RAIZ, "resultados", "fase2", "logs")
HF_MODELO = "wietsedv/xlm-roberta-base-ft-udpos28-es"
TRAS_DET = {"NOUN", "PROPN", "ADJ", "NUM", "DET"}                       # regla R3
TRAS_ADP = {"DET", "NOUN", "PROPN", "PRON", "NUM", "ADJ", "VERB"}       # regla R4


def palabras_de(oracion: str) -> list[str]:
    """Palabras de la oración, sin signos de puntuación y sin separar «al»/«del»."""
    return re.findall(r"\w+", unicodedata.normalize("NFC", oracion))


def registro(sistema: str, version: str, caso: Caso, acepta: bool, motivo: str = "", svo=None, palabras=None,
             etiquetas=None, ms: float = 0.0, **extra) -> dict:
    """Una línea del log: campos comunes a todos los sistemas + los propios de cada uno (`extra`)."""
    return {"sistema": sistema, "version": version, "id": caso.id, "nivel": caso.nivel, "oracion": caso.oracion,
            "acepta": acepta, "motivo": motivo, "svo": list(svo) if svo else None, "palabras": palabras,
            "etiquetas": etiquetas, "ms": round(ms, 4), **extra}


def escribir_log(registros: list[dict], ruta: str) -> str:
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        for r in registros:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return ruta


# ------------------------------------------------------------------ parser propio
def analizar_propio(casos: list[Caso]) -> list[dict]:
    parser, out = ParserEspanol(), []
    version = "parser propio (tlp/espanol/gramatica_es.py)"
    for c in casos:
        t0 = time.perf_counter()
        arbol, diagnostico = parser.parse(c.oracion)
        ms = 1000 * (time.perf_counter() - t0)
        derivaciones = len(parser.parse_todos(c.oracion)) if arbol else 0
        out.append(registro("Parser propio (CFG)", version, c, arbol is not None, "" if arbol else diagnostico,
                            extraer_svo(arbol) if arbol else None, ms=ms, derivaciones=derivaciones,
                            arbol=arbol.bracket() if arbol else None))
    return out


# ------------------------------------------------------------------ spaCy
def _lema(tok) -> str:
    return LEMA_DE_FORMA.get(tok.text.lower()) or tok.lemma_.lower()


def _svo_spacy(doc) -> tuple[str, str, str] | None:
    raiz = next((t for t in doc if t.dep_ == "ROOT"), None)
    if raiz is None:
        return None
    sujeto = next((_lema(c) for c in raiz.children if c.dep_.startswith(("nsubj", "csubj"))), "-")
    objeto = next((_lema(c) for c in raiz.children if c.dep_ in ("obj", "dobj")), "-")
    return sujeto, _lema(raiz), objeto


def _rasgo(tok, k: str) -> str | None:
    v = tok.morph.get(k)
    return v[0] if v else None


def concordancia_spacy(doc) -> str:
    """Criterio «+ concordancia»: '' si no encuentra discordancias; si no, el motivo del rechazo."""
    raiz = next((t for t in doc if t.dep_ == "ROOT"), None)
    if raiz is None or raiz.pos_ not in ("VERB", "AUX"):
        return "la raíz no es un verbo"
    for t in doc:
        if t.dep_.startswith("nsubj") and t.head.pos_ in ("VERB", "AUX"):
            a, b = _rasgo(t, "Number"), _rasgo(t.head, "Number")
            if a and b and a != b:
                return f"número sujeto-verbo: {t.text} ({a}) vs {t.head.text} ({b})"
        if t.dep_ in ("det", "amod") and t.head.pos_ in ("NOUN", "PROPN"):
            for k, rasgo in (("Number", "número"), ("Gender", "género")):
                a, b = _rasgo(t, k), _rasgo(t.head, k)
                if a and b and a != b:
                    return f"{rasgo}: {t.text} ({a}) vs {t.head.text} ({b})"
    return ""


def analizar_spacy(casos: list[Caso], sufijo: str = "sm") -> tuple[list[dict], list[dict]]:
    """Dos sistemas con el mismo análisis de spaCy: crudo (acepta todo) y + concordancia."""
    import spacy
    nlp = spacy.load(f"es_core_news_{sufijo}")
    version = f"spaCy {spacy.__version__}, modelo es_core_news_{sufijo} {nlp.meta.get('version', '?')}"
    crudo, conc = [], []
    for c in casos:
        t0 = time.perf_counter()
        doc = nlp(c.oracion)
        ms = 1000 * (time.perf_counter() - t0)
        svo = _svo_spacy(doc)
        palabras = palabras_de(c.oracion)
        toks = [t for t in doc if not t.is_punct]
        # una etiqueta por palabra solo si spaCy tokenizó igual que palabras_de (si no, no se evalúan categorías)
        etiquetas = [t.pos_ for t in toks] if [t.text.lower() for t in toks] == [p.lower() for p in palabras] else None
        tokens = [{"texto": t.text, "lema": t.lemma_, "upos": t.pos_, "dep": t.dep_, "cabeza": t.head.i,
                   "morfologia": str(t.morph)} for t in doc]
        motivo = concordancia_spacy(doc)
        crudo.append(registro(f"spaCy {sufijo} (crudo)", version, c, True, "", svo, palabras, etiquetas, ms,
                              tokens=tokens))
        conc.append(registro(f"spaCy {sufijo} + concordancia", version, c, motivo == "", motivo, svo, palabras,
                             etiquetas, ms, tokens=tokens))
    return crudo, conc


# ------------------------------------------------------------------ HuggingFace
class EtiquetadorHF:
    """Etiquetador UPOS de HuggingFace: una etiqueta por palabra (la de su primer subtoken)."""

    def __init__(self, modelo: str = HF_MODELO):
        import torch
        from transformers import AutoModelForTokenClassification, AutoTokenizer
        self._torch = torch
        self.tokenizador = AutoTokenizer.from_pretrained(modelo)
        self.modelo = AutoModelForTokenClassification.from_pretrained(modelo).eval()

    def etiquetar(self, palabras: list[str]) -> list[str]:
        enc = self.tokenizador(palabras, is_split_into_words=True, return_tensors="pt")
        with self._torch.no_grad():
            pred = self.modelo(**enc).logits[0].argmax(-1).tolist()
        etiquetas = [""] * len(palabras)
        for i, w in enumerate(enc.word_ids()):
            if w is not None and not etiquetas[w]:
                etiquetas[w] = self.modelo.config.id2label[pred[i]]
        return etiquetas


def reglas_upos(palabras: list[str], etiquetas: list[str]) -> str:
    """Criterio «+ reglas» de HuggingFace: '' si la secuencia de categorías es aceptable; si no, la regla que falla."""
    if not any(e in ("VERB", "AUX") for e in etiquetas):
        return "R1: no hay ningún verbo"
    for p, e in zip(palabras, etiquetas):
        if e == "X":
            return f"R2: '{p}' tiene categoría desconocida (X)"
    for i, (p, e) in enumerate(zip(palabras, etiquetas)):
        sig = etiquetas[i + 1] if i + 1 < len(etiquetas) else "fin de oración"
        if e == "DET" and sig not in TRAS_DET:
            return f"R3: tras el determinante '{p}' viene {sig}"
        if e == "ADP" and sig not in TRAS_ADP:
            return f"R4: tras la preposición '{p}' viene {sig}"
    return ""


def analizar_hf(casos: list[Caso], modelo: str = HF_MODELO) -> list[dict]:
    import torch
    import transformers
    etiquetador = EtiquetadorHF(modelo)
    version = f"HuggingFace transformers {transformers.__version__} (torch {torch.__version__}), modelo {modelo}"
    out = []
    for c in casos:
        palabras = palabras_de(c.oracion)
        t0 = time.perf_counter()
        etiquetas = etiquetador.etiquetar(palabras)
        ms = 1000 * (time.perf_counter() - t0)
        motivo = reglas_upos(palabras, etiquetas)
        out.append(registro("HuggingFace + reglas", version, c, motivo == "", motivo, None, palabras, etiquetas, ms))
    return out


# ------------------------------------------------------------------ programa
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m tlp.espanol.comparacion_nlp",
                                 description="Corre el parser propio, spaCy y HuggingFace y escribe sus logs.")
    ap.add_argument("--modelos", nargs="+", default=["sm"], help="sufijos de es_core_news_* (por defecto: sm)")
    ap.add_argument("--hf-modelo", default=HF_MODELO, help=f"etiquetador UPOS de HuggingFace (por defecto: {HF_MODELO})")
    ap.add_argument("--salida", default=DIR_LOGS, help="carpeta de los logs (por defecto: resultados/fase2/logs)")
    a = ap.parse_args(argv)

    casos = cargar_conjunto()
    logs = {"parser.jsonl": analizar_propio(casos)}
    for sufijo in a.modelos:
        try:
            crudo, conc = analizar_spacy(casos, sufijo)
            logs[f"spacy_{sufijo}_crudo.jsonl"], logs[f"spacy_{sufijo}_concordancia.jsonl"] = crudo, conc
        except (ImportError, OSError) as e:
            print(f"[aviso] se omite spaCy es_core_news_{sufijo}: {e}", file=sys.stderr)
    try:
        logs["huggingface.jsonl"] = analizar_hf(casos, a.hf_modelo)
    except (ImportError, OSError) as e:
        print(f"[aviso] se omite HuggingFace {a.hf_modelo}: {e}", file=sys.stderr)

    for nombre, registros in logs.items():
        ruta = escribir_log(registros, os.path.join(a.salida, nombre))
        print(f"{registros[0]['sistema']:28} acepta {sum(r['acepta'] for r in registros):2}/{len(registros)} · "
              f"{registros[0]['version']}\n  log: {ruta}")
    print("\nPara calcular las métricas de todos los enfoques:  python -m tlp.espanol.evaluar")
    return 0


if __name__ == "__main__":
    sys.exit(main())
