# EJ 6 — Search in Rotated Sorted Array — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej6_search_rotated.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import sys
from typing import List


# ---------------------------------------------------------------------------
# EJ 6 — Search in Rotated Sorted Array. Complejidad: O(log n).
# En cada paso, al menos una mitad [lo..mid] o [mid..hi] está ordenada;
# se detecta cuál lo está y se decide en qué mitad seguir buscando.
def search(nums: List[int], target: int) -> int:
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[lo] <= nums[mid]:
            if nums[lo] <= target < nums[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:
            if nums[mid] < target <= nums[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return -1


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
    check(search([4, 5, 6, 7, 0, 1, 2], 0) == 4, "EJ6 target en el lado rotado")
    check(search([4, 5, 6, 7, 0, 1, 2], 3) == -1, "EJ6 target ausente")
    check(search([1], 0) == -1, "EJ6 array de un elemento sin match")
    check(search([1], 1) == 0, "EJ6 array de un elemento con match")
    check(search([5, 1, 3], 5) == 0, "EJ6 target justo en el pivote")
    check(search([], 5) == -1, "EJ6 array vacio")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
