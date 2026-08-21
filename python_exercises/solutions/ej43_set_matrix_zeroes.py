# EJ 43 — Set Matrix Zeroes — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej43_set_matrix_zeroes.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import sys
from typing import List


# ---------------------------------------------------------------------------
# EJ 43 — Set Matrix Zeroes. Complejidad: O(m*n) tiempo, O(1) espacio
# extra.
# Se usan la primera fila y la primera columna de la propia matriz como
# marcadores de que fila/columna hay que poner a cero, guardando aparte
# si la primera fila/columna ya tenian algun cero originalmente (para no
# confundirlo con un marcador). Luego se aplican los marcadores al resto
# de la matriz, y al final se ponen a cero la primera fila/columna si
# hacia falta.
def set_zeroes(matrix: List[List[int]]) -> None:
    rows = len(matrix)
    cols = len(matrix[0])
    first_row_has_zero = any(matrix[0][c] == 0 for c in range(cols))
    first_col_has_zero = any(matrix[r][0] == 0 for r in range(rows))

    for r in range(1, rows):
        for c in range(1, cols):
            if matrix[r][c] == 0:
                matrix[r][0] = 0
                matrix[0][c] = 0

    for r in range(1, rows):
        for c in range(1, cols):
            if matrix[r][0] == 0 or matrix[0][c] == 0:
                matrix[r][c] = 0

    if first_row_has_zero:
        for c in range(cols):
            matrix[0][c] = 0
    if first_col_has_zero:
        for r in range(rows):
            matrix[r][0] = 0


# ===========================================================================
#                               TEST HARNESS
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
