# EJ 37 — Single Number — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej37_single_number.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import sys
from typing import List


# ---------------------------------------------------------------------------
# EJ 37 — Single Number. Complejidad: O(n) tiempo, O(1) espacio.
# XOR de todos los numeros: cada par igual se cancela (a^a=0) y el orden
# no importa (XOR es conmutativo y asociativo), asi que al final solo
# queda el numero que aparecia una unica vez (x^0=x).
def single_number(nums: List[int]) -> int:
    result = 0
    for n in nums:
        result ^= n
    return result


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
    check(single_number([2, 2, 1]) == 1, "EJ37 caso general del enunciado")
    check(single_number([4, 1, 2, 1, 2]) == 4, "EJ37 el unico esta al principio")
    check(single_number([1]) == 1, "EJ37 un solo elemento")
    check(single_number([7, 3, 7]) == 3, "EJ37 el unico esta en medio")
    check(single_number([-1, -1, -2]) == -2, "EJ37 con negativos")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
