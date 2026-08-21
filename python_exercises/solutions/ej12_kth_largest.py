# EJ 12 — Kth Largest Element in an Array — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej12_kth_largest.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import heapq
import sys
from typing import List


# ---------------------------------------------------------------------------
# EJ 12 — Kth Largest Element. Complejidad: O(n log k).
# Mantiene un min-heap de tamaño k: al final, el tope del heap (el mínimo
# de los k mayores vistos) es el k-ésimo más grande.
def find_kth_largest(nums: List[int], k: int) -> int:
    heap = []
    for n in nums:
        heapq.heappush(heap, n)
        if len(heap) > k:
            heapq.heappop(heap)
    return heap[0]


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
    check(find_kth_largest([3, 2, 1, 5, 6, 4], 2) == 5, "EJ12 caso general k=2")
    check(find_kth_largest([3, 2, 3, 1, 2, 4, 5, 5, 6], 4) == 4, "EJ12 con duplicados")
    check(find_kth_largest([1], 1) == 1, "EJ12 array de un elemento")
    check(find_kth_largest([2, 1], 2) == 1, "EJ12 k es el minimo")
    check(find_kth_largest([7, 6, 5, 4, 3, 2, 1], 1) == 7, "EJ12 k=1 es el maximo")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
