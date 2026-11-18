// errores_defensa.mc: programa de Mini-C con 4 errores sintácticos para la demo.
// Correr con --recuperar para ver los 4 errores y el árbol de lo que sí es válido.
int a = 10;
int b = 5 5;          // ERROR 1: dos operandos seguidos, falta un operador o el ';'
print(b);
int c = a + * b;      // ERROR 2: falta el operando entre '+' y '*'
print(c);
x = (a + b;           // ERROR 3: paréntesis sin cerrar
while (a > 0) { a = a - 1; }
5 = a;                // ERROR 4: asignar a un literal (una sentencia no puede empezar con un número)
print(a);
