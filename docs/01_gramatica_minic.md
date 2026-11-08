# Mini-C: subconjunto del lenguaje formal (Fase 1)

## Alcance
Subconjunto de C con: declaraciones (`int x;`, `int x = e;`), asignación, `if / else`, `while`, `print(e);`,
bloques `{ }`, expresiones aritméticas (`+ - * /`, paréntesis, negación unaria), comparaciones
(`== != < > <= >=`) y comentarios `//`. **Las llaves son obligatorias** en `if`/`while`: elimina el «else colgante».

## EBNF (lectura humana)
```ebnf
programa  = { sentencia } ;
sentencia = "int" ID [ "=" expr ] ";"
          | ID "=" expr ";"
          | "if" "(" cond ")" bloque [ "else" bloque ]
          | "while" "(" cond ")" bloque
          | "print" "(" expr ")" ";"
          | bloque ;
bloque    = "{" { sentencia } "}" ;
cond      = expr [ RELOP expr ] ;
expr      = term { ("+" | "-") term } ;
term      = factor { ("*" | "/") factor } ;
factor    = NUM | ID | "(" expr ")" | "-" factor ;
```

## BNF LL(1) (la que se implementa; sin recursión izquierda y factorizada)
```
Programa -> Stmts
Stmts    -> Stmt Stmts | ε
Stmt     -> int ID Init ;  | ID = Expr ;  | if ( Cond ) Bloque Else
          | while ( Cond ) Bloque | print ( Expr ) ; | Bloque
Init     -> = Expr | ε
Else     -> else Bloque | ε
Bloque   -> { Stmts }
Cond     -> Expr CondR          CondR -> RELOP Expr | ε
Expr     -> Term ExprR          ExprR -> + Term ExprR | - Term ExprR | ε
Term     -> Factor TermR        TermR -> * Factor TermR | / Factor TermR | ε
Factor   -> NUM | ID | ( Expr ) | - Factor
```
Fuente de verdad en código: `tlp/formal/gramatica.py` (`GRAMATICA`). `verificar_ll1()` calcula FIRST/FOLLOW sobre
ese mismo diccionario y confirma **0 conflictos**.

## FIRST / FOLLOW (calculados por el código)
| No terminal | FIRST | FOLLOW |
|---|---|---|
| Programa | `ID if int print while {` ε | `$` |
| Stmts | `ID if int print while {` ε | `$ }` |
| Stmt | `ID if int print while {` | `$ } ID if int print while {` |
| Init | `=` ε | `;` |
| Else | `else` ε | `$ } ID if int print while {` |
| Bloque | `{` | `$ } else ID if int print while {` |
| Cond | `( - ID NUM` | `)` |
| CondR | `RELOP` ε | `)` |
| Expr | `( - ID NUM` | `) ; RELOP` |
| ExprR | `+ -` ε | `) ; RELOP` |
| Term | `( - ID NUM` | `) + - ; RELOP` |
| TermR | `* /` ε | `) + - ; RELOP` |
| Factor | `( - ID NUM` | `) * + - / ; RELOP` |

## Nivel en la jerarquía de Chomsky
Los paréntesis anidados arbitrariamente (`((((1))))`) forman un lenguaje no regular: exige memoria de pila
(autómata de pila) ⇒ **Tipo 2, libre de contexto**. Lo que sí se sale de Tipo 2 en un lenguaje real
(declarar-antes-de-usar, tipos) es contexto *semántico*, que no se trata en esta fase.

## Manejo de errores
- **Léxico**: carácter ilegal ⇒ `ErrorSintactico` (nunca se descarta en silencio).
- **Sintáctico**: `consumir(tipo)` lanza `ErrorSintactico(mensaje, línea, columna)` con «se esperaba X pero llegó Y».
- **Recuperación (opcional)**: `analizar(código, recuperar=True)` sincroniza en `;` o `}` (modo pánico) y reporta varios errores.
