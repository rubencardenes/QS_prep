# EJ 45 — Insert Interval (arrays)
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej45_insert_interval.py
#   3. Cronométrate: apunta a ~20-25 min.
#   4. Solo si te atascas, mira solutions/ej45_insert_interval.py.

import sys
from typing import List


# ===========================================================================
# EJ 45 — Insert Interval
#   `intervals` es una lista de intervalos [inicio, fin] ya ordenada por
#   inicio y sin solapamientos entre sí. Inserta `new_interval` en su
#   sitio, fusionando con los intervalos existentes si es necesario, de
#   forma que el resultado siga ordenado y sin solapamientos.
#   Complejidad esperada: O(n), un solo recorrido (no hace falta volver a
#   ordenar).
# ---------------------------------------------------------------------------
def insert(intervals: List[List[int]], new_interval: List[int]) -> List[List[int]]:
    print(f"{intervals=}, {new_interval=}")

    results = []
    for i in range(len(intervals)):
        # if new_interval has been inserted continue with the rest
        if not new_interval:
            results.append(intervals[i])
            continue
        if new_interval[1] < intervals[i][0]:
            # new_interval is lower than current without overlap, insert new interval and current forget new_interval  
            results.append(new_interval)
            results.append(intervals[i])
            new_interval = None
            continue 
        if new_interval[0] > intervals[i][1]:
            # new_interval is higher than current without overlap, insert current  
            results.append(intervals[i])
            continue
        if (new_interval[0] >= intervals[i][0] and new_interval[0] < intervals[i][1]) or (new_interval[1] >= intervals[i][0] and new_interval[1] < intervals[i][1]):
            # There is overlap, we have to merge update new interval 
            new_interval[0] = min(new_interval[0], intervals[i][0])
            new_interval[1] = max(new_interval[1], intervals[i][1])
    if new_interval:
        results.append(new_interval)

    print(f"{results=}")
    return results 


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
    check(insert([[1, 3], [6, 9]], [2, 5]) == [[1, 5], [6, 9]],
          "EJ45 se fusiona con un intervalo")
    check(insert([[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], [4, 8]) ==
          [[1, 2], [3, 10], [12, 16]], "EJ45 se fusiona con varios intervalos")
    check(insert([], [5, 7]) == [[5, 7]], "EJ45 lista de intervalos vacia")
    check(insert([[1, 5]], [2, 3]) == [[1, 5]], "EJ45 el nuevo intervalo queda contenido")
    check(insert([[1, 5]], [6, 8]) == [[1, 5], [6, 8]], "EJ45 no hay solapamiento")
    check(insert([[3, 5]], [1, 2]) == [[1, 2], [3, 5]], "EJ45 se inserta al principio")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
