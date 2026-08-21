# EJ 23 — Redundant Connection — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej23_redundant_connection.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import sys
from typing import List


# ---------------------------------------------------------------------------
# EJ 23 — Redundant Connection. Complejidad: O(n * alpha(n)) ~ O(n).
# Union-Find con compresion de caminos y union por rango: se procesan las
# aristas en orden y se intenta unir sus dos extremos. La primera arista
# cuyos extremos ya pertenecen al mismo conjunto es la que cierra el ciclo,
# y por tanto la respuesta (por construccion, es la ultima que cumpliria
# esa condicion si se procesaran en orden).
def find_redundant_connection(edges: List[List[int]]) -> List[int]:
    n = len(edges)
    parent = list(range(n + 1))
    rank = [0] * (n + 1)

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> bool:
        ra, rb = find(a), find(b)
        if ra == rb:
            return False
        if rank[ra] < rank[rb]:
            ra, rb = rb, ra
        parent[rb] = ra
        if rank[ra] == rank[rb]:
            rank[ra] += 1
        return True

    for u, v in edges:
        if not union(u, v):
            return [u, v]
    raise ValueError("no redundant edge found")


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
    check(find_redundant_connection([[1, 2], [1, 3], [2, 3]]) == [2, 3],
          "EJ23 ciclo simple de 3 nodos")

    check(find_redundant_connection([[1, 2], [2, 3], [3, 4], [1, 4], [1, 5]]) == [1, 4],
          "EJ23 ciclo de 4 nodos con una rama extra")

    check(find_redundant_connection([[1, 2], [2, 3], [1, 3]]) == [1, 3],
          "EJ23 la arista redundante es la ultima en cerrar el ciclo")

    check(find_redundant_connection([[1, 4], [3, 4], [1, 3], [1, 2]]) == [1, 3],
          "EJ23 arista redundante no es la ultima de la lista")

    check(find_redundant_connection([[1, 2], [1, 3], [1, 4], [1, 5], [1, 6], [2, 6]]) == [2, 6],
          "EJ23 grafo en forma de estrella")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
