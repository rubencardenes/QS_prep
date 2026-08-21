# EJ 41 — House Robber (programacion dinamica)
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej41_house_robber.py
#   3. Cronométrate: apunta a ~20 min.
#   4. Solo si te atascas, mira solutions/ej41_house_robber.py.

import sys
from typing import List


# ===========================================================================
# EJ 41 — House Robber
#   `nums[i]` es el dinero guardado en la casa i, dispuestas en fila. Eres
#   un ladrón: puedes robar cualquier subconjunto de casas, pero NO puedes
#   robar dos casas adyacentes (activaría la alarma). Devuelve el máximo
#   dinero que puedes robar. Complejidad esperada: O(n) tiempo, O(1)
#   espacio.
# ---------------------------------------------------------------------------
def rob(nums: List[int]) -> int:
    if len(nums) == 0:
        return 0
    if len(nums) == 1:
        return nums[0]
    if len(nums) == 2:
        return max(nums[0],nums[1])
    accum = [n for n in nums[:3]]
    accum[2] += nums[0]
    print(nums)
    for i in range(3, len(nums)):
        temp = accum[2]
        accum[2] = max(accum[1], accum[0])+nums[i]
        accum[0] = accum[1]
        accum[1] = temp
    return max(accum[2], accum[1])


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
