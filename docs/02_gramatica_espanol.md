# Anexo B — Gramática libre de contexto para un subconjunto controlado del español (Fase 2)

## Alcance
Fragmento controlado del español: **3.ª persona**; tiempos **presente** y **pretérito perfecto simple**; sujeto
siempre explícito; oraciones transitivas (Sujeto-Verbo-Objeto), intransitivas y con cláusula completiva
(«dice que …»); adjetivos pospuestos; adverbios; frases preposicionales; relativas de sujeto («el gato que duerme»).
No cubre: coordinación, clíticos, negación, interrogativas, pasivas ni verbos copulativos.

**Preprocesamiento** (`tokenizar`): minúsculas, normalización Unicode NFC, se eliminan los signos `¿ ? ¡ ! . , ; :`
y se separan las contracciones «al» = «a el» y «del» = «de el».

## 1. Rasgos
| Rasgo | Variable | Dominio | Lo llevan |
|---|---|---|---|
| género | γ | `m`, `f` | Det, N, PN, Adj, SN |
| número | ν | `sg`, `pl` | Det, N, Adj, V, SN, SV, Rel |
| animacidad | α | `h` (humano), `a` (animal), `n` (no animado) | N, SN (todo PN es `h`) |
| tiempo | τ | `pres`, `pret` | V |
| subcategoría | — | `tr` (transitivo), `intr` (intransitivo), `comp` (completiva) | V |

Las palabras de género común (marcadas `mf` en el léxico: *estudiante*, *grande*, *inteligente*, *feliz*, *joven*)
pertenecen a las dos categorías de género (p. ej. *estudiante* ∈ N[m,sg,h] y N[f,sg,h]).

## 2. Definición formal: G = (N, Σ, P, S)

- **S = O** (oración). En la CFG pura generada por `cfg_nltk()` el símbolo inicial se llama `S`.
- **Σ** = las 181 formas del léxico (§5).
- **N** = { O, SN, SP, SPs, Rel, RelOpc, SV, AdvOpc, Obj, Adjs } ∪ { Det, N, PN, Adj, V, Adv, P, A, Que },
  cada uno indexado por los rasgos que lleva (§1).
- **P** = los esquemas siguientes. γ, ν, α y τ son variables sobre sus dominios finitos; **repetir una variable
  dentro de una producción obliga a que los valores coincidan** (así se expresa la concordancia).

```
(1)  O           → SN[γ,ν,α] SV[ν]
(2)  SN[γ,sg,h]  → PN[γ]
(3)  SN[γ,ν,α]   → Det[γ,ν] N[γ,ν,α] Adjs[γ,ν] SPs RelOpc[ν]
(4)  Adjs[γ,ν]   → Adj[γ,ν] Adjs[γ,ν]  |  ε
(5)  SPs         → SP SPs  |  ε
(6)  SP          → P SN[γ,ν,α]
(7)  RelOpc[ν]   → Rel[ν]  |  ε
(8)  Rel[ν]      → Que SV[ν]
(9)  SV[ν]       → V[τ,ν,intr] AdvOpc SPs
(10) SV[ν]       → V[τ,ν,tr] AdvOpc Obj AdvOpc SPs
(11) SV[ν]       → V[τ,ν,comp] Que O
(12) AdvOpc      → Adv  |  ε
(13) Obj         → SN[γ,ν,α]          con α ∈ {a, n}
(14) Obj         → A SN[γ,ν,α]        con α ∈ {h, a}
(15) Det, N, PN, Adj, V, Adv, P → las palabras del léxico con esos rasgos (§5);  A → a ;  Que → que
```

En (6), (13) y (14) los rasgos del SN son libres: no concuerdan con nada fuera de ese SN.
Los auxiliares Adjs, SPs, RelOpc y AdvOpc solo existen para escribir en BNF los operadores `*` y `?`; el parser
los aplana, por eso no aparecen como nodos en los árboles.

**Es una CFG.** Cada variable recorre un dominio finito, así que cada esquema equivale a un número finito de
producciones ordinarias A → β con A ∈ N y β ∈ (N ∪ Σ)\*. La función `cfg_nltk()` hace esa expansión (con sus
propios nombres de auxiliares) y obtiene una **CFG pura de 338 producciones y 71 no terminales**; las pruebas
(`tests/test_espanol_extension.py`, `TestCFGPura`) comprueban que el parser con rasgos y el ChartParser de NLTK
sobre esa CFG pura aceptan las mismas oraciones.

## 3. Concordancia dentro de las limitaciones de las CFG
| Concordancia | Producciones | Rasgos compartidos |
|---|---|---|
| Determinante–sustantivo | (3) | γ, ν |
| Sustantivo–adjetivo | (3), (4) | γ, ν |
| Sujeto–verbo | (1) → (9)/(10)/(11) | ν |
| Antecedente–verbo de la relativa | (3), (7), (8) | ν |
| «a personal» (objeto humano exige «a»; animal admite ambas formas; no animado no la admite) | (13), (14) | α |

El tiempo τ no concuerda con nada: los dos tiempos están disponibles en (9), (10) y (11).
Como los rasgos tienen dominio finito y las dependencias que expresan son **anidadas** (no cruzadas), la
concordancia solo aumenta el tamaño de la gramática (de 14 esquemas a 338 producciones), no su poder expresivo:
el lenguaje sigue siendo **libre de contexto (Tipo 2)**.

## 4. Requisitos de la Fase 2 cubiertos
| Requisito | Producciones |
|---|---|
| Oraciones Sujeto-Verbo-Objeto | (1) + (10) |
| Adjetivos | (3), (4) |
| Adverbios | (9), (10), (12) |
| Frases preposicionales | (3), (5), (6), (9), (10) |
| Al menos dos tiempos verbales | τ ∈ {pres, pret} en (9), (10), (11) |
| Concordancia básica | §3 |
| Vocabulario reducido pero suficiente | §5 (181 formas) |

## 5. Léxico (Σ, 181 formas)
**Det (8)** — `el` [m,sg] · `la` [f,sg] · `los` [m,pl] · `las` [f,pl] · `un` [m,sg] · `una` [f,sg] · `unos` [m,pl] · `unas` [f,pl]

**N (28 lemas, 56 formas: singular/plural)**
| Animacidad | Masculino | Femenino | Común (mf) |
|---|---|---|---|
| `a` animal | gato/gatos, perro/perros, ratón/ratones, pájaro/pájaros | gata/gatas, perra/perras | — |
| `h` humano | niño/niños, profesor/profesores, hombre/hombres | niña/niñas, profesora/profesoras, mujer/mujeres | estudiante/estudiantes |
| `n` no animado | libro/libros, pan/panes, sombrero/sombreros, telescopio/telescopios, jardín/jardines, parque/parques | carta/cartas, casa/casas, mesa/mesas, manzana/manzanas, puerta/puertas, ventana/ventanas, escuela/escuelas, ciudad/ciudades, cocina/cocinas | — |

**PN (4)** — `juan` [m] · `pedro` [m] · `maría` [f] · `ana` [f]; todos [sg, h].

**Adj (12 lemas, 40 formas)**
- 4 formas (-o, -a, -os, -as): negro, blanco, pequeño, nuevo, viejo, rápido, cansado, simpático.
- 2 formas (género común, sg/pl): grande/grandes, inteligente/inteligentes, feliz/felices, joven/jóvenes.

**V (15 lemas, 60 formas)**
| Lema | Subcat. | pres sg | pres pl | pret sg | pret pl |
|---|---|---|---|---|---|
| perseguir | tr | persigue | persiguen | persiguió | persiguieron |
| ver | tr | ve | ven | vio | vieron |
| comer | tr | come | comen | comió | comieron |
| leer | tr | lee | leen | leyó | leyeron |
| escribir | tr | escribe | escriben | escribió | escribieron |
| comprar | tr | compra | compran | compró | compraron |
| mirar | tr | mira | miran | miró | miraron |
| abrir | tr | abre | abren | abrió | abrieron |
| correr | intr | corre | corren | corrió | corrieron |
| dormir | intr | duerme | duermen | durmió | durmieron |
| llegar | intr | llega | llegan | llegó | llegaron |
| cantar | intr | canta | cantan | cantó | cantaron |
| trabajar | intr | trabaja | trabajan | trabajó | trabajaron |
| decir | comp | dice | dicen | dijo | dijeron |
| pensar | comp | piensa | piensan | pensó | pensaron |

**Adv (5)** — rápidamente · lentamente · siempre · tranquilamente · hoy

**P (7)** — con · en · de · para · sobre · por · a  (la forma `a` también es el terminal de A en (14))

**Que (1)** — que

## 6. Ambigüedad y elección del parser
La gramática es **ambigua**: una frase preposicional después del objeto puede colgar del SN (3) o del SV (10).
«el hombre ve al gato con el telescopio» tiene 2 derivaciones; con 2 y 3 frases preposicionales hay 5 y 14
(números de Catalan, comprobado en `tests/test_espanol_extension.py`, `TestAmbiguedad`). Una gramática ambigua
no puede ser LL(1), por eso el parser es **descendente recursivo con retroceso**, implementado con generadores
para devolver **todas** las derivaciones (`ParserEspanol.parse_todos`).

## 7. Fuente de verdad en código
`tlp/espanol/gramatica_es.py`: `LEXICO` (§5), `REGLAS_BNF` (estas mismas reglas en forma compacta, con `*` y `?`),
`ParserEspanol` y `cfg_nltk()`.

| Producciones | Método de `ParserEspanol` |
|---|---|
| (1) | `_O` |
| (2), (3) | `_SN` |
| (4) | `_ADJS` |
| (5) | `_SPS` |
| (6) | `_SP` |
| (7), (8) | `_cola_SN` |
| (9), (10), (11) | `_SV` |
| (12) | `_ADV` |
| (13), (14) | `_OBJ` |

Los nodos de los árboles muestran los rasgos: `Det[m,sg]`, `N[m,sg]`, `Adj[m,sg]`, `PN[f,sg]`, `V[pret,pl]`.
Las palabras de género común conservan en el árbol el valor del léxico (`N[mf,pl]`, `Adj[mf,sg]`); el género del SN
lo fija el determinante.
