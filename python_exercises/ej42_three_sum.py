# EJ 42 — 3Sum (ordenar + dos punteros)
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej42_three_sum.py
#   3. Cronométrate: apunta a ~25 min.
#   4. Solo si te atascas, mira solutions/ej42_three_sum.py.

import sys
from typing import List


# ===========================================================================
# EJ 42 — 3Sum
#   Dado un array `nums`, devuelve TODOS los tríos [a, b, c] de índices
#   distintos tales que a + b + c == 0, sin tríos duplicados (por valor,
#   no por índice). El orden de los tríos y de los valores dentro de cada
#   trío no importa. Complejidad esperada: O(n^2) — ordena el array y usa
#   dos punteros para cada elemento fijo (NO fuerza bruta O(n^3)).
# ---------------------------------------------------------------------------
def three_sum(nums: List[int]) -> List[List[int]]:
    nums = sorted(nums)
    print(f"{nums=}")
    n = len(nums)
    result = []
    for i in range(n - 2):
        if i > 0 and nums[i] == nums[i - 1]:
            continue
        # When nums are positive, there is no way to find 
        # more number suming up to zero:
        if nums[i] > 0:
            break
        left, right = i + 1, n - 1
        while left < right:
            total = nums[i] + nums[left] + nums[right]
            if total < 0:
                left += 1
            elif total > 0:
                right -= 1
            else:
                result.append([nums[i], nums[left], nums[right]])
                left += 1
                right -= 1
                while left < right and nums[left] == nums[left - 1]:
                    left += 1
                while left < right and nums[right] == nums[right + 1]:
                    right -= 1
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


def normalize(triplets: List[List[int]]):
    """Convierte la lista de trios en un conjunto de tuplas ordenadas,
    para comparar resultados sin importar el orden."""
    return sorted(tuple(sorted(t)) for t in triplets)


def main() -> None:
    check(normalize(three_sum([-1, 0, 1, 2, -1, -4])) == normalize([[-1, -1, 2], [-1, 0, 1]]),
          "EJ42 caso general del enunciado")
    check(three_sum([]) == [], "EJ42 array vacio")
    check(three_sum([0, 1, 1]) == [], "EJ42 sin ningun trio valido")
    check(normalize(three_sum([0, 0, 0])) == normalize([[0, 0, 0]]), "EJ42 trio de ceros")
    check(normalize(three_sum([0, 0, 0, 0])) == normalize([[0, 0, 0]]),
          "EJ42 deduplica trios repetidos")
    check(normalize(three_sum([-2, 0, 1, 1, 2])) == normalize([[-2, 0, 2], [-2, 1, 1]]),
          "EJ42 varios trios validos")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
