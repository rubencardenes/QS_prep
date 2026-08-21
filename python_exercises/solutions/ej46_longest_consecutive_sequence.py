# EJ 46 — Longest Consecutive Sequence — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej46_longest_consecutive_sequence.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import sys
from typing import List


# ---------------------------------------------------------------------------
# EJ 46 — Longest Consecutive Sequence. Complejidad: O(n) tiempo, O(n)
# espacio.
# Metemos todos los valores en un set. Para cada número que sea el inicio
# de una secuencia (es decir, num - 1 no está en el set), contamos hacia
# arriba mientras num + 1, num + 2, ... existan en el set. Como cada número
# solo se recorre una vez como parte de su secuencia, el coste total es
# lineal aunque haya un bucle anidado.
def longest_consecutive(nums: List[int]) -> int:
    num_set = set(nums)
    best = 0
    for num in num_set:
        if num - 1 in num_set:
            continue
        length = 1
        current = num
        while current + 1 in num_set:
            current += 1
            length += 1
        best = max(best, length)
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
    check(longest_consecutive([100, 4, 200, 1, 3, 2]) == 4,
          "EJ46 secuencia 1-2-3-4")
    check(longest_consecutive([]) == 0, "EJ46 array vacio")
    check(longest_consecutive([1, 2, 0, 1]) == 3, "EJ46 con duplicados")
    check(longest_consecutive([9, 1, 4, 7, 3, -1, 0, 5, 8, -1, 6]) == 7,
          "EJ46 secuencia larga con negativos")
    check(longest_consecutive([5]) == 1, "EJ46 un solo elemento")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
