LEXICO = {
    "el": ("DET", "m_sg"), "la": ("DET", "f_sg"), "los": ("DET", "m_pl"), "un": ("DET", "m_sg"),
    "gato": ("N", "m_sg"), "gatos": ("N", "m_pl"), "ratón": ("N", "m_sg"), "niña": ("N", "f_sg"),
    "negro": ("ADJ", "m_sg"), "negros": ("ADJ", "m_pl"),
    "persigue": ("V", "sg"), "ve": ("V", "sg"), "corre": ("V", "sg"),
    "que": ("REL", "inv")
}

class SpanishParser:
    def __init__(self, oracion):
        self.palabras = oracion.lower().split()
        self.pos = 0

    def consumir(self, tipo_esp, rasgo_esp=None):
        if self.pos >= len(self.palabras):
            raise SyntaxError("Error: Oración incompleta.")
        pal = self.palabras[self.pos]
        if pal not in LEXICO:
            raise SyntaxError(f"Fallo Léxico: '{pal}' no existe en el diccionario.")
        tipo, rasgo = LEXICO[pal]
        if tipo != tipo_esp:
            raise SyntaxError(f"Fallo de Orden/Estructura: Se esperaba {tipo_esp}, llegó '{pal}' ({tipo}).")
        if rasgo_esp and rasgo != rasgo_esp:
            raise SyntaxError(f"Fallo de Concordancia: '{pal}' ({rasgo}) no concuerda con ({rasgo_esp}).")
        self.pos += 1
        return pal, rasgo

    def parse(self):
        # Regla rígida: Oración -> Sintagma Nominal (Sujeto) + Sintagma Verbal
        sujeto, num = self.sintagma_nominal()
        verbo, _ = self.consumir("V", num) # Exige que el verbo coincida en singular/plural
        objeto, _ = self.sintagma_nominal()

        if self.pos < len(self.palabras):
            raise SyntaxError(f"Fallo por Complejidad: No se pudo procesar desde '{self.palabras[self.pos]}'.")
        return {'Oracion': {'Sujeto': sujeto, 'Verbo': verbo, 'Objeto': objeto}}

    def sintagma_nominal(self):
        det, rasgo = self.consumir("DET")
        sust, _ = self.consumir("N", rasgo) # Exige mismo género y número que el determinante
        nodo = {'DET': det, 'N': sust}
        # Adjetivo opcional
        if self.pos < len(self.palabras) and LEXICO.get(self.palabras[self.pos], ("",))[0] == "ADJ":
            nodo['ADJ'], _ = self.consumir("ADJ", rasgo)
        return nodo, rasgo.split('_')[1] # Retorna 'sg' o 'pl'

ORACIONES = [
    "el gato negro persigue un ratón",            # 1. Pasa: estructura fija SVO
    "la gatos negros persigue un ratón",          # 2. Falla: mala concordancia ("la gatos")
    "persigue un ratón",                          # 3. Falla: sujeto tácito (válido en español, inválido en CFG)
    "la niña que ve el gato corre"                # 4. Falla: cláusula subordinada ("que ve...") rompe el parser
]

if __name__ == "__main__":
    for o in ORACIONES:
        try:
            print(f"ÉXITO: '{o}' ->", SpanishParser(o).parse())
        except SyntaxError as e:
            print(f"FALLO: '{o}' -> {e}")