import re

class FormalParser:
    def __init__(self, code):
        # 1. Lexer en una línea: extrae números, variables y operadores (+, *, =, (, ))
        self.tokens = re.findall(r'\d+|[a-zA-Z]+|[+*=\(\)]', code)
        self.pos = 0

    def actual(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consumir(self, esperado=None):
        tok = self.actual()
        if esperado and tok != esperado:
            raise SyntaxError(f"Error: Se esperaba '{esperado}', pero llegó '{tok}'")
        self.pos += 1
        return tok

    # Gramática LL(1): Sentencia -> ID '=' Expr
    def parse(self):
        var = self.consumir()
        if not var or not var.isalpha():
            raise SyntaxError("Error: La sentencia debe iniciar con una variable.")
        self.consumir('=')
        arbol = {'Asignacion': var, 'Valor': self.expr()}
        if self.actual() is not None:
            raise SyntaxError(f"Error: Token inesperado '{self.actual()}'")
        return arbol

    # Expr -> Term ('+' Term)*
    def expr(self):
        nodo = self.term()
        while self.actual() == '+':
            op = self.consumir()
            nodo = {'Op': op, 'Izq': nodo, 'Der': self.term()}
        return nodo

    # Term -> Factor ('*' Factor)*
    def term(self):
        nodo = self.factor()
        while self.actual() == '*':
            op = self.consumir()
            nodo = {'Op': op, 'Izq': nodo, 'Der': self.factor()}
        return nodo

    # Factor -> NUM | ID | '(' Expr ')'
    def factor(self):
        tok = self.actual()
        if tok == '(':
            self.consumir('(')
            nodo = self.expr()
            self.consumir(')')
            return nodo
        elif tok and tok.isalnum():
            return self.consumir()
        raise SyntaxError(f"Error sintáctico cerca de: '{tok}'")

if __name__ == "__main__":
    print("Árbol Formal:", FormalParser("x = 5 + 3 * 2").parse())