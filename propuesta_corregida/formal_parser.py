"""
Módulo 1: Analizador léxico y sintáctico LL(1) (descendente recursivo) para un
subconjunto de un lenguaje tipo C: declaraciones, asignaciones, if / else if / else,
while, bloques y expresiones aritméticas con precedencia.

Salida: árbol sintáctico abstracto (AST). El árbol de derivación concreto (con los
no terminales) lo produce `ll1_table_parser.py`, que usa la tabla LL(1) calculada en
`ll1_analysis.py` a partir de la MISMA gramática.

Manejo de errores: el analizador lanza SyntaxErrorException con línea y columna.
Dentro de listas de sentencias aplica recuperación en modo pánico (sincroniza en ';'
o '}') para reportar varios errores en una sola pasada; la excepción final trae la
lista completa en `.errors`.
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Token:
    type: str
    value: str
    line: int
    column: int


@dataclass
class ASTNode:
    node_type: str
    value: Optional[str] = None
    children: List['ASTNode'] = field(default_factory=list)

    def pretty_print(self, level: int = 0) -> str:
        indent = "  " * level
        val_str = f" ({self.value})" if self.value is not None else ""
        result = f"{indent}{self.node_type}{val_str}\n"
        for child in self.children:
            result += child.pretty_print(level + 1)
        return result


class SyntaxErrorException(Exception):
    """Errores léxicos y sintácticos. `errors` agrupa todos los detectados."""

    def __init__(self, message: str, errors: Optional[List[str]] = None):
        super().__init__(message)
        self.errors = errors if errors is not None else [message]


class Lexer:
    """Analizador léxico basado en expresiones regulares (equivale a un AFD por token)."""

    TOKEN_SPECS = [
        ('KEYWORD',  r'\b(int|float|if|else|while)\b'),
        ('ID',       r'[a-zA-Z_][a-zA-Z0-9_]*'),
        ('NUMBER',   r'\d+(\.\d+)?'),
        ('RELOP',    r'==|!=|<=|>=|<|>'),
        ('ASSIGN',   r'='),
        ('PLUS',     r'\+'),
        ('MINUS',    r'-'),
        ('MUL',      r'\*'),
        ('DIV',      r'/'),
        ('LPAREN',   r'\('),
        ('RPAREN',   r'\)'),
        ('LBRACE',   r'\{'),
        ('RBRACE',   r'\}'),
        ('SEMI',     r';'),
        ('SKIP',     r'[ \t\r]+'),
        ('NEWLINE',  r'\n'),
        ('MISMATCH', r'.'),
    ]

    def __init__(self, source_code: str):
        self.source_code = source_code
        self.tokens: List[Token] = []
        self._tokenize()

    def _tokenize(self):
        tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in self.TOKEN_SPECS)
        line_num = 1
        line_start = 0

        for match in re.finditer(tok_regex, self.source_code):
            kind = match.lastgroup
            value = match.group()
            column = match.start() - line_start + 1

            if kind == 'NEWLINE':
                line_start = match.end()
                line_num += 1
            elif kind == 'SKIP':
                continue
            elif kind == 'MISMATCH':
                raise SyntaxErrorException(
                    f"Error Léxico: Carácter inesperado '{value}' en línea {line_num}, columna {column}."
                )
            else:
                self.tokens.append(Token(kind, value, line_num, column))

        end_col = len(self.source_code) - line_start + 1
        self.tokens.append(Token('EOF', 'EOF', line_num, end_col))


class FormalParser:
    """
    Parser descendente recursivo LL(1). Gramática (BNF, sin recursión por la izquierda
    y con prefijo común factorizado). Es la MISMA que `ll1_analysis.GRAMMAR`:

        Program    -> StmtList
        StmtList   -> Stmt StmtList | ε
        Stmt       -> DeclStmt | AssignStmt | IfStmt | WhileStmt | Block
        DeclStmt   -> Type ID DeclInit ';'
        Type       -> 'int' | 'float'
        DeclInit   -> '=' Expr | ε
        AssignStmt -> ID '=' Expr ';'
        IfStmt     -> 'if' '(' Cond ')' Block ElsePart
        ElsePart   -> 'else' ElseBody | ε
        ElseBody   -> Block | IfStmt
        WhileStmt  -> 'while' '(' Cond ')' Block
        Block      -> '{' StmtList '}'
        Cond       -> Expr RELOP Expr
        Expr       -> Term ExprTail
        ExprTail   -> ('+' | '-') Term ExprTail | ε
        Term       -> Factor TermTail
        TermTail   -> ('*' | '/') Factor TermTail | ε
        Factor     -> '(' Expr ')' | '-' Factor | ID | NUMBER

    Cada procedimiento decide con UN solo token de lookahead (propiedad LL(1)); la
    prueba formal (FIRST/FOLLOW sin conflictos) está en `ll1_analysis.py`.
    Los `while` de stmt_list/expr_tail/term_tail son la forma iterativa de las reglas
    recursivas por la derecha (equivalente, y construyen asociatividad izquierda).
    """

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.errors: List[str] = []

    @property
    def current_token(self) -> Token:
        return self.tokens[self.pos]

    def consume(self, expected_type: str, expected_value: Optional[str] = None) -> Token:
        token = self.current_token
        if token.type != expected_type:
            raise SyntaxErrorException(
                f"Error Sintáctico (Línea {token.line}, Col {token.column}): "
                f"Se esperaba token de tipo '{expected_type}', pero se encontró '{token.type}' ('{token.value}')."
            )
        if expected_value is not None and token.value != expected_value:
            raise SyntaxErrorException(
                f"Error Sintáctico (Línea {token.line}, Col {token.column}): "
                f"Se esperaba '{expected_value}', pero se encontró '{token.value}'."
            )
        self.pos += 1
        return token

    def parse(self) -> ASTNode:
        ast = self.program()
        if self.current_token.type != 'EOF':
            t = self.current_token
            self.errors.append(
                f"Error Sintáctico (Línea {t.line}, Col {t.column}): "
                f"Token inesperado '{t.value}' al final del programa."
            )
        if self.errors:
            raise SyntaxErrorException("\n".join(self.errors), errors=list(self.errors))
        return ast

    def program(self) -> ASTNode:
        node = ASTNode("Program")
        node.children = self.stmt_list()
        return node

    def stmt_list(self) -> List[ASTNode]:
        stmts = []
        while self.current_token.type in ('KEYWORD', 'ID', 'LBRACE'):
            start = self.pos
            try:
                stmts.append(self.stmt())
            except SyntaxErrorException as exc:
                self.errors.append(str(exc))
                self._synchronize(start)
        return stmts

    def _synchronize(self, start: int):
        """Recuperación en modo pánico: avanza hasta pasar un ';' o llegar a '}' / EOF."""
        if self.pos == start:          # garantiza progreso (evita ciclos infinitos)
            self.pos += 1
        elif (self.current_token.type == 'KEYWORD'
              and self.current_token.value in ('int', 'float', 'if', 'while')):
            return                     # el error fue un ';' omitido: no se come la sentencia siguiente
        while self.current_token.type not in ('SEMI', 'RBRACE', 'EOF'):
            self.pos += 1
        if self.current_token.type == 'SEMI':
            self.pos += 1

    def stmt(self) -> ASTNode:
        tok = self.current_token
        if tok.type == 'KEYWORD':
            if tok.value in ('int', 'float'):
                return self.decl_stmt()
            elif tok.value == 'if':
                return self.if_stmt()
            elif tok.value == 'while':
                return self.while_stmt()
        elif tok.type == 'ID':
            return self.assign_stmt()
        elif tok.type == 'LBRACE':
            return self.block()

        raise SyntaxErrorException(
            f"Error Sintáctico (Línea {tok.line}, Col {tok.column}): "
            f"Inicio de sentencia inválido '{tok.value}'."
        )

    def decl_stmt(self) -> ASTNode:
        type_tok = self.consume('KEYWORD')
        id_tok = self.consume('ID')
        children = []
        if self.current_token.type == 'ASSIGN':      # DeclInit -> '=' Expr | ε
            self.consume('ASSIGN')
            children.append(self.expr())
        self.consume('SEMI')
        return ASTNode("DeclStmt", value=f"{type_tok.value} {id_tok.value}", children=children)

    def assign_stmt(self) -> ASTNode:
        id_tok = self.consume('ID')
        self.consume('ASSIGN')
        expr_node = self.expr()
        self.consume('SEMI')
        return ASTNode("AssignStmt", value=id_tok.value, children=[expr_node])

    def if_stmt(self) -> ASTNode:
        self.consume('KEYWORD', 'if')
        self.consume('LPAREN')
        cond_node = self.cond()
        self.consume('RPAREN')
        then_block = self.block()
        children = [cond_node, then_block]

        if self.current_token.type == 'KEYWORD' and self.current_token.value == 'else':
            self.consume('KEYWORD', 'else')
            if self.current_token.type == 'KEYWORD' and self.current_token.value == 'if':
                children.append(self.if_stmt())      # else if
            else:
                children.append(self.block())

        return ASTNode("IfStmt", children=children)

    def while_stmt(self) -> ASTNode:
        self.consume('KEYWORD', 'while')
        self.consume('LPAREN')
        cond_node = self.cond()
        self.consume('RPAREN')
        body_block = self.block()
        return ASTNode("WhileStmt", children=[cond_node, body_block])

    def block(self) -> ASTNode:
        self.consume('LBRACE')
        stmts = self.stmt_list()
        self.consume('RBRACE')
        return ASTNode("Block", children=stmts)

    def cond(self) -> ASTNode:
        left = self.expr()
        relop = self.consume('RELOP')
        right = self.expr()
        return ASTNode("Condition", value=relop.value, children=[left, right])

    def expr(self) -> ASTNode:
        left = self.term()
        return self.expr_tail(left)

    def expr_tail(self, left: ASTNode) -> ASTNode:
        while self.current_token.type in ('PLUS', 'MINUS'):
            op = self.consume(self.current_token.type)
            right = self.term()
            left = ASTNode("BinOp", value=op.value, children=[left, right])
        return left

    def term(self) -> ASTNode:
        left = self.factor()
        return self.term_tail(left)

    def term_tail(self, left: ASTNode) -> ASTNode:
        while self.current_token.type in ('MUL', 'DIV'):
            op = self.consume(self.current_token.type)
            right = self.factor()
            left = ASTNode("BinOp", value=op.value, children=[left, right])
        return left

    def factor(self) -> ASTNode:
        tok = self.current_token
        if tok.type == 'LPAREN':
            self.consume('LPAREN')
            node = self.expr()
            self.consume('RPAREN')
            return node
        elif tok.type == 'MINUS':
            self.consume('MINUS')
            return ASTNode("UnaryOp", value='-', children=[self.factor()])
        elif tok.type == 'ID':
            t = self.consume('ID')
            return ASTNode("Identifier", value=t.value)
        elif tok.type == 'NUMBER':
            t = self.consume('NUMBER')
            return ASTNode("Literal", value=t.value)
        else:
            raise SyntaxErrorException(
                f"Error Sintáctico (Línea {tok.line}, Col {tok.column}): "
                f"Se esperaba una expresión válida (ID, NUMBER, '(' o '-'), pero se encontró '{tok.value}'."
            )


def parse_code(source: str) -> ASTNode:
    """Analiza `source`; lanza SyntaxErrorException (con `.errors`) si es inválido."""
    lexer = Lexer(source)
    parser = FormalParser(lexer.tokens)
    return parser.parse()


if __name__ == "__main__":
    sample_code = """
    int x = 10;
    float y = 20.5;
    int z;
    if (x < y) {
        x = x + 2 * (5 - 1);
    } else if (x == y) {
        y = -1;
    } else {
        y = 0;
    }
    """
    print("=== Entrada válida ===")
    print(parse_code(sample_code).pretty_print())

    bad_code = """
    int a = 5
    while (a < 10) { a = a + 1; }
    b = (3 + ;
    x = * 2;
    """
    print("=== Entrada inválida (recuperación en modo pánico) ===")
    try:
        parse_code(bad_code)
    except SyntaxErrorException as exc:
        for err in exc.errors:
            print(" -", err)
