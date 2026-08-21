# EJ 32 — Container With Most Water — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej32_container_with_most_water.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import sys
from typing import List


# ---------------------------------------------------------------------------
# EJ 32 — Container With Most Water. Complejidad: O(n) tiempo, O(1)
# espacio.
# Dos punteros en los extremos: el area actual esta limitada por la pared
# mas baja de las dos, asi que mover el puntero de la pared mas alta
# nunca puede mejorar el resultado (el ancho baja y la altura limitante
# sigue siendo la misma o peor). Por eso siempre se mueve el puntero de
# la pared mas baja, buscando una pared mas alta que compense el ancho
# perdido.
def max_area(height: List[int]) -> int:
    left, right = 0, len(height) - 1
    best = 0
    while left < right:
        h = min(height[left], height[right])
        best = max(best, h * (right - left))
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
    return best


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
    check(max_area([1, 8, 6, 2, 5, 4, 8, 3, 7]) == 49, "EJ32 caso general del enunciado")
    check(max_area([1, 1]) == 1, "EJ32 dos paredes iguales")
    check(max_area([4, 3, 2, 1, 4]) == 16, "EJ32 los extremos son el par optimo")
    check(max_area([1, 2, 1]) == 2, "EJ32 tres paredes")
    check(max_area([1, 2, 4, 3]) == 4, "EJ32 el mejor par no son las mas altas")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
