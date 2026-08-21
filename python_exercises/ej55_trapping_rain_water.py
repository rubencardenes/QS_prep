# EJ 55 — Trapping Rain Water (dos punteros)  [dificil]
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej55_trapping_rain_water.py
#   3. Cronométrate: apunta a ~20-25 min.
#   4. Solo si te atascas, mira solutions/ej55_trapping_rain_water.py.

import sys
from typing import List


# ===========================================================================
# EJ 55 — Trapping Rain Water
#   Dado un array `height` que representa un mapa de elevación (cada
#   posición tiene ancho 1), calcula cuánta agua de lluvia queda
#   atrapada entre las barras después de llover.
#   Complejidad esperada: O(n) tiempo, O(1) espacio. Pista: el agua
#   atrapada en la posición i es min(max izquierda, max derecha) -
#   height[i]. Con dos punteros (left, right) y dos variables
#   left_max/right_max, puedes calcularlo en una sola pasada sin arrays
#   auxiliares: mueve siempre el puntero del lado con el máximo más
#   pequeño.
# ---------------------------------------------------------------------------
def trap(height: List[int]) -> int:
    if len(height) < 3:
        return 0
    max_prev, max_current = -1, -1
    if height[0] > height[1]: 
        max_current = 0
    partial_accum, accum = 0, 0
    for i in range(1,len(height)):
        if max_current >= 0 and height[i] < height[max_current]:
            partial_accum += height[max_current] - height[i]
            print(f"{i=} {partial_accum=}")
        if (i == len(height)-1 and height[i] > height[i-1]) or (i < len(height)-1 and ((height[i] > height[i+1] and height[i] > height[i-1]))):
            if max_current == -1:
                max_current = i
            else:
                max_prev = max_current
                max_current = i
                if (height[max_prev] > height[max_current]):
                    partial_accum = partial_accum - (max_current - max_prev)*(height[max_prev]-height[max_current])
                accum += partial_accum
            print(f"{max_current=} {partial_accum=} {accum}")
            partial_accum = 0
    print("Result ", accum)
    return accum

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
