# EJ 59 — Spiral Matrix (arrays / simulación de matriz)
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej59_spiral_matrix.py
#   3. Cronométrate: apunta a ~20-25 min.
#   4. Solo si te atascas, mira solutions/ej59_spiral_matrix.py.

import sys
from typing import List


# ===========================================================================
# EJ 59 — Spiral Matrix
#   Dada una matriz `matrix` de m x n, devuelve todos sus elementos en
#   orden espiral (empezando arriba a la izquierda, hacia la derecha,
#   luego abajo, luego izquierda, luego arriba, y así sucesivamente
#   hacia el interior).
#   Complejidad esperada: O(m * n) tiempo, O(1) espacio extra (sin
#   contar la salida). Pista: mantén cuatro límites (top, bottom, left,
#   right) y recorre los cuatro lados del rectángulo actual, estrechando
#   los límites después de cada lado.
# ---------------------------------------------------------------------------
def spiral_order(matrix: List[List[int]]) -> List[int]:
    # TODO
    raise NotImplementedError


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
    check(spiral_order([[1, 2, 3], [4, 5, 6], [7, 8, 9]]) ==
          [1, 2, 3, 6, 9, 8, 7, 4, 5], "EJ59 matriz cuadrada 3x3")
    check(spiral_order([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]) ==
          [1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7], "EJ59 matriz 3x4")
    check(spiral_order([[1]]) == [1], "EJ59 una sola celda")
    check(spiral_order([[1, 2], [3, 4]]) == [1, 2, 4, 3], "EJ59 matriz 2x2")
    check(spiral_order([]) == [], "EJ59 matriz vacia")
    check(spiral_order([[1], [2], [3]]) == [1, 2, 3], "EJ59 una sola columna")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
