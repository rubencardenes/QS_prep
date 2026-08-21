# EJ 40 — Find Minimum in Rotated Sorted Array (busqueda binaria)
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej40_find_min_rotated_array.py
#   3. Cronométrate: apunta a ~20 min.
#   4. Solo si te atascas, mira solutions/ej40_find_min_rotated_array.py.

import sys
from typing import List


# ===========================================================================
# EJ 40 — Find Minimum in Rotated Sorted Array
#   Un array ordenado ascendentemente (sin duplicados) fue rotado un
#   número desconocido de posiciones (ej: [0,1,2,4,5,6,7] -> [4,5,6,7,0,
#   1,2]). Encuentra el elemento mínimo. Complejidad esperada: O(log n)
#   con búsqueda binaria (NO O(n) recorriendo todo el array).
# ---------------------------------------------------------------------------
def find_min(nums: List[int]) -> int:
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
    check(find_min([3, 4, 5, 1, 2]) == 1, "EJ40 caso general del enunciado")
    check(find_min([4, 5, 6, 7, 0, 1, 2]) == 0, "EJ40 rotacion mas grande")
    check(find_min([11, 13, 15, 17]) == 11, "EJ40 array sin rotar")
    check(find_min([2, 1]) == 1, "EJ40 dos elementos")
    check(find_min([1]) == 1, "EJ40 un solo elemento")
    check(find_min([5, 1, 2, 3, 4]) == 1, "EJ40 rotacion de un solo paso")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
