# EJ 32 — Container With Most Water (dos punteros)
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej32_container_with_most_water.py
#   3. Cronométrate: apunta a ~20 min.
#   4. Solo si te atascas, mira solutions/ej32_container_with_most_water.py.

import sys
from typing import List


# ===========================================================================
# EJ 32 — Container With Most Water
#   `height[i]` es la altura de una pared vertical en la posición i.
#   Elige dos paredes que, junto con el eje X, formen un contenedor que
#   almacene la mayor cantidad de agua posible. El area es
#   min(height[i], height[j]) * (j - i). Devuelve esa area máxima.
#   Complejidad esperada: O(n) con dos punteros (NO O(n^2) probando todos
#   los pares).
# ---------------------------------------------------------------------------
def max_area(height: List[int]) -> int:
    if len(height) == 0:
        return 0
    max_area = 0
    l, r = 0, len(height)-1
    while l < r:
        area = (r - l)*min(height[l], height[r])
        max_area = max(max_area, area)
        if height[l] < height[r]:
            l += 1
        else:
            r -= 1

    return max_area


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
    check(max_area([1, 8, 6, 2, 5, 4, 8, 3, 7]) == 49, "EJ32 caso general del enunciado")
    check(max_area([1, 1]) == 1, "EJ32 dos paredes iguales")
    check(max_area([4, 3, 2, 1, 4]) == 16, "EJ32 los extremos son el par optimo")
    check(max_area([1, 2, 1]) == 2, "EJ32 tres paredes")
    check(max_area([1, 2, 4, 3]) == 4, "EJ32 el mejor par no son las mas altas")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
