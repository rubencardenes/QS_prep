# EJ 40 — Find Minimum in Rotated Sorted Array — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej40_find_min_rotated_array.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import sys
from typing import List


# ---------------------------------------------------------------------------
# EJ 40 — Find Minimum in Rotated Sorted Array. Complejidad: O(log n).
# Busqueda binaria comparando el elemento medio con el ultimo: si
# nums[mid] > nums[right], el minimo esta a la derecha de mid (el array
# "se rompe" en algun punto posterior); si no, el minimo esta en mid o a
# su izquierda. Se descarta la mitad que no puede contener el minimo en
# cada paso.
def find_min(nums: List[int]) -> int:
    left, right = 0, len(nums) - 1
    while left < right:
        mid = (left + right) // 2
        if nums[mid] > nums[right]:
            left = mid + 1
        else:
            right = mid
    return nums[left]


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
    check(find_min([3, 4, 5, 1, 2]) == 1, "EJ40 caso general del enunciado")
    check(find_min([4, 5, 6, 7, 0, 1, 2]) == 0, "EJ40 rotacion mas grande")
    check(find_min([11, 13, 15, 17]) == 11, "EJ40 array sin rotar")
    check(find_min([2, 1]) == 1, "EJ40 dos elementos")
    check(find_min([1]) == 1, "EJ40 un solo elemento")
    check(find_min([5, 1, 2, 3, 4]) == 1, "EJ40 rotacion de un solo paso")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
