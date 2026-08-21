# EJ 11 — Product of Array Except Self — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej11_product_except_self.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import sys
from typing import List


# ---------------------------------------------------------------------------
# EJ 11 — Product of Array Except Self. Complejidad: O(n) tiempo, O(1) extra.
# Dos pasadas: out[i] guarda primero el producto de todo lo anterior a i
# (prefijo), luego se multiplica in-place por el producto de todo lo
# posterior a i (sufijo), calculado en la segunda pasada.
def product_except_self(nums: List[int]) -> List[int]:
    n = len(nums)
    out = [1] * n
    prefix = 1
    for i in range(n):
        out[i] = prefix
        prefix *= nums[i]
    suffix = 1
    for i in range(n - 1, -1, -1):
        out[i] *= suffix
        suffix *= nums[i]
    return out


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
    check(product_except_self([1, 2, 3, 4]) == [24, 12, 8, 6], "EJ11 caso general")
    check(product_except_self([-1, 1, 0, -3, 3]) == [0, 0, 9, 0, 0], "EJ11 con un cero")
    check(product_except_self([2, 3]) == [3, 2], "EJ11 array de dos elementos")
    check(product_except_self([1, 0, 0]) == [0, 0, 0], "EJ11 con dos ceros -> todo 0")
    check(product_except_self([5]) == [1], "EJ11 array de un elemento -> producto vacio 1")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
