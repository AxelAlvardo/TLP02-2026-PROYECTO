"""llm_experimento.py - Fase 2: ¿sigue un LLM reglas gramaticales formales o se desvía hacia su conocimiento del español?

Condiciones:  zero-shot (solo reglas + léxico)   vs   few-shot (reglas + léxico + 6 ejemplos resueltos).
Referencia ("oráculo"): el veredicto del parser propio, que implementa exactamente las reglas dadas.
Métricas:
   acuerdo con el oráculo, desviación hacia el español (el LLM acepta algo que la gramática rechaza pero que
   SÍ es español correcto), sobre-rechazo (rechaza algo derivable) y árbol idéntico al del parser.

Uso:
    export ANTHROPIC_API_KEY=...                       (Windows PowerShell: $env:ANTHROPIC_API_KEY="...")
    python llm_experimento.py                          # corre las dos condiciones sobre las 71 oraciones
    python llm_experimento.py --limite 10              # prueba barata
    python llm_experimento.py --dry-run                # solo escribe los prompts en el log (sin llamar a la API)
    python llm_experimento.py --modelo claude-sonnet-5-5
    python llm_experimento.py --analizar               # recalcula el resumen a partir del log existente
Salidas:  resultados/llm_logs.jsonl (prompt + respuesta cruda de cada llamada)  y  resultados/llm_resumen.md
Si se usa otro proveedor (OpenAI, Gemini), basta reemplazar la función `llamar_llm`.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import time

from comparacion_nlp import cargar_dataset
from spanish_cfg import REGLAS_BNF, ParserEspanol, lexico_para_prompt

DIR = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(DIR, "resultados", "llm_logs.jsonl")
RESUMEN = os.path.join(DIR, "resultados", "llm_resumen.md")

SISTEMA = ("Eres un analizador sintáctico FORMAL. Aplicas ÚNICAMENTE la gramática y el léxico que se te dan. "
           "No uses tu conocimiento general del español: si una oración es correcta en español pero la gramática "
           "no puede derivarla, debes RECHAZARLA; si la gramática la deriva aunque suene rara, debes ACEPTARLA. "
           "Responde SOLO con un objeto JSON.")

FORMATO = ('Responde con JSON: {"acepta": true|false, "arbol": "<árbol en notación de paréntesis o null>", '
           '"regla_que_falla": "<regla o restricción violada, o null>", "razon": "<una frase>"}. '
           'Formato del árbol: (O (SN (Det[m,sg] el) (N[m,sg] gato)) (SV (V[pres,sg] corre))) — '
           'cada hoja es una palabra; los rasgos van entre corchetes en las categorías léxicas.')

# oraciones de ejemplo (NO pertenecen al conjunto de prueba)
EJEMPLOS = ["el pájaro canta", "la gata come una manzana", "los perros que duermen corren",
            "los pájaro cantan", "canta", "el niño canta y corre"]


def _arbol_ejemplo(parser, o):
    a, diag = parser.parse(o)
    return (a.bracket(), None, "") if a else (None, diag, diag)


def construir_prompt(oracion: str, few_shot: bool, parser=None) -> str:
    parser = parser or ParserEspanol()
    p = [f"GRAMÁTICA:\n{REGLAS_BNF}", f"LÉXICO (forma:rasgos):\n{lexico_para_prompt()}", FORMATO]
    if few_shot:
        p.append("EJEMPLOS RESUELTOS:")
        for e in EJEMPLOS:
            arbol, diag = parser.parse(e)
            r = {"acepta": True, "arbol": arbol.bracket(), "regla_que_falla": None, "razon": "derivable"} if arbol else \
                {"acepta": False, "arbol": None, "regla_que_falla": diag, "razon": "no derivable con la gramática dada"}
            p.append(f"Oración: {e}\n{json.dumps(r, ensure_ascii=False)}")
    p.append(f"Analiza esta oración:\nOración: {oracion}")
    return "\n\n".join(p)


def llamar_llm(prompt: str, modelo: str) -> str:
    import anthropic
    cliente = anthropic.Anthropic()
    r = cliente.messages.create(model=modelo, max_tokens=700, temperature=0, system=SISTEMA,
                                messages=[{"role": "user", "content": prompt}])
    return r.content[0].text


def extraer_json(txt: str):
    m = re.search(r"\{.*\}", txt, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group())
    except json.JSONDecodeError:
        return None


def _norm_arbol(b):
    return re.sub(r"\s+", " ", re.sub(r"\[[^\]]*\]", "", b or "")).strip().lower()


def correr(args):
    rows = cargar_dataset()[: args.limite] if args.limite else cargar_dataset()
    parser = ParserEspanol()
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "w", encoding="utf-8") as f:
        for cond in ("zero-shot", "few-shot"):
            for r in rows:
                prompt = construir_prompt(r["oracion"], cond == "few-shot", parser)
                reg = dict(id=r["id"], nivel=r["nivel"], condicion=cond, oracion=r["oracion"], modelo=args.modelo,
                           gramatical_es=r["gramatical_es"], prompt=prompt, respuesta=None, error=None)
                if not args.dry_run:
                    try:
                        reg["respuesta"] = llamar_llm(prompt, args.modelo)
                    except Exception as e:
                        reg["error"] = repr(e)
                    time.sleep(args.pausa)
                f.write(json.dumps(reg, ensure_ascii=False) + "\n")
                f.flush()
    print(f"Log escrito en {LOG}")


def analizar():
    parser = ParserEspanol()
    with open(LOG, encoding="utf-8") as f:
        regs = [json.loads(l) for l in f]
    if not any(r["respuesta"] for r in regs):
        print("El log no contiene respuestas (¿se usó --dry-run?). Nada que analizar.")
        return
    stats = {}
    for r in regs:
        s = stats.setdefault(r["condicion"], dict(n=0, sin_resp=0, acuerdo=0, desvia=0, sobre=0, ambos_acep=0,
                                                   arbol_ok=0, fp_otro=0, por_nivel={}))
        if not r["respuesta"]:
            s["sin_resp"] += 1
            continue
        j = extraer_json(r["respuesta"])
        if j is None:
            s["sin_resp"] += 1
            continue
        arbol, _ = parser.parse(r["oracion"])
        oraculo, llm = arbol is not None, bool(j.get("acepta"))
        s["n"] += 1
        pn = s["por_nivel"].setdefault(r["nivel"], [0, 0])
        pn[1] += 1
        if llm == oraculo:
            s["acuerdo"] += 1
            pn[0] += 1
        elif llm and not oraculo:
            s["desvia" if r["gramatical_es"] == "SI" else "fp_otro"] += 1
        else:
            s["sobre"] += 1
        if llm and oraculo:
            s["ambos_acep"] += 1
            s["arbol_ok"] += _norm_arbol(j.get("arbol")) == _norm_arbol(arbol.bracket())
    pct = lambda a, b: f"{100 * a / b:.1f}% ({a}/{b})" if b else "—"
    L = ["# Resumen del experimento con LLM", "",
         "| Condición | Oraciones válidas | Acuerdo con el parser | Desviación hacia el español | Aceptó agramatical | Sobre-rechazo | Árbol idéntico (si ambos aceptan) |",
         "|---|---|---|---|---|---|---|"]
    for c, s in stats.items():
        L.append(f"| {c} | {s['n']} (sin respuesta/JSON inválido: {s['sin_resp']}) | {pct(s['acuerdo'], s['n'])} | {s['desvia']} | "
                 f"{s['fp_otro']} | {s['sobre']} | {pct(s['arbol_ok'], s['ambos_acep'])} |")
    L += ["", "Acuerdo por nivel:", "", "| Condición | Nivel 1 | Nivel 2 | Nivel 3 |", "|---|---|---|---|"]
    for c, s in stats.items():
        L.append(f"| {c} | " + " | ".join(pct(*s["por_nivel"].get(n, [0, 0])) for n in ("1", "2", "3")) + " |")
    L += ["", "*Desviación hacia el español* = el LLM aceptó una oración que la gramática rechaza y que es español correcto."]
    with open(RESUMEN, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelo", default=os.environ.get("LLM_MODEL", "claude-sonnet-5-5"))
    ap.add_argument("--limite", type=int, default=0)
    ap.add_argument("--pausa", type=float, default=0.3)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--analizar", action="store_true")
    a = ap.parse_args()
    if not a.analizar:
        if not a.dry_run and not os.environ.get("ANTHROPIC_API_KEY"):
            raise SystemExit("Falta ANTHROPIC_API_KEY (o use --dry-run para generar solo los prompts).")
        correr(a)
    if not a.dry_run:
        analizar()
