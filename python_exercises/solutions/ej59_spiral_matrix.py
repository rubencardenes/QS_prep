# EJ 59 — Spiral Matrix — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej59_spiral_matrix.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import sys
from typing import List


# ---------------------------------------------------------------------------
# EJ 59 — Spiral Matrix. Complejidad: O(m * n) tiempo, O(1) espacio extra.
# Cuatro límites (top, bottom, left, right) delimitan el rectángulo que
# falta por recorrer. En cada vuelta recorremos los cuatro lados del
# rectángulo (arriba de izq. a der., derecha de arriba a abajo, abajo de
# der. a izq., izquierda de abajo a arriba) y estrechamos el límite
# correspondiente tras cada lado. Comprobamos top <= bottom / left <=
# right antes de los dos últimos lados porque, en matrices no
# cuadradas, el rectángulo puede quedar reducido a una sola fila o
# columna a mitad de vuelta.
def spiral_order(matrix: List[List[int]]) -> List[int]:
    if not matrix or not matrix[0]:
        return []

    top, bottom = 0, len(matrix) - 1
    left, right = 0, len(matrix[0]) - 1
    result: List[int] = []

    while top <= bottom and left <= right:
        for col in range(left, right + 1):
            result.append(matrix[top][col])
        top += 1

        for row in range(top, bottom + 1):
            result.append(matrix[row][right])
        right -= 1

        if top <= bottom:
            for col in range(right, left - 1, -1):
                result.append(matrix[bottom][col])
            bottom -= 1

        if left <= right:
            for row in range(bottom, top - 1, -1):
                result.append(matrix[row][left])
            left += 1

    return result


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
