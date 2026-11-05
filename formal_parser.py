"""
Módulo 1: Analizador Léxico y Sintáctico LL(1) para Lenguaje Formal.
Soporta asignaciones, estructuras de control (if/while) y expresiones aritméticas.
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
    """Excepción personalizada para errores sintácticos y léxicos."""
    pass


class Lexer:
    """Analizador léxico basado en expresiones regulares."""
    
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
        ('SKIP',     r'[ \t]+'),
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

        self.tokens.append(Token('EOF', 'EOF', line_num, 0))


class FormalParser:
    """
    Parser Descendente Recursivo LL(1).
    Gramática libre de contexto (sin recursión por la izquierda):
        Program     -> StmtList EOF
        StmtList    -> Stmt StmtList | ε
        Stmt        -> DeclStmt | AssignStmt | IfStmt | WhileStmt | Block
        DeclStmt    -> ('int' | 'float') ID '=' Expr ';'
        AssignStmt  -> ID '=' Expr ';'
        IfStmt      -> 'if' '(' Cond ')' Block ('else' Block)?
        WhileStmt   -> 'while' '(' Cond ')' Block
        Block       -> '{' StmtList '}'
        Cond        -> Expr RELOP Expr
        Expr        -> Term ExprTail
        ExprTail    -> ('+' | '-') Term ExprTail | ε
        Term        -> Factor TermTail
        TermTail    -> ('*' | '/') Factor TermTail | ε
        Factor      -> '(' Expr ')' | ID | NUMBER
    """

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

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
            raise SyntaxErrorException(
                f"Error Sintáctico: Token inesperado '{t.value}' al final del archivo (Línea {t.line})."
            )
        return ast

    def program(self) -> ASTNode:
        node = ASTNode("Program")
        node.children = self.stmt_list()
        return node

    def stmt_list(self) -> List[ASTNode]:
        stmts = []
        while self.current_token.type in ('KEYWORD', 'ID', 'LBRACE'):
            stmts.append(self.stmt())
        return stmts

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
        self.consume('ASSIGN')
        expr_node = self.expr()
        self.consume('SEMI')
        return ASTNode("DeclStmt", value=f"{type_tok.value} {id_tok.value}", children=[expr_node])

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
            else_block = self.block()
            children.append(else_block)

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
        if self.current_token.type in ('PLUS', 'MINUS'):
            op = self.consume(self.current_token.type)
            right = self.term()
            new_left = ASTNode("BinOp", value=op.value, children=[left, right])
            return self.expr_tail(new_left)
        return left

    def term(self) -> ASTNode:
        left = self.factor()
        return self.term_tail(left)

    def term_tail(self, left: ASTNode) -> ASTNode:
        if self.current_token.type in ('MUL', 'DIV'):
            op = self.consume(self.current_token.type)
            right = self.factor()
            new_left = ASTNode("BinOp", value=op.value, children=[left, right])
            return self.term_tail(new_left)
        return left

    def factor(self) -> ASTNode:
        tok = self.current_token
        if tok.type == 'LPAREN':
            self.consume('LPAREN')
            node = self.expr()
            self.consume('RPAREN')
            return node
        elif tok.type == 'ID':
            t = self.consume('ID')
            return ASTNode("Identifier", value=t.value)
        elif tok.type == 'NUMBER':
            t = self.consume('NUMBER')
            return ASTNode("Literal", value=t.value)
        else:
            raise SyntaxErrorException(
                f"Error Sintáctico (Línea {tok.line}, Col {tok.column}): "
                f"Se esperaba una expresión válida (ID, NUMBER o '('), pero se encontró '{tok.value}'."
            )


def parse_code(source: str) -> ASTNode:
    lexer = Lexer(source)
    parser = FormalParser(lexer.tokens)
    return parser.parse()


if __name__ == "__main__":
    sample_code = """
    int x = 10;
    float y = 20.5;
    if (x < y) {
        x = x + 2 * (5 - 1);
    } else {
        y = 0;
    }
    """
    print("=== Demostración de Lenguaje Formal ===")
    ast = parse_code(sample_code)
    print(ast.pretty_print())