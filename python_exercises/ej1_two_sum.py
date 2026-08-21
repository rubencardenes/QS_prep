# EJ 1 — Two Sum (hashmap)  [warm-up]
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej1_two_sum.py
#   3. Cronométrate: apunta a ~10 min.
#   4. Solo si te atascas, mira solutions/ej1_two_sum.py.

import sys
from typing import List


# ===========================================================================
# EJ 1 — Two Sum
#   Dado un array de enteros `nums` y un entero `target`, devuelve los
#   índices [i, j] (i != j) tales que nums[i] + nums[j] == target.
#   Se asume que existe exactamente una solución y no se puede usar el mismo
#   elemento dos veces. Complejidad esperada: O(n) tiempo, O(n) espacio.
# ---------------------------------------------------------------------------
def two_sum2(nums: List[int], target: int) -> List[int]:
    # Brute force O(n^2)
    for i in range(len(nums)):
        for j in range(i+1,len(nums)):
            if (nums[i] + nums[j] == target):
                return [i, j]
    return (i, j)

def two_sum(nums: List[int], target: int) -> List[int]:
    # With hashmap O(n)
    print(f"{nums=} {target=}")
    C = {nums[0]: 0}
    for i in range(1,len(nums)):
        if target - nums[i] in C:
            print("result: ", i, C[target - nums[i]])
            return (i, C[target - nums[i]])
        C[nums[i]] = i
    return None




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
    check(sorted(two_sum([2, 7, 11, 15], 9)) == [0, 1], "EJ1 par simple al inicio")
    check(sorted(two_sum([3, 2, 4], 6)) == [1, 2], "EJ1 par en medio del array")
    check(sorted(two_sum([3, 3], 6)) == [0, 1], "EJ1 valores duplicados")
    check(sorted(two_sum([-1, -2, -3, -4, -5], -8)) == [2, 4], "EJ1 numeros negativos")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
