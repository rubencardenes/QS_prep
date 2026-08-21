# EJ 52 — Find Median from Data Stream (diseño: dos heaps)  [dificil]
#
# CÓMO USARLO
#   1. Rellena los métodos marcados con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej52_find_median_data_stream.py
#   3. Cronométrate: apunta a ~25-30 min.
#   4. Solo si te atascas, mira solutions/ej52_find_median_data_stream.py.

import sys


# ===========================================================================
# EJ 52 — Find Median from Data Stream
#   Implementa una estructura que recibe números uno a uno y puede
#   devolver la mediana de todos los números vistos hasta el momento.
#     add_num(num)   -> añade un número al flujo.
#     find_median()  -> devuelve la mediana actual (float).
#   Complejidad esperada: add_num en O(log n), find_median en O(1).
#   Pista: mantén dos heaps balanceados — un max-heap con la mitad
#   inferior de los números y un min-heap con la mitad superior (en
#   Python, el max-heap se simula con un min-heap de valores negados).
# ---------------------------------------------------------------------------
import heapq

class MedianFinder:
    def __init__(self):
        self.lower = [] # Max heap
        self.higher = [] # Min heap

    def add_num(self, num: int) -> None:
        if len(self.lower) == 0 and len(self.higher) == 0:
            heapq.heappush(self.lower, -num)
        else:
            if num < self.lower[0]*-1:
                # Add to lower
                heapq.heappush(self.lower, -num)
            else:
                # Add to higher
                heapq.heappush(self.higher, num)
            # Balance heaps
            if len(self.lower) - len(self.higher) > 1:
                num = heapq.heappop(self.lower)*(-1)
                heapq.heappush(self.higher, num)
            if len(self.higher) - len(self.lower) > 1:
                num = heapq.heappop(self.higher)
                heapq.heappush(self.lower, -num)
        print(self.lower, " -- ", self.higher)

    def find_median(self) -> float:
        if len(self.lower) == 0 and len(self.lower) == 0:
            return 0 
        if len(self.lower) < len(self.higher):
            return self.higher[0]
        elif len(self.lower) > len(self.higher):
            return -self.lower[0]
        else:
            return 0.5 * (self.higher[0] - self.lower[0])

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
