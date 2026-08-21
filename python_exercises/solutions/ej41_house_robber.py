# EJ 41 — House Robber — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej41_house_robber.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import sys
from typing import List


# ---------------------------------------------------------------------------
# EJ 41 — House Robber. Complejidad: O(n) tiempo, O(1) espacio.
# Para cada casa hay dos opciones: no robarla (el máximo sigue siendo el
# de la casa anterior) o robarla (su valor + el máximo de dos casas
# atrás, ya que la anterior queda descartada). Se guarda solo el máximo
# acumulado hasta la casa anterior y hasta dos casas atrás.
def rob(nums: List[int]) -> int:
    prev2, prev1 = 0, 0
    for n in nums:
        prev2, prev1 = prev1, max(prev1, prev2 + n)
    return prev1


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
    check(rob([1, 2, 3, 1]) == 4, "EJ41 caso general (robar casas 0 y 2)")
    check(rob([2, 7, 9, 3, 1]) == 12, "EJ41 robar casas 0, 2 y 4")
    check(rob([]) == 0, "EJ41 sin casas")
    check(rob([5]) == 5, "EJ41 una sola casa")
    check(rob([2, 1, 1, 2]) == 4, "EJ41 mejor robar los extremos")
    check(rob([5, 5, 10, 100, 10, 5]) == 110, "EJ41 casa central muy valiosa")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
