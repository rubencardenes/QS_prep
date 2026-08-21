# EJ 45 — Insert Interval — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej45_insert_interval.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import sys
from typing import List


# ---------------------------------------------------------------------------
# EJ 45 — Insert Interval. Complejidad: O(n) tiempo, O(n) espacio para el
# resultado.
# Tres fases en un solo recorrido: (1) copiar tal cual los intervalos que
# terminan antes de que empiece `new_interval`; (2) fusionar con
# `new_interval` todos los que se solapan con el (ampliando sus limites);
# (3) copiar tal cual el resto, que empiezan despues de que termine el
# intervalo fusionado.
def insert(intervals: List[List[int]], new_interval: List[int]) -> List[List[int]]:
    result = []
    i = 0
    n = len(intervals)
    start, end = new_interval

    while i < n and intervals[i][1] < start:
        result.append(intervals[i])
        i += 1

    while i < n and intervals[i][0] <= end:
        start = min(start, intervals[i][0])
        end = max(end, intervals[i][1])
        i += 1
    result.append([start, end])

    while i < n:
        result.append(intervals[i])
        i += 1

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
