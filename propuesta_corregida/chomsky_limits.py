"""
Módulo 5: Demostración ejecutable del límite CFG -> gramáticas sensibles al contexto.

Idea (jerarquía de Chomsky): una CFG empareja dependencias ANIDADAS (pila: a^n b^n, w w^R),
pero no dependencias CRUZADAS (copia: w w, a^n b^n c^n). Los patrones "respectivamente" del
español ("Juan, Ana y Luis son alto, alta y bajo respectivamente") exigen que el i-ésimo
sujeto concuerde con el i-ésimo adjetivo: dependencia cruzada = lenguaje de copia {ww}.

Este script NO prueba que "el español" no sea libre de contexto (es un debate abierto en
lingüística); muestra, con un fragmento concreto, por qué una CFG no puede reproducir el
patrón de concordancia cruzada y qué reconocedor sí puede.
"""

from itertools import product

GENDERS = "mf"


def is_nested(s: str) -> bool:
    """Lo que una CFG sí puede: S -> m S m | f S f | ε   (palíndromos pares, w w^R)."""
    return len(s) % 2 == 0 and s == s[::-1]


def is_copy(s: str) -> bool:
    """Lo que se necesita: s = w w (dependencia cruzada). Requiere memoria no-pila (LBA / CSG)."""
    h = len(s) // 2
    return len(s) % 2 == 0 and s[:h] == s[h:]


def is_anbncn(s: str) -> bool:
    n = len(s) // 3
    return len(s) % 3 == 0 and s == "a" * n + "b" * n + "c" * n


def enumerate_language(pred, alphabet: str, length: int):
    return ["".join(t) for t in product(alphabet, repeat=length) if pred("".join(t))]


def report() -> str:
    out = ["=== Dependencias anidadas (CFG) vs cruzadas (fuera de CFG) ===", ""]
    out.append("Rasgo de género de cada sustantivo (m/f) seguido del de cada adjetivo, longitud 4 (2+2):")
    nested = set(enumerate_language(is_nested, GENDERS, 4))
    copy = set(enumerate_language(is_copy, GENDERS, 4))
    out.append(f"  CFG anidada  S -> m S m | f S f | ε   genera : {sorted(nested)}")
    out.append(f"  Concordancia cruzada requerida  {{ww}}   : {sorted(copy)}")
    out.append(f"  Aceptadas por la CFG pero MAL concordadas : {sorted(nested - copy)}")
    out.append(f"  Bien concordadas que la CFG RECHAZA       : {sorted(copy - nested)}")
    out.append("")
    out.append("Ejemplo español (3 sujetos, 3 adjetivos):")
    subj = "mff"   # p. ej. Juan(m), Ana(f), María(f)
    labels = {"mff": "alto, alta, alta   (correcto)", "ffm": "alta, alta, alto   (orden inverso)",
              "mmf": "alto, alto, alta   (incorrecto)", "fmm": "alta, alto, alto   (incorrecto)"}
    for adj in ("mff", "ffm", "mmf", "fmm"):
        out.append(f"  sujetos=m,f,f  adjetivos={labels[adj]:<34} "
                   f"concordancia cruzada válida={is_copy(subj + adj)!s:<5}  la CFG anidada la acepta={is_nested(subj + adj)}")
    out.append("")
    out.append("Lectura: la CFG anidada acepta el orden INVERSO (primer sujeto con último adjetivo) y rechaza el correcto.")
    return "\n".join(out)


if __name__ == "__main__":
    print(report())
