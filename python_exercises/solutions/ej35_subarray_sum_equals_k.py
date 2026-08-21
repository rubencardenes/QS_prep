# EJ 35 — Subarray Sum Equals K — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej35_subarray_sum_equals_k.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import sys
from collections import defaultdict
from typing import List


# ---------------------------------------------------------------------------
# EJ 35 — Subarray Sum Equals K. Complejidad: O(n) tiempo, O(n) espacio.
# Se recorre el array acumulando la suma prefija `running`. Si en algun
# punto anterior la suma prefija fue (running - k), el tramo entre medio
# suma exactamente k. Un hashmap cuenta cuantas veces se ha visto cada
# suma prefija (con {0: 1} para cubrir subarrays que empiezan en el
# indice 0).
def subarray_sum(nums: List[int], k: int) -> int:
    counts = defaultdict(int)
    counts[0] = 1
    running = 0
    total = 0
    for n in nums:
        running += n
        total += counts[running - k]
        counts[running] += 1
    return total


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
