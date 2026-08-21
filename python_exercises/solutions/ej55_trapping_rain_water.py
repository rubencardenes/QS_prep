# EJ 55 — Trapping Rain Water — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej55_trapping_rain_water.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import sys
from typing import List


# ---------------------------------------------------------------------------
# EJ 55 — Trapping Rain Water. Complejidad: O(n) tiempo, O(1) espacio.
# Dos punteros left/right que avanzan uno hacia el otro, junto con
# left_max/right_max (el máximo visto hasta cada puntero). En cada paso
# movemos el puntero del lado cuyo máximo es menor: si left_max <
# right_max, sabemos con certeza que el agua en `left` está limitada por
# left_max (porque a la derecha hay algo aún más alto que left_max, así
# que no importa el detalle del terreno entre medias), así que sumamos
# left_max - height[left] y avanzamos left. Simétrico para el otro lado.
def trap(height: List[int]) -> int:
    if not height:
        return 0

    left, right = 0, len(height) - 1
    left_max, right_max = height[left], height[right]
    water = 0

    while left < right:
        if left_max < right_max:
            left += 1
            left_max = max(left_max, height[left])
            water += left_max - height[left]
        else:
            right -= 1
            right_max = max(right_max, height[right])
            water += right_max - height[right]

    return water


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
    check(trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6,
          "EJ55 ejemplo clasico")
    check(trap([4, 2, 0, 3, 2, 5]) == 9, "EJ55 con un pico alto al final")
    check(trap([]) == 0, "EJ55 array vacio")
    check(trap([1, 1, 1]) == 0, "EJ55 superficie plana")
    check(trap([5, 4, 3, 2, 1]) == 0, "EJ55 estrictamente decreciente")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
