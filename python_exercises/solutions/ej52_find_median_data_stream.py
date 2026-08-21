# EJ 52 — Find Median from Data Stream — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej52_find_median_data_stream.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import heapq
import sys


# ---------------------------------------------------------------------------
# EJ 52 — Find Median from Data Stream. Complejidad: O(log n) por add_num,
# O(1) por find_median.
# `lo` es un max-heap (min-heap de valores negados) con la mitad inferior
# de los números; `hi` es un min-heap con la mitad superior. Mantenemos
# el invariante len(lo) == len(hi) o len(lo) == len(hi) + 1. Al insertar,
# siempre metemos primero en `lo` y empujamos su máximo hacia `hi`; si
# `hi` se queda con más elementos que `lo`, devolvemos uno a `lo`. Así
# `lo` nunca tiene menos elementos que `hi`, y como mucho uno más.
class MedianFinder:
    def __init__(self):
        self.lo: list = []  # max-heap (negado)
        self.hi: list = []  # min-heap

    def add_num(self, num: int) -> None:
        heapq.heappush(self.lo, -num)
        heapq.heappush(self.hi, -heapq.heappop(self.lo))
        if len(self.hi) > len(self.lo):
            heapq.heappush(self.lo, -heapq.heappop(self.hi))

    def find_median(self) -> float:
        if len(self.lo) > len(self.hi):
            return float(-self.lo[0])
        return (-self.lo[0] + self.hi[0]) / 2.0


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
    mf = MedianFinder()
    mf.add_num(1)
    mf.add_num(2)
    check(mf.find_median() == 1.5, "EJ52 mediana con dos elementos")
    mf.add_num(3)
    check(mf.find_median() == 2, "EJ52 mediana con tres elementos")

    mf2 = MedianFinder()
    mf2.add_num(5)
    check(mf2.find_median() == 5, "EJ52 mediana con un elemento")
    mf2.add_num(1)
    check(mf2.find_median() == 3.0, "EJ52 mediana tras rebalancear")
    mf2.add_num(3)
    check(mf2.find_median() == 3, "EJ52 mediana con tres elementos ordenados")

    mf3 = MedianFinder()
    for n in [6, 10, 2, 6, 5]:
        mf3.add_num(n)
    check(mf3.find_median() == 6, "EJ52 mediana con cinco elementos")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
