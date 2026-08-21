# EJ 51 — Meeting Rooms II — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej51_meeting_rooms_ii.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import heapq
import sys
from typing import List


# ---------------------------------------------------------------------------
# EJ 51 — Meeting Rooms II. Complejidad: O(n log n) tiempo, O(n) espacio.
# Ordenamos las reuniones por hora de inicio. Mantenemos un min-heap con
# las horas de fin de las salas ocupadas. Para cada reunión: si la sala
# que libera antes (heap[0]) ya terminó a tiempo (su fin <= el inicio de
# la reunión actual), la reutilizamos (pop + push); si no, necesitamos
# una sala nueva (push sin pop). El tamaño máximo que alcanza el heap es
# el número de salas necesarias.
def min_meeting_rooms(intervals: List[List[int]]) -> int:
    if not intervals:
        return 0

    intervals = sorted(intervals, key=lambda pair: pair[0])
    end_times: List[int] = []
    rooms = 0

    for start, end in intervals:
        if end_times and end_times[0] <= start:
            heapq.heapreplace(end_times, end)
        else:
            heapq.heappush(end_times, end)
            rooms = max(rooms, len(end_times))

    return rooms


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
    check(min_meeting_rooms([[0, 30], [5, 10], [15, 20]]) == 2,
          "EJ51 tres reuniones, dos salas")
    check(min_meeting_rooms([[7, 10], [2, 4]]) == 1,
          "EJ51 reuniones sin solapamiento")
    check(min_meeting_rooms([]) == 0, "EJ51 sin reuniones")
    check(min_meeting_rooms([[1, 5], [8, 9], [8, 9]]) == 2,
          "EJ51 dos reuniones identicas a la vez")
    check(min_meeting_rooms(
        [[1, 10], [2, 7], [3, 19], [8, 12], [10, 20], [11, 30]]) == 4,
        "EJ51 muchos solapamientos")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
