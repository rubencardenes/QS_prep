# EJ 16 — Permutations (backtracking)
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej16_permutations.py
#   3. Cronométrate: apunta a ~15-20 min.
#   4. Solo si te atascas, mira solutions/ej16_permutations.py.

import sys
from typing import List


# ===========================================================================
# EJ 16 — Permutations
#   Dado un array `nums` de enteros distintos, devuelve todas las
#   permutaciones posibles. El orden de las permutaciones no importa.
#   Complejidad esperada: O(n!).
# ---------------------------------------------------------------------------
def permute(nums: List[int]) -> List[List[int]]:
    print(f"{nums=}")
    result = []
    def backtrack(permutation):
        if len(permutation) > len(nums):
            return
        if len(permutation) == len(nums):
            result.append(permutation)
        for n in nums:
            if n not in permutation:
                backtrack(permutation + [n])

    backtrack([])
    print(f"{result=}")

    return result

# ===========================================================================
#                        TEST HARNESS (no tocar)
# ===========================================================================
_pass = 0
_fail = 0


def check(ok: bool, name: str) -> None:
    global _pass, _fail
    _pass, _fail = (_pass + 1, _fail) if ok else (_pass, _fail + 1)
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}")


def _normalize(perms: List[List[int]]) -> set:
    return {tuple(p) for p in perms}


def main() -> None:
    result = permute([1, 2, 3])
    expected = _normalize([[1, 2, 3], [1, 3, 2], [2, 1, 3],
                            [2, 3, 1], [3, 1, 2], [3, 2, 1]])
    check(len(result) == 6, "EJ16 numero total de permutaciones = 3!")
    check(_normalize(result) == expected, "EJ16 contenido correcto para [1,2,3]")

    check(permute([1]) == [[1]], "EJ16 un solo elemento")
    check(_normalize(permute([1, 2])) == _normalize([[1, 2], [2, 1]]), "EJ16 dos elementos")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
