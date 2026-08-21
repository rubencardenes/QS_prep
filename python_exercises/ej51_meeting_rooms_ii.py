# EJ 51 — Meeting Rooms II (heap / intervalos)
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej51_meeting_rooms_ii.py
#   3. Cronométrate: apunta a ~20-25 min.
#   4. Solo si te atascas, mira solutions/ej51_meeting_rooms_ii.py.

import sys
from typing import List


# ===========================================================================
# EJ 51 — Meeting Rooms II
#   Dado un array de intervalos de reuniones `intervals` (cada uno
#   [inicio, fin]), devuelve el número mínimo de salas necesarias para
#   que todas las reuniones se puedan celebrar sin solaparse.
#   Complejidad esperada: O(n log n) tiempo. Pista: usa un min-heap con
#   las horas de fin de las reuniones en curso; al procesar cada reunión
#   (ordenadas por inicio), si la que termina antes ya ha acabado,
#   reutiliza esa sala; si no, hace falta una sala nueva.
# ---------------------------------------------------------------------------
def min_meeting_rooms(intervals: List[List[int]]) -> int:
    # TODO
    raise NotImplementedError


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
