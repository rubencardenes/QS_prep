# EJ 58 — Unique Paths — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej58_unique_paths.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import sys
from typing import List


# ---------------------------------------------------------------------------
# EJ 58 — Unique Paths. Complejidad: O(m * n) tiempo, O(n) espacio.
# Solo necesitamos una fila de la tabla dp a la vez: `row[j]` empieza
# siendo 1 (representa la primera fila, donde solo hay un camino: ir
# siempre a la derecha). Para cada fila siguiente, row[j] += row[j - 1]
# acumula los caminos que llegan desde arriba (el valor viejo de row[j],
# antes de sumar) y desde la izquierda (row[j - 1], ya actualizado en
# esta misma fila).
def unique_paths(m: int, n: int) -> int:
    row: List[int] = [1] * n
    for _ in range(1, m):
        for j in range(1, n):
            row[j] += row[j - 1]
    return row[-1]


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
    check(unique_paths(3, 7) == 28, "EJ58 rejilla 3x7")
    check(unique_paths(3, 2) == 3, "EJ58 rejilla 3x2")
    check(unique_paths(1, 1) == 1, "EJ58 una sola celda")
    check(unique_paths(1, 5) == 1, "EJ58 una sola fila")
    check(unique_paths(5, 1) == 1, "EJ58 una sola columna")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
