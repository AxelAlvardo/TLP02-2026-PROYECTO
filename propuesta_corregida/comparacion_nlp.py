"""comparacion_nlp.py - Evaluación cuantitativa: parser propio (CFG) vs spaCy (vs HuggingFace opcional).

Uso:
    python comparacion_nlp.py                      # parser propio + spaCy sm + spaCy md (si están instalados)
    python comparacion_nlp.py --modelos sm         # solo es_core_news_sm
    python comparacion_nlp.py --hf-model <modelo>  # añade un modelo HuggingFace de token-classification con
                                                   # etiquetas UPOS (solo mide etiquetado; ver nota abajo)

Definiciones (positivo = "la oración es gramatical y el sistema la ACEPTA"):
    TP: gramatical y aceptada       FP: agramatical y aceptada
    FN: gramatical y rechazada      TN: agramatical y rechazada
    Precisión = TP/(TP+FP)   Cobertura (recall) = TP/(TP+FN)   Rechazo correcto = TN/(TN+FP)
    Exactitud estructural = % de oraciones con tripleta (sujeto, verbo, objeto) correcta sobre las
                            que tienen etiqueta esperada y son gramaticales; una oración rechazada cuenta como error.
    Error de etiquetado   = oración correctamente aceptada pero con tripleta (S,V,O) incorrecta.

La verdad de referencia es la columna `gramatical_es` (juicio lingüístico), NO lo que acepta la gramática.
Por eso las oraciones de nivel 3 que el parser rechaza por diseño penalizan su cobertura: es el hallazgo.

spaCy y los modelos neuronales nunca "rechazan": siempre devuelven un árbol. Por eso se reportan DOS modos:
  crudo           acepta siempre (rechazo correcto = 0 por construcción)
  +concordancia   acepta salvo que (a) la raíz no sea verbo, (b) falle la concordancia de número
                  sujeto-verbo o de género/número det-sustantivo/adjetivo según los rasgos morfológicos
                  que el propio modelo predice.  Es un detector heurístico sencillo, no parte de spaCy.
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
import time
from collections import defaultdict

from spanish_cfg import LEMA_DE_FORMA, LEXICO, ParserEspanol, extraer_svo, tokenizar

DIR = os.path.dirname(os.path.abspath(__file__))
TIEMPO_MS: dict = {}          # sistema -> ms por oración (solo el análisis, sin cargar el modelo)
CAT2UPOS = {"DET": {"DET"}, "N": {"NOUN"}, "PN": {"PROPN"}, "ADJ": {"ADJ"}, "V": {"VERB", "AUX"},
            "ADV": {"ADV"}, "P": {"ADP"}, "QUE": {"PRON", "SCONJ"}}


def cargar_dataset(ruta=None):
    ruta = ruta or os.path.join(DIR, "dataset", "test_set.csv")
    with open(ruta, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def gold_triple(r):
    return (r["sujeto"], r["verbo"], r["objeto"])


def evaluable(r):
    return r["gramatical_es"] == "SI" and any(x not in ("*", "") for x in gold_triple(r))


def triple_ok(pred, r):
    return pred is not None and all(g == "*" or g == p for g, p in zip(gold_triple(r), pred))


# ------------------------------------------------------------------ parser propio
def correr_propio(rows):
    p = ParserEspanol()
    out = []
    t0 = time.perf_counter()
    for r in rows:
        arbol, diag = p.parse(r["oracion"])
        out.append(dict(acepta=arbol is not None, triple=extraer_svo(arbol) if arbol else None, nota=diag))
    TIEMPO_MS["Parser propio (CFG)"] = 1000 * (time.perf_counter() - t0) / len(rows)
    return out


# ------------------------------------------------------------------ spaCy
def _norm(tok):
    return LEMA_DE_FORMA.get(tok.text.lower()) or tok.lemma_.lower()


def _triple_spacy(doc):
    raiz = next((t for t in doc if t.dep_ == "ROOT"), None)
    if raiz is None:
        return None
    sujeto = next((_norm(c) for c in raiz.children if c.dep_.startswith(("nsubj", "csubj"))), "-")
    obj = next((_norm(c) for c in raiz.children if c.dep_ in ("obj", "dobj")), "-")
    return (sujeto, _norm(raiz), obj)


def _rasgo(tok, k):
    v = tok.morph.get(k)
    return v[0] if v else None


def _concordancia_ok(doc):
    raiz = next((t for t in doc if t.dep_ == "ROOT"), None)
    if raiz is None or raiz.pos_ not in ("VERB", "AUX"):
        return False, "la raíz no es un verbo"
    for t in doc:
        if t.dep_.startswith("nsubj") and t.head.pos_ in ("VERB", "AUX"):
            a, b = _rasgo(t, "Number"), _rasgo(t.head, "Number")
            if a and b and a != b:
                return False, f"número sujeto-verbo: {t.text} ({a}) vs {t.head.text} ({b})"
        if t.dep_ in ("det", "amod") and t.head.pos_ in ("NOUN", "PROPN"):
            for k in ("Number", "Gender"):
                a, b = _rasgo(t, k), _rasgo(t.head, k)
                if a and b and a != b:
                    return False, f"{k} {t.text} ({a}) vs {t.head.text} ({b})"
    return True, ""


def _etiquetas_spacy(doc, oracion):
    palabras = tokenizar(oracion)
    toks = [t for t in doc if not t.is_punct]
    if [t.text.lower() for t in toks] != palabras or any(w not in LEXICO for w in palabras):
        return None
    ok = 0
    for t, w in zip(toks, palabras):
        gold = set().union(*(CAT2UPOS[e.cat] for e in LEXICO[w]))
        ok += t.pos_ in gold
    return ok, len(palabras)


def correr_spacy(nombre_modelo, rows):
    import spacy
    nlp = spacy.load(nombre_modelo)
    crudo, conc, tags = [], [], []
    dur = 0.0
    for r in rows:
        t0 = time.perf_counter()
        doc = nlp(r["oracion"])
        dur += time.perf_counter() - t0
        tri = _triple_spacy(doc)
        ok, motivo = _concordancia_ok(doc)
        crudo.append(dict(acepta=True, triple=tri, nota=""))
        conc.append(dict(acepta=ok, triple=tri, nota=motivo))
        tags.append(_etiquetas_spacy(doc, r["oracion"]) if r["gramatical_es"] == "SI" else None)
    TIEMPO_MS[nombre_modelo] = 1000 * dur / len(rows)
    return crudo, conc, tags


# ------------------------------------------------------------------ HuggingFace (opcional, solo etiquetado)
def correr_hf(modelo, rows):
    """Usa un modelo de token-classification con etiquetas UPOS.  Solo mide el etiquetado de las
    oraciones del fragmento; no produce dependencias ni decide aceptación."""
    from transformers import pipeline
    pipe = pipeline("token-classification", model=modelo, aggregation_strategy="first")
    tags = []
    for r in rows:
        palabras = tokenizar(r["oracion"])
        if r["gramatical_es"] != "SI" or any(w not in LEXICO for w in palabras) or \
                {"a", "el"} <= set(palabras) and r["oracion"].lower().count(" al ") + r["oracion"].lower().count(" del "):
            tags.append(None)
            continue
        pred = pipe(r["oracion"].lower())
        if len(pred) != len(palabras):
            tags.append(None)           # desalineación de tokens: no se evalúa (se reporta el recuento)
            continue
        ok = sum(p["entity_group"].upper() in set().union(*(CAT2UPOS[e.cat] for e in LEXICO[w]))
                 for p, w in zip(pred, palabras))
        tags.append((ok, len(palabras)))
    return tags


# ------------------------------------------------------------------ métricas
def metricas(rows, res, tags=None):
    tp = fp = fn = tn = 0
    por_nivel = defaultdict(lambda: dict(tp=0, fp=0, fn=0, tn=0))
    ev = ev_ok = etiquetado = 0
    errores = []
    for r, x in zip(rows, res):
        gram, acepta = r["gramatical_es"] == "SI", x["acepta"]
        k = "tp" if gram and acepta else "fp" if (not gram) and acepta else "fn" if gram else "tn"
        por_nivel[r["nivel"]][k] += 1
        tp += k == "tp"; fp += k == "fp"; fn += k == "fn"; tn += k == "tn"
        if k in ("fp", "fn"):
            errores.append(dict(id=r["id"], nivel=r["nivel"], oracion=r["oracion"],
                                tipo="falso positivo" if k == "fp" else "falso negativo",
                                detalle=x["nota"] or r["fenomeno"]))
        if evaluable(r):
            ev += 1
            bien = acepta and triple_ok(x["triple"], r)
            ev_ok += bien
            if acepta and not bien:
                etiquetado += 1
                errores.append(dict(id=r["id"], nivel=r["nivel"], oracion=r["oracion"], tipo="error de etiquetado",
                                    detalle=f"esperado {gold_triple(r)} obtenido {x['triple']}"))
    div = lambda a, b: a / b if b else float("nan")
    m = dict(TP=tp, FP=fp, FN=fn, TN=tn,
             precision=div(tp, tp + fp), cobertura=div(tp, tp + fn), rechazo_correcto=div(tn, tn + fp),
             exactitud_estructural=div(ev_ok, ev), errores_etiquetado=etiquetado, n_evaluables=ev)
    p, c = m["precision"], m["cobertura"]
    m["f1"] = 2 * p * c / (p + c) if p + c else float("nan")
    if tags is not None:
        validos = [t for t in tags if t]
        m["exactitud_upos"] = div(sum(a for a, _ in validos), sum(b for _, b in validos))
        m["oraciones_upos"] = len(validos)
    return m, dict(por_nivel), errores


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelos", nargs="*", default=["sm", "md"], help="sufijos de es_core_news_*")
    ap.add_argument("--hf-model", default=None)
    ap.add_argument("--salida", default=os.path.join(DIR, "resultados"))
    a = ap.parse_args()
    os.makedirs(a.salida, exist_ok=True)
    rows = cargar_dataset()
    sistemas = {"Parser propio (CFG)": (correr_propio(rows), None)}
    for suf in a.modelos:
        try:
            crudo, conc, tags = correr_spacy(f"es_core_news_{suf}", rows)
        except Exception as e:                                            # modelo no instalado
            print(f"[aviso] no se pudo cargar es_core_news_{suf}: {e}", file=sys.stderr)
            continue
        sistemas[f"spaCy {suf} (crudo)"] = (crudo, tags)
        sistemas[f"spaCy {suf} + concordancia"] = (conc, tags)
    todos_err, glob, niv = [], [], []
    for nombre, (res, tags) in sistemas.items():
        m, pn, errs = metricas(rows, res, tags)
        m["ms_por_oracion"] = TIEMPO_MS["Parser propio (CFG)"] if nombre.startswith("Parser") \
            else TIEMPO_MS["es_core_news_" + nombre.split()[1]]
        glob.append((nombre, m))
        niv += [(nombre, n, d) for n, d in sorted(pn.items())]
        todos_err += [dict(sistema=nombre, **e) for e in errs]
    hf_tags = None
    if a.hf_model:
        hf_tags = correr_hf(a.hf_model, rows)

    # --- CSV
    campos = ["sistema", "TP", "FP", "FN", "TN", "precision", "cobertura", "f1", "rechazo_correcto",
              "exactitud_estructural", "errores_etiquetado", "n_evaluables", "exactitud_upos", "oraciones_upos", "ms_por_oracion"]
    with open(os.path.join(a.salida, "metricas_globales.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, campos, extrasaction="ignore")
        w.writeheader()
        for n, m in glob:
            w.writerow(dict(sistema=n, **{k: (round(v, 4) if isinstance(v, float) else v) for k, v in m.items()}))
    with open(os.path.join(a.salida, "errores_detalle.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, ["sistema", "id", "nivel", "oracion", "tipo", "detalle"])
        w.writeheader(); w.writerows(todos_err)

    # --- Markdown
    pct = lambda v: "—" if v != v else f"{100 * v:.1f}%"
    L = ["### Métricas globales (71 oraciones)", "",
         "| Sistema | TP | FP | FN | TN | Precisión | Cobertura | F1 | Rechazo correcto | Exactitud estructural (S,V,O) | Err. etiquetado | UPOS | ms/oración |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for n, m in glob:
        L.append(f"| {n} | {m['TP']} | {m['FP']} | {m['FN']} | {m['TN']} | {pct(m['precision'])} | {pct(m['cobertura'])} | "
                 f"{pct(m['f1'])} | {pct(m['rechazo_correcto'])} | {pct(m['exactitud_estructural'])} | "
                 f"{m['errores_etiquetado']} | {pct(m.get('exactitud_upos', float('nan')))} | {m['ms_por_oracion']:.2f} |")
    L += ["", "### Por nivel de complejidad", "", "| Sistema | Nivel | TP | FP | FN | TN | Cobertura | Rechazo correcto |", "|---|---|---|---|---|---|---|---|"]
    for n, nivel, d in niv:
        c = d["tp"] / (d["tp"] + d["fn"]) if d["tp"] + d["fn"] else float("nan")
        rj = d["tn"] / (d["tn"] + d["fp"]) if d["tn"] + d["fp"] else float("nan")
        L.append(f"| {n} | {nivel} | {d['tp']} | {d['fp']} | {d['fn']} | {d['tn']} | {pct(c)} | {pct(rj)} |")
    if hf_tags is not None:
        v = [t for t in hf_tags if t]
        L += ["", f"### HuggingFace `{a.hf_model}` (solo etiquetado)", "",
              f"Exactitud UPOS: {pct(sum(x for x, _ in v) / sum(y for _, y in v)) if v else '—'} sobre {len(v)} oraciones alineables."]
    with open(os.path.join(a.salida, "tablas.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))

    # --- Gráficas
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    nombres = [n for n, _ in glob]
    claves = [("precision", "Precisión"), ("cobertura", "Cobertura"), ("rechazo_correcto", "Rechazo correcto"),
              ("exactitud_estructural", "Exactitud (S,V,O)")]
    x = np.arange(len(nombres)); w = 0.2
    fig, ax = plt.subplots(figsize=(11, 4.8))
    for i, (k, et) in enumerate(claves):
        vals = [0 if m[k] != m[k] else 100 * m[k] for _, m in glob]
        b = ax.bar(x + (i - 1.5) * w, vals, w, label=et)
        ax.bar_label(b, fmt="%.0f", fontsize=7)
    ax.set_xticks(x); ax.set_xticklabels(nombres, rotation=15, ha="right", fontsize=8)
    ax.set_ylabel("%"); ax.set_ylim(0, 112); ax.legend(ncol=4, fontsize=8, loc="upper center")
    ax.set_title("Parser propio vs spaCy — 71 oraciones (referencia: gramaticalidad en español)")
    fig.tight_layout(); fig.savefig(os.path.join(a.salida, "grafica_metricas.png"), dpi=130); plt.close(fig)

    fig, axs = plt.subplots(1, 2, figsize=(11, 4))
    for ax, clave, titulo in [(axs[0], "cob", "Cobertura (recall) por nivel"), (axs[1], "rej", "Rechazo correcto por nivel")]:
        for j, nombre in enumerate(nombres):
            vals = []
            for nivel in ("1", "2", "3"):
                d = next(dd for nn, nv, dd in niv if nn == nombre and nv == nivel)
                num, den = (d["tp"], d["tp"] + d["fn"]) if clave == "cob" else (d["tn"], d["tn"] + d["fp"])
                vals.append(100 * num / den if den else 0)
            ax.bar(np.arange(3) + (j - len(nombres) / 2 + 0.5) * 0.8 / len(nombres), vals, 0.8 / len(nombres), label=nombre)
        ax.set_xticks(range(3)); ax.set_xticklabels(["Nivel 1", "Nivel 2", "Nivel 3"]); ax.set_ylim(0, 105)
        ax.set_title(titulo); ax.set_ylabel("%")
    axs[1].legend(fontsize=6, loc="upper right")
    fig.tight_layout(); fig.savefig(os.path.join(a.salida, "grafica_por_nivel.png"), dpi=130); plt.close(fig)
    print(f"\nArchivos escritos en {a.salida}")


if __name__ == "__main__":
    main()
