# EJ 50 — Combination Sum (backtracking)
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej50_combination_sum.py
#   3. Cronométrate: apunta a ~20-25 min.
#   4. Solo si te atascas, mira solutions/ej50_combination_sum.py.

import sys
from typing import List


def normalize(combos: List[List[int]]) -> List[List[int]]:
    """Ordena cada combinacion y luego la lista de combinaciones, para
    poder comparar resultados sin importar el orden en que se generen."""
    return sorted(sorted(c) for c in combos)


# ===========================================================================
# EJ 50 — Combination Sum
#   Dado un array de enteros positivos distintos `candidates` y un
#   entero `target`, devuelve todas las combinaciones únicas de
#   `candidates` cuya suma sea exactamente `target`. El mismo número se
#   puede elegir varias veces (repetición ilimitada).
#   Complejidad esperada: exponencial en el peor caso (es backtracking),
#   pero se poda el árbol de búsqueda en cuanto la suma parcial supera
#   `target`. Pista: ordena `candidates` y, en cada paso, solo avanza el
#   índice de inicio hacia adelante o mantente en el mismo índice (para
#   permitir repetición) — nunca retrocedas, así evitas duplicados.
# ---------------------------------------------------------------------------
def combination_sum(candidates: List[int], target: int) -> List[List[int]]:
    if len(candidates) == 0:
        return [] 
    candidates = sorted(candidates)
    print(f"{candidates} {target=}")
    result = []
    def backtrack(combination, i):
        #print(f"{combination=}")
        s = sum(combination) 
        if candidates[i] > target or s > target:
            return 
        if s == target:
            result.append(combination)
            return 
        for j in range(i,len(candidates)):
            backtrack(combination + [candidates[j]], j)
    
    backtrack([],0)
    print(f"{result}")
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
