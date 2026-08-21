# EJ 50 — Combination Sum — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej50_combination_sum.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import sys
from typing import List


def normalize(combos: List[List[int]]) -> List[List[int]]:
    """Ordena cada combinacion y luego la lista de combinaciones, para
    poder comparar resultados sin importar el orden en que se generen."""
    return sorted(sorted(c) for c in combos)


# ---------------------------------------------------------------------------
# EJ 50 — Combination Sum. Complejidad: O(2^n) en el peor caso (backtracking
# con poda).
# Ordenamos `candidates` para poder cortar la búsqueda en cuanto un
# candidato ya supera lo que queda de `target` (el resto solo pueden ser
# mayores o iguales). En cada llamada probamos incluir candidates[i] las
# veces que haga falta, avanzando el índice de inicio solo hacia
# adelante (nunca hacia atrás) para no generar la misma combinación en
# distinto orden.
def combination_sum(candidates: List[int], target: int) -> List[List[int]]:
    candidates = sorted(candidates)
    result: List[List[int]] = []
    path: List[int] = []

    def backtrack(start: int, remaining: int) -> None:
        if remaining == 0:
            result.append(path[:])
            return
        for i in range(start, len(candidates)):
            candidate = candidates[i]
            if candidate > remaining:
                break
            path.append(candidate)
            backtrack(i, remaining - candidate)
            path.pop()

    backtrack(0, target)
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
    check(normalize(combination_sum([2, 3, 6, 7], 7)) ==
          normalize([[2, 2, 3], [7]]), "EJ50 dos combinaciones")
    check(normalize(combination_sum([2, 3, 5], 8)) ==
          normalize([[2, 2, 2, 2], [2, 3, 3], [3, 5]]), "EJ50 tres combinaciones")
    check(combination_sum([2], 1) == [], "EJ50 sin solucion posible")
    check(normalize(combination_sum([1], 2)) == normalize([[1, 1]]),
          "EJ50 unico candidato repetido")
    check(combination_sum([5], 3) == [], "EJ50 candidato mayor que target")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
