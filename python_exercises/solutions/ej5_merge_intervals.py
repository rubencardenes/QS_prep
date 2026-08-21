# EJ 5 — Merge Intervals (ordenar + barrido) — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej5_merge_intervals.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import sys
from typing import List


# ---------------------------------------------------------------------------
# EJ 5 — Merge Intervals. Complejidad: O(n log n) por el sort.
# Tras ordenar por inicio, un intervalo se fusiona con el último acumulado
# si su inicio no supera el fin del acumulado; si no, se añade uno nuevo.
def merge(intervals: List[List[int]]) -> List[List[int]]:
    if not intervals:
        return []
    intervals = sorted(intervals, key=lambda iv: iv[0])
    merged = [intervals[0][:]]
    for start, end in intervals[1:]:
        if start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged


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
