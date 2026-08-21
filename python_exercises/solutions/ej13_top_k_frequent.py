# EJ 13 — Top K Frequent Elements — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej13_top_k_frequent.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import sys
from collections import Counter
from typing import List


# ---------------------------------------------------------------------------
# EJ 13 — Top K Frequent Elements. Complejidad: O(n) con bucket sort.
# buckets[f] guarda los números que aparecen exactamente f veces (f va de
# 0 a n como máximo). Se recorren los buckets de mayor a menor frecuencia.
def top_k_frequent(nums: List[int], k: int) -> List[int]:
    counts = Counter(nums)
    buckets: List[List[int]] = [[] for _ in range(len(nums) + 1)]
    for num, freq in counts.items():
        buckets[freq].append(num)

    result = []
    for freq in range(len(buckets) - 1, 0, -1):
        for num in buckets[freq]:
            result.append(num)
            if len(result) == k:
                return result
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
    check(set(top_k_frequent([1, 1, 1, 2, 2, 3], 2)) == {1, 2}, "EJ13 caso general k=2")
    check(set(top_k_frequent([1], 1)) == {1}, "EJ13 un solo elemento")
    check(len(top_k_frequent([1, 2, 3, 4], 4)) == 4, "EJ13 k igual al numero de distintos")
    check(set(top_k_frequent([4, 4, 4, 5, 5, 6], 1)) == {4}, "EJ13 el mas frecuente claro")
    check(set(top_k_frequent([7, 7, 8, 8, 9], 2)) == {7, 8}, "EJ13 empate entre dos")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
