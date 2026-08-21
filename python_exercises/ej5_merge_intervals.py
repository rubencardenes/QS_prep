# EJ 5 — Merge Intervals (ordenar + barrido)
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej5_merge_intervals.py
#   3. Cronométrate: apunta a ~15-20 min.
#   4. Solo si te atascas, mira solutions/ej5_merge_intervals.py.

import sys
from typing import List


# ===========================================================================
# EJ 5 — Merge Intervals
#   Dada una lista de intervalos [inicio, fin] (posiblemente solapados),
#   fusiona todos los solapados y devuelve la lista resultante, ordenada
#   por inicio. Complejidad esperada: O(n log n).
# ---------------------------------------------------------------------------
def merge(intervals: List[List[int]]) -> List[List[int]]:
    if not intervals:
        return intervals 
    # First sort be the left
    i_sorted = sorted(intervals, key = lambda p: p[0])
    # Now go from the first to the last comparing the right of i with the left of i+1
    i_final = []
    l = i_sorted[0][0]
    print("i_sorted: ", i_sorted)
    for i in range(1, len(i_sorted)):
        r = i_sorted[i-1][1]
        if i_sorted[i-1][1] >= i_sorted[i][0]:
            # There is overlap between i-1 and i
            r = max(i_sorted[i][1], i_sorted[i-1][1])
        else:
            # Reset the left 
            i_final.append([l,r])
            l = i_sorted[i][0]
            r = i_sorted[i][1]
    i_final.append([l,r])
    print("i_final ", i_final)
    return i_final


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
    check(merge([[1, 3], [2, 6], [8, 10], [15, 18]]) == [[1, 6], [8, 10], [15, 18]],
          "EJ5 solapamientos parciales")
    check(merge([[1, 4], [4, 5]]) == [[1, 5]], "EJ5 intervalos contiguos se fusionan")
    check(merge([[1, 4], [0, 4]]) == [[0, 4]], "EJ5 entrada no ordenada por inicio")
    check(merge([]) == [], "EJ5 lista vacia")
    check(merge([[1, 4], [2, 3]]) == [[1, 4]], "EJ5 intervalo contenido en otro")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
