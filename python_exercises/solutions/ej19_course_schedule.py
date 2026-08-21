# EJ 19 — Course Schedule — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej19_course_schedule.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import sys
from collections import deque
from typing import List


# ---------------------------------------------------------------------------
# EJ 19 — Course Schedule. Complejidad: O(V + E).
# Orden topológico de Kahn: se van "cursando" los nodos sin dependencias
# pendientes (in_degree 0); si al final no se han visitado todos los
# cursos, es porque queda un ciclo que ninguno puede romper.
def can_finish(num_courses: int, prerequisites: List[List[int]]) -> bool:
    graph: List[List[int]] = [[] for _ in range(num_courses)]
    in_degree = [0] * num_courses
    for a, b in prerequisites:
        graph[b].append(a)
        in_degree[a] += 1

    queue = deque(c for c in range(num_courses) if in_degree[c] == 0)
    visited = 0
    while queue:
        course = queue.popleft()
        visited += 1
        for nxt in graph[course]:
            in_degree[nxt] -= 1
            if in_degree[nxt] == 0:
                queue.append(nxt)

    return visited == num_courses


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
    check(can_finish(2, [[1, 0]]) is True, "EJ19 sin ciclos, dos cursos")
    check(can_finish(2, [[1, 0], [0, 1]]) is False, "EJ19 ciclo directo entre dos cursos")
    check(can_finish(4, [[1, 0], [2, 0], [3, 1], [3, 2]]) is True,
          "EJ19 grafo en diamante sin ciclos")
    check(can_finish(3, [[0, 1], [1, 2], [2, 0]]) is False, "EJ19 ciclo de longitud 3")
    check(can_finish(1, []) is True, "EJ19 un curso sin prerequisitos")
    check(can_finish(5, []) is True, "EJ19 varios cursos sin prerequisitos")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
