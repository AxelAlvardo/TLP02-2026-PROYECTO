"""arbol.py - Estructura de árbol de análisis sintáctico + visualización.

Se comparte entre el parser formal (Fase 1) y el parser del español (Fases 1 y 2).
La visualización usa solo matplotlib (sin binarios externos como Graphviz).
"""
from __future__ import annotations


class Node:
    """Nodo del árbol de análisis. Las hojas tienen `children == []`."""

    def __init__(self, label: str, children: list["Node"] | None = None):
        self.label = label
        self.children = children or []

    @property
    def es_hoja(self) -> bool:
        return not self.children

    # --- representaciones textuales -------------------------------------
    def bracket(self) -> str:
        """Notación con paréntesis: (O (SN (Det el) (N gato)) ...)"""
        if self.es_hoja:
            return self.label
        return "(" + self.label + " " + " ".join(c.bracket() for c in self.children) + ")"

    def indentado(self, prefijo: str = "", ultimo: bool = True, raiz: bool = True) -> str:
        """Árbol en ASCII, apto para consola."""
        if raiz:
            salida = self.label + "\n"
            nuevo = ""
        else:
            salida = prefijo + ("└── " if ultimo else "├── ") + self.label + "\n"
            nuevo = prefijo + ("    " if ultimo else "│   ")
        for i, c in enumerate(self.children):
            salida += c.indentado(nuevo, i == len(self.children) - 1, False)
        return salida

    def hojas(self) -> list[str]:
        if self.es_hoja:
            return [self.label]
        return [h for c in self.children for h in c.hojas()]

    def to_nltk(self):
        """Convierte a nltk.Tree (por si se quiere usar draw() / pretty_print())."""
        from nltk import Tree
        if self.es_hoja:
            return self.label
        return Tree(self.label, [c.to_nltk() for c in self.children])

    def to_dict(self) -> dict:
        if self.es_hoja:
            return {"hoja": self.label}
        return {self.label: [c.to_dict() for c in self.children]}

    def __repr__(self) -> str:
        return self.bracket()


# ---------------------------------------------------------------------------
# Visualización con matplotlib
# ---------------------------------------------------------------------------
def dibujar_arbol(raiz: Node, ruta_png: str, titulo: str | None = None) -> str:
    """Dibuja `raiz` y lo guarda como PNG. Devuelve la ruta."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # 1) profundidad máxima y posición x de cada nodo (hojas equiespaciadas)
    contador = [0]
    pos: dict[int, tuple[float, int]] = {}
    max_prof = [0]

    def colocar(n: Node, prof: int) -> float:
        max_prof[0] = max(max_prof[0], prof)
        if n.es_hoja:
            x = float(contador[0])
            contador[0] += 1
        else:
            xs = [colocar(c, prof + 1) for c in n.children]
            x = sum(xs) / len(xs)
        pos[id(n)] = (x, prof)
        return x

    colocar(raiz, 0)
    n_hojas = max(contador[0], 1)
    ancho = max(6.0, 1.15 * n_hojas)
    alto = max(3.0, 0.85 * (max_prof[0] + 1))
    fig, ax = plt.subplots(figsize=(ancho, alto))

    def pintar(n: Node):
        x, prof = pos[id(n)]
        y = -(max_prof[0] if n.es_hoja else prof)  # hojas alineadas abajo
        for c in n.children:
            cx, cprof = pos[id(c)]
            cy = -(max_prof[0] if c.es_hoja else cprof)
            ax.plot([x, cx], [y - 0.12, cy + 0.2], color="#777777", lw=1, zorder=1)
            pintar(c)
        if n.es_hoja:
            ax.text(x, y, n.label, ha="center", va="center", fontsize=11, style="italic",
                    bbox=dict(boxstyle="round,pad=0.25", fc="#e8f1fb", ec="#7aa6d6"), zorder=2)
        else:
            ax.text(x, y, n.label, ha="center", va="center", fontsize=10, fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.25", fc="#fff6e0", ec="#d6a84a"), zorder=2)

    pintar(raiz)
    ax.set_xlim(-0.8, n_hojas - 0.2)
    ax.set_ylim(-max_prof[0] - 0.7, 0.7)
    ax.axis("off")
    if titulo:
        ax.set_title(titulo, fontsize=11)
    fig.tight_layout()
    fig.savefig(ruta_png, dpi=130)
    plt.close(fig)
    return ruta_png
