# EJ 19 — Course Schedule (orden topologico / deteccion de ciclos)
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej19_course_schedule.py
#   3. Cronométrate: apunta a ~20-25 min.
#   4. Solo si te atascas, mira solutions/ej19_course_schedule.py.

import sys
from typing import List
from dataclasses import dataclass


# ===========================================================================
# EJ 19 — Course Schedule
#   Hay `num_courses` cursos, numerados de 0 a num_courses-1. `prerequisites`
#   es una lista de pares [a, b] que significan "para cursar a hace falta
#   haber cursado antes b". Devuelve True si es posible cursar todos los
#   cursos (es decir, si el grafo de dependencias no tiene ciclos).
#   Complejidad esperada: O(V + E).
# ---------------------------------------------------------------------------
@dataclass 
class Node:
    val = 0
    next = None

def can_finish(num_courses: int, prerequisites: List[List[int]]) -> bool:
    # So we have to traverse the graph 
    visited = [x for x in range(num_courses)]

    graph = [Node() for val in range(num_courses)]
    # Construct graph 
    for el in prerequisites:
        graph[el[0]].val = el[0]
        graph[el[1]].val = el[1]
        graph[el[0]].next = graph[el[1]]

    i = 0
    root = graph[0]
    result = [root.val]
    while i < num_courses:
        if root.next is not None:
            node = root.next
            result.append(node.val)
        i += 1
    print(f"prerequisites {prerequisites}" )
    print(f"result {result}")
    return False


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
