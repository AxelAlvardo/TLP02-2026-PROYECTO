### Métricas globales (71 oraciones)

| Sistema | TP | FP | FN | TN | Precisión | Cobertura | F1 | Rechazo correcto | Exactitud estructural (S,V,O) | Err. etiquetado | UPOS | ms/oración |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Parser propio (CFG) | 37 | 0 | 19 | 15 | 100.0% | 66.1% | 79.6% | 100.0% | 84.1% | 0 | — | 0.02 |
| spaCy sm (crudo) | 56 | 15 | 0 | 0 | 78.9% | 100.0% | 88.2% | 0.0% | 93.2% | 3 | 99.0% | 3.70 |
| spaCy sm + concordancia | 48 | 3 | 8 | 12 | 94.1% | 85.7% | 89.7% | 80.0% | 90.9% | 1 | 99.0% | 3.70 |
| spaCy md (crudo) | 56 | 15 | 0 | 0 | 78.9% | 100.0% | 88.2% | 0.0% | 95.5% | 2 | 99.5% | 3.94 |
| spaCy md + concordancia | 51 | 2 | 5 | 13 | 96.2% | 91.1% | 93.6% | 86.7% | 95.5% | 0 | 99.5% | 3.94 |

### Por nivel de complejidad

| Sistema | Nivel | TP | FP | FN | TN | Cobertura | Rechazo correcto |
|---|---|---|---|---|---|---|---|
| Parser propio (CFG) | 1 | 20 | 0 | 0 | 0 | 100.0% | — |
| Parser propio (CFG) | 2 | 15 | 0 | 0 | 10 | 100.0% | 100.0% |
| Parser propio (CFG) | 3 | 2 | 0 | 19 | 5 | 9.5% | 100.0% |
| spaCy sm (crudo) | 1 | 20 | 0 | 0 | 0 | 100.0% | — |
| spaCy sm (crudo) | 2 | 15 | 10 | 0 | 0 | 100.0% | 0.0% |
| spaCy sm (crudo) | 3 | 21 | 5 | 0 | 0 | 100.0% | 0.0% |
| spaCy sm + concordancia | 1 | 20 | 0 | 0 | 0 | 100.0% | — |
| spaCy sm + concordancia | 2 | 14 | 1 | 1 | 9 | 93.3% | 90.0% |
| spaCy sm + concordancia | 3 | 14 | 2 | 7 | 3 | 66.7% | 60.0% |
| spaCy md (crudo) | 1 | 20 | 0 | 0 | 0 | 100.0% | — |
| spaCy md (crudo) | 2 | 15 | 10 | 0 | 0 | 100.0% | 0.0% |
| spaCy md (crudo) | 3 | 21 | 5 | 0 | 0 | 100.0% | 0.0% |
| spaCy md + concordancia | 1 | 20 | 0 | 0 | 0 | 100.0% | — |
| spaCy md + concordancia | 2 | 14 | 0 | 1 | 10 | 93.3% | 100.0% |
| spaCy md + concordancia | 3 | 17 | 2 | 4 | 3 | 81.0% | 60.0% |
