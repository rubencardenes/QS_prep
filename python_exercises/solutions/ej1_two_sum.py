# EJ 1 — Two Sum (hashmap) — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej1_two_sum.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import sys
from typing import List


# ---------------------------------------------------------------------------
# EJ 1 — Two Sum. Complejidad: O(n) tiempo, O(n) espacio.
# Un solo paso: por cada número, comprueba si su complemento ya se ha visto.
def two_sum(nums: List[int], target: int) -> List[int]:
    seen = {}
    for i, n in enumerate(nums):
        complement = target - n
        if complement in seen:
            return [seen[complement], i]
        seen[n] = i
    raise ValueError("No existe solucion")


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
    check(sorted(two_sum([2, 7, 11, 15], 9)) == [0, 1], "EJ1 par simple al inicio")
    check(sorted(two_sum([3, 2, 4], 6)) == [1, 2], "EJ1 par en medio del array")
    check(sorted(two_sum([3, 3], 6)) == [0, 1], "EJ1 valores duplicados")
    check(sorted(two_sum([-1, -2, -3, -4, -5], -8)) == [2, 4], "EJ1 numeros negativos")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
