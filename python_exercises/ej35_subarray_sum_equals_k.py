# EJ 35 — Subarray Sum Equals K (prefix sum + hashmap)
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej35_subarray_sum_equals_k.py
#   3. Cronométrate: apunta a ~20-25 min.
#   4. Solo si te atascas, mira solutions/ej35_subarray_sum_equals_k.py.

import sys
from typing import List


# ===========================================================================
# EJ 35 — Subarray Sum Equals K
#   Dado un array `nums` y un entero `k`, devuelve el número total de
#   subarrays CONTIGUOS cuya suma sea exactamente `k`. `nums` puede tener
#   negativos. Complejidad esperada: O(n) tiempo usando sumas prefijas y
#   un hashmap (NO O(n^2) probando todos los subarrays).
# ---------------------------------------------------------------------------
def subarray_sum(nums: List[int], k: int) -> int:
    # Brute force 
    result = 0
    for i in range(len(nums)):
        sum = nums[i]
        if sum == k:
            result += 1
        for j in range(i+1, len(nums)):
            sum += nums[j]
            if sum == k:
                result += 1
    return result 

def subarray_sum2(nums: List[int], k: int) -> int:
    result = 0
    accum = 0
    start = 0
    for i, n in enumerate(nums):
        print(f"{i=} {n=} {start=}")
        accum = accum + n
        if accum > k:
            accum -= nums[start]
            start += 1
        if accum == k:
            accum -= nums[start]
            start += 1
            result += 1
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
    check(subarray_sum([1, 1, 1], 2) == 2, "EJ35 caso general del enunciado")
    check(subarray_sum([1, 2, 3], 3) == 2, "EJ35 dos subarrays distintos suman 3")
    check(subarray_sum([1, -1, 0], 0) == 3, "EJ35 con negativos y ceros")
    check(subarray_sum([3, 4, 7, 2, -3, 1, 4, 2], 7) == 4, "EJ35 array mas largo")
    check(subarray_sum([1], 0) == 0, "EJ35 sin ningun subarray valido")
    check(subarray_sum([], 0) == 0, "EJ35 array vacio")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
