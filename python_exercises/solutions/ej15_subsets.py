# EJ 15 — Subsets — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej15_subsets.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import sys
from typing import List


# ---------------------------------------------------------------------------
# EJ 15 — Subsets. Complejidad: O(2^n).
# Backtracking: en cada posición decide "incluir nums[i]" o "no incluirlo",
# guardando una copia del `path` como subconjunto válido en cada llamada.
def subsets(nums: List[int]) -> List[List[int]]:
    result: List[List[int]] = []

    def backtrack(start: int, path: List[int]) -> None:
        result.append(path[:])
        for i in range(start, len(nums)):
            path.append(nums[i])
            backtrack(i + 1, path)
            path.pop()

    backtrack(0, [])
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


def _normalize(subs: List[List[int]]) -> set:
    return {tuple(sorted(s)) for s in subs}


def main() -> None:
    result = subsets([1, 2, 3])
    expected = _normalize([[], [1], [2], [3], [1, 2], [1, 3], [2, 3], [1, 2, 3]])
    check(len(result) == 8, "EJ15 numero total de subconjuntos = 2^3")
    check(_normalize(result) == expected, "EJ15 contenido correcto para [1,2,3]")

    check(_normalize(subsets([])) == {()}, "EJ15 array vacio -> solo el subconjunto vacio")

    result2 = subsets([0])
    check(_normalize(result2) == _normalize([[], [0]]), "EJ15 un solo elemento")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
