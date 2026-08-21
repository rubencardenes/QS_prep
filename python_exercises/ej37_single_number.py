# EJ 37 — Single Number (bit manipulation: XOR)  [warm-up]
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej37_single_number.py
#   3. Cronométrate: apunta a ~10-15 min.
#   4. Solo si te atascas, mira solutions/ej37_single_number.py.

import sys
from typing import List


# ===========================================================================
# EJ 37 — Single Number
#   En `nums`, todos los elementos aparecen exactamente dos veces excepto
#   uno, que aparece una sola vez. Encuéntralo. Complejidad esperada:
#   O(n) tiempo, O(1) espacio extra (nada de sets/dicts: usa la operación
#   XOR y sus propiedades: a^a=0, a^0=a, es conmutativa y asociativa).
# ---------------------------------------------------------------------------
def single_number(nums: List[int]) -> int:
    res = 0
    for n in nums:
        res = res^n
    return res


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
    check(single_number([2, 2, 1]) == 1, "EJ37 caso general del enunciado")
    check(single_number([4, 1, 2, 1, 2]) == 4, "EJ37 el unico esta al principio")
    check(single_number([1]) == 1, "EJ37 un solo elemento")
    check(single_number([7, 3, 7]) == 3, "EJ37 el unico esta en medio")
    check(single_number([-1, -1, -2]) == -2, "EJ37 con negativos")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
