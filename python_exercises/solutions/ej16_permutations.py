# EJ 16 — Permutations — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej16_permutations.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import sys
from typing import List


# ---------------------------------------------------------------------------
# EJ 16 — Permutations. Complejidad: O(n!).
# Backtracking: en cada paso elige uno de los elementos restantes, lo añade
# al `path` y recurre con el resto; al agotar `remaining` guarda el `path`.
def permute(nums: List[int]) -> List[List[int]]:
    result: List[List[int]] = []

    def backtrack(path: List[int], remaining: List[int]) -> None:
        if not remaining:
            result.append(path[:])
            return
        for i in range(len(remaining)):
            path.append(remaining[i])
            backtrack(path, remaining[:i] + remaining[i + 1:])
            path.pop()

    backtrack([], nums)
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
