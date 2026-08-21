# EJ 33 — Rotate Image (matriz in-place)
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej33_rotate_image.py
#   3. Cronométrate: apunta a ~20-25 min.
#   4. Solo si te atascas, mira solutions/ej33_rotate_image.py.

import sys
from typing import List


# ===========================================================================
# EJ 33 — Rotate Image
#   Dada una matriz cuadrada `matrix` (n x n), rótala 90 grados en sentido
#   horario, MODIFICÁNDOLA in-place (no crees una matriz nueva y la
#   devuelvas: la función no devuelve nada, muta `matrix` directamente).
#   Pista: transponer la matriz y luego invertir cada fila.
#   Complejidad esperada: O(n^2) tiempo, O(1) espacio extra.
# ---------------------------------------------------------------------------
def rotate(matrix: List[List[int]]) -> None:
    if matrix is None:
        return None
    N = len(matrix)
    
    for r in range(N):
        for c in range(r+1, N):
            temp = matrix[r][c]
            matrix[r][c] = matrix[c][r]
            matrix[c][r] = temp
    for r in range(N):
        matrix[r] = matrix[r][::-1]

    return None


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
    m1 = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    rotate(m1)
    check(m1 == [[7, 4, 1], [8, 5, 2], [9, 6, 3]], "EJ33 matriz 3x3")

    m2 = [[1, 2], [3, 4]]
    rotate(m2)
    check(m2 == [[3, 1], [4, 2]], "EJ33 matriz 2x2")

    m3 = [[1]]
    rotate(m3)
    check(m3 == [[1]], "EJ33 matriz 1x1")

    m4 = [[5, 1, 9, 11], [2, 4, 8, 10], [13, 3, 6, 7], [15, 14, 12, 16]]
    rotate(m4)
    check(m4 == [[15, 13, 2, 5], [14, 3, 4, 1], [12, 6, 8, 9], [16, 7, 10, 11]],
          "EJ33 matriz 4x4")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
