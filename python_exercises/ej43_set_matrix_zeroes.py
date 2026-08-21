# EJ 43 — Set Matrix Zeroes (matriz in-place)
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej43_set_matrix_zeroes.py
#   3. Cronométrate: apunta a ~20-25 min.
#   4. Solo si te atascas, mira solutions/ej43_set_matrix_zeroes.py.

import sys
from typing import List


# ===========================================================================
# EJ 43 — Set Matrix Zeroes
#   Dada una matriz `matrix` (m x n), si un elemento es 0, pon toda su
#   fila y toda su columna a 0. Hazlo IN-PLACE (la función no devuelve
#   nada, muta `matrix` directamente). Cuidado: si marcas las filas/
#   columnas a medida que avanzas, puedes contaminar la detección de
#   ceros originales. Complejidad esperada: O(m*n) tiempo, idealmente
#   O(1) espacio extra (puedes usar la primera fila y columna como
#   marcadores en vez de sets).
# ---------------------------------------------------------------------------
def set_zeroes(matrix: List[List[int]]) -> None:
    for m in matrix:
        print(m)
    if matrix is None:
        return
    ROWS = len(matrix)
    COLS = len(matrix[0])
    r0, c0 = [], []
    for r in range(ROWS):
        for c in range(COLS):
            if matrix[r][c] == 0:
               r0.append(r)
               c0.append(c)
    for r in range(ROWS):
        for c in range(COLS):
            if r in r0 or c in c0:
                matrix[r][c] = 0

    for m in matrix:
        print(m)
                
    return


# ===========================================================================
#                        TEST HARNESS (no tocar)
# ===========================================================================
_pass = 0
_fail = 0


def check(ok: bool, name: str) -> None:
    global _pass, _fail
    _pass, _fail = (_pass + 1, _fail) if ok else (_pass, _fail + 1)
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}")


def main() -> None:
    m1 = [[1, 1, 1], [1, 0, 1], [1, 1, 1]]
    set_zeroes(m1)
    check(m1 == [[1, 0, 1], [0, 0, 0], [1, 0, 1]], "EJ43 un solo cero en el centro")

    m2 = [[0, 1, 2, 0], [3, 4, 5, 2], [1, 3, 1, 5]]
    set_zeroes(m2)
    check(m2 == [[0, 0, 0, 0], [0, 4, 5, 0], [0, 3, 1, 0]], "EJ43 dos ceros en la misma fila")

    m3 = [[1]]
    set_zeroes(m3)
    check(m3 == [[1]], "EJ43 matriz sin ceros")

    m4 = [[0]]
    set_zeroes(m4)
    check(m4 == [[0]], "EJ43 matriz de un solo elemento, ya es cero")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
