# EJ 6 — Search in Rotated Sorted Array (busqueda binaria)
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej6_search_rotated.py
#   3. Cronométrate: apunta a ~15-20 min.
#   4. Solo si te atascas, mira solutions/ej6_search_rotated.py.

import sys
from typing import List


# ===========================================================================
# EJ 6 — Search in Rotated Sorted Array
#   `nums` es un array ordenado ascendentemente sin duplicados, rotado un
#   número desconocido de posiciones. Devuelve el índice de `target` o -1
#   si no está presente. Complejidad esperada: O(log n).
# ---------------------------------------------------------------------------
def search(nums: List[int], target: int) -> int:
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
    check(search([4, 5, 6, 7, 0, 1, 2], 0) == 4, "EJ6 target en el lado rotado")
    check(search([4, 5, 6, 7, 0, 1, 2], 3) == -1, "EJ6 target ausente")
    check(search([1], 0) == -1, "EJ6 array de un elemento sin match")
    check(search([1], 1) == 0, "EJ6 array de un elemento con match")
    check(search([5, 1, 3], 5) == 0, "EJ6 target justo en el pivote")
    check(search([], 5) == -1, "EJ6 array vacio")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
