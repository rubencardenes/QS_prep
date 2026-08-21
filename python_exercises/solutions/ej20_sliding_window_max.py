# EJ 20 — Sliding Window Maximum — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej20_sliding_window_max.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import sys
from collections import deque
from typing import List


# ---------------------------------------------------------------------------
# EJ 20 — Sliding Window Maximum. Complejidad: O(n).
# Deque monótona decreciente de índices: antes de añadir el índice actual,
# se descartan por detrás todos los índices cuyo valor sea <= al actual (ya
# no podrán ser el máximo de ninguna ventana futura); el máximo de la
# ventana es siempre el valor del índice al frente de la deque, expulsando
# ese índice cuando cae fuera de la ventana.
def max_sliding_window(nums: List[int], k: int) -> List[int]:
    dq: deque = deque()  # indices, valores decrecientes
    result = []
    for i, n in enumerate(nums):
        while dq and nums[dq[-1]] <= n:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()
        if i >= k - 1:
            result.append(nums[dq[0]])
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
    check(max_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 3) == [3, 3, 5, 5, 6, 7],
          "EJ20 caso general k=3")
    check(max_sliding_window([1], 1) == [1], "EJ20 ventana igual al array")
    check(max_sliding_window([9, 11], 2) == [11], "EJ20 array de dos elementos")
    check(max_sliding_window([4, -2], 2) == [4], "EJ20 con negativos")
    check(max_sliding_window([1, 2, 3, 4, 5], 1) == [1, 2, 3, 4, 5], "EJ20 ventana de tamaño 1")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
