# EJ 62 — Pacific Atlantic Water Flow — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej62_pacific_atlantic.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import sys
from typing import List, Set, Tuple


def normalize(cells: List[List[int]]) -> List[List[int]]:
    """Ordena la lista de celdas para poder comparar resultados sin
    importar el orden en que se generen."""
    return sorted(cells)


# ---------------------------------------------------------------------------
# EJ 62 — Pacific Atlantic Water Flow. Complejidad: O(m * n) tiempo y
# espacio.
# DFS hacia atrás desde los bordes de cada océano. Desde una celda de
# borde recorremos hacia una vecina si su altura es >= la de la celda
# actual (equivalente a decir que el agua podría fluir desde esa vecina
# hasta aquí). Así obtenemos, en dos DFS independientes (uno por
# océano), el conjunto de celdas desde las que el agua alcanza cada
# océano. El resultado es la intersección de ambos conjuntos.
def pacific_atlantic(heights: List[List[int]]) -> List[List[int]]:
    if not heights or not heights[0]:
        return []

    rows, cols = len(heights), len(heights[0])

    def bfs(starts: List[Tuple[int, int]]) -> Set[Tuple[int, int]]:
        visited: Set[Tuple[int, int]] = set(starts)
        stack = list(starts)
        while stack:
            r, c = stack.pop()
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if (0 <= nr < rows and 0 <= nc < cols and
                        (nr, nc) not in visited and
                        heights[nr][nc] >= heights[r][c]):
                    visited.add((nr, nc))
                    stack.append((nr, nc))
        return visited

    pacific_starts = [(0, c) for c in range(cols)] + [(r, 0) for r in range(rows)]
    atlantic_starts = ([(rows - 1, c) for c in range(cols)] +
                        [(r, cols - 1) for r in range(rows)])

    pacific_reachable = bfs(pacific_starts)
    atlantic_reachable = bfs(atlantic_starts)

    return [[r, c] for r, c in pacific_reachable & atlantic_reachable]


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
    heights1 = [
        [1, 2, 2, 3, 5],
        [3, 2, 3, 4, 4],
        [2, 4, 5, 3, 1],
        [6, 7, 1, 4, 5],
        [5, 1, 1, 2, 4],
    ]
    expected1 = [[0, 4], [1, 3], [1, 4], [2, 2], [3, 0], [3, 1], [4, 0]]
    check(normalize(pacific_atlantic(heights1)) == normalize(expected1),
          "EJ62 ejemplo clasico 5x5")

    check(normalize(pacific_atlantic([[1]])) == [[0, 0]],
          "EJ62 una sola celda toca ambos oceanos")

    check(pacific_atlantic([]) == [], "EJ62 matriz vacia")

    heights2 = [[1, 1], [1, 1]]
    check(normalize(pacific_atlantic(heights2)) ==
          normalize([[0, 0], [0, 1], [1, 0], [1, 1]]),
          "EJ62 matriz plana, todas las celdas fluyen a ambos")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
