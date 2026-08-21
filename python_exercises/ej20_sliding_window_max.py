# EJ 20 — Sliding Window Maximum (deque monotona)  [dificil]
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej20_sliding_window_max.py
#   3. Cronométrate: apunta a ~25-30 min.
#   4. Solo si te atascas, mira solutions/ej20_sliding_window_max.py.

import sys
from typing import List


# ===========================================================================
# EJ 20 — Sliding Window Maximum
#   Dado un array `nums` y el tamaño de ventana `k`, devuelve un array con
#   el máximo de cada ventana deslizante de tamaño k al recorrer `nums` de
#   izquierda a derecha. Complejidad esperada: O(n) usando una deque que
#   guarda índices en orden decreciente de valor (no O(n*k) con fuerza
#   bruta).
# ---------------------------------------------------------------------------
def max_sliding_window(nums: List[int], k: int) -> List[int]:
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
    check(max_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 3) == [3, 3, 5, 5, 6, 7],
          "EJ20 caso general k=3")
    check(max_sliding_window([1], 1) == [1], "EJ20 ventana igual al array")
    check(max_sliding_window([9, 11], 2) == [11], "EJ20 array de dos elementos")
    check(max_sliding_window([4, -2], 2) == [4], "EJ20 con negativos")
    check(max_sliding_window([1, 2, 3, 4, 5], 1) == [1, 2, 3, 4, 5], "EJ20 ventana de tamaño 1")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
