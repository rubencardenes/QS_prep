# EJ 11 — Product of Array Except Self (prefijos/sufijos)  [warm-up]
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej11_product_except_self.py
#   3. Cronométrate: apunta a ~15 min.
#   4. Solo si te atascas, mira solutions/ej11_product_except_self.py.

import sys
from typing import List


# ===========================================================================
# EJ 11 — Product of Array Except Self
#   Dado un array `nums`, devuelve un array `out` donde out[i] es el
#   producto de todos los elementos de `nums` excepto nums[i].
#   Prohibido usar división. Complejidad esperada: O(n) tiempo, O(1) espacio
#   extra (sin contar el array de salida).
# ---------------------------------------------------------------------------
def product_except_self(nums: List[int]) -> List[int]:
    out = [1] * len(nums)
    out_ = [1] * len(nums)
    # Using two passes 
    for i in range(1,len(nums)):
        out[i] = out[i-1]*nums[i-1]
    
    for i in range(len(nums)-2, -1, -1):
        out_[i] = out_[i+1]*nums[i+1]
        out[i] = out[i]*out_[i]

    return out

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
    check(product_except_self([1, 2, 3, 4]) == [24, 12, 8, 6], "EJ11 caso general")
    check(product_except_self([-1, 1, 0, -3, 3]) == [0, 0, 9, 0, 0], "EJ11 con un cero")
    check(product_except_self([2, 3]) == [3, 2], "EJ11 array de dos elementos")
    check(product_except_self([1, 0, 0]) == [0, 0, 0], "EJ11 con dos ceros -> todo 0")
    check(product_except_self([5]) == [1], "EJ11 array de un elemento -> producto vacio 1")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
