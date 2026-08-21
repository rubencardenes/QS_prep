# EJ 46 — Longest Consecutive Sequence (hashmap/set)
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej46_longest_consecutive_sequence.py
#   3. Cronométrate: apunta a ~15-20 min.
#   4. Solo si te atascas, mira solutions/ej46_longest_consecutive_sequence.py.

import sys
from typing import List


# ===========================================================================
# EJ 46 — Longest Consecutive Sequence
#   Dado un array de enteros sin ordenar `nums`, devuelve la longitud de la
#   secuencia más larga de enteros consecutivos (no hace falta que sean
#   consecutivos en el array, solo como valores: p.ej. 3, 4, 5).
#   Complejidad esperada: O(n) tiempo. Pista: usa un set para O(1) lookups y
#   arranca a contar solo desde los números que son "inicio" de secuencia
#   (aquellos cuyo n-1 no está en el set).
# ---------------------------------------------------------------------------
def longest_consecutive(nums: List[int]) -> int:
    if len(nums) == 0:
        return 0
    Lmax = 1
    L = 1
    nums = sorted(nums)
    print(f"{nums=}")
    for i in range(1, len(nums)):
        if nums[i] == nums[i-1]:
            continue
        if nums[i] - 1 == nums[i-1]:
            L += 1
            Lmax = max(L, Lmax)
        else:
            L = 1
    print(f"{Lmax=}")
    return Lmax

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
