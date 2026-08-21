# EJ 12 — Kth Largest Element in an Array (heap)
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej12_kth_largest.py
#   3. Cronométrate: apunta a ~15 min.
#   4. Solo si te atascas, mira solutions/ej12_kth_largest.py.

import sys
from typing import List
import heapq

# ===========================================================================
# EJ 12 — Kth Largest Element in an Array
#   Devuelve el k-ésimo elemento más grande de `nums` (k=1 es el máximo).
#   Es el k-ésimo en el orden ordenado, no el k-ésimo distinto: los
#   duplicados cuentan. Usa un heap de tamaño k para O(n log k).
# ---------------------------------------------------------------------------
def find_kth_largest(nums: List[int], k: int) -> int:
    h = []
    for n in nums:
        heapq.heappush(h, -n)
    for _ in range(k):
        r = heapq.heappop(h)*-1
    return r


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
    check(find_kth_largest([3, 2, 1, 5, 6, 4], 2) == 5, "EJ12 caso general k=2")
    check(find_kth_largest([3, 2, 3, 1, 2, 4, 5, 5, 6], 4) == 4, "EJ12 con duplicados")
    check(find_kth_largest([1], 1) == 1, "EJ12 array de un elemento")
    check(find_kth_largest([2, 1], 2) == 1, "EJ12 k es el minimo")
    check(find_kth_largest([7, 6, 5, 4, 3, 2, 1], 1) == 7, "EJ12 k=1 es el maximo")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
