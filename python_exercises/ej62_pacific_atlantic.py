# EJ 62 — Pacific Atlantic Water Flow (DFS/BFS en grid)
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej62_pacific_atlantic.py
#   3. Cronométrate: apunta a ~25-30 min.
#   4. Solo si te atascas, mira solutions/ej62_pacific_atlantic.py.

import sys
from typing import List


def normalize(cells: List[List[int]]) -> List[List[int]]:
    """Ordena la lista de celdas para poder comparar resultados sin
    importar el orden en que se generen."""
    return sorted(cells)


# ===========================================================================
# EJ 62 — Pacific Atlantic Water Flow
#   Hay una matriz `heights` de m x n con la altura de cada celda. El
#   océano Pacífico toca el borde superior e izquierdo de la matriz; el
#   Atlántico toca el borde inferior y derecho. El agua de una celda
#   puede fluir a una celda vecina (arriba/abajo/izq/der) si la altura
#   de la vecina es menor o igual. Devuelve la lista de celdas [fila,
#   columna] desde las que el agua puede fluir a AMBOS océanos.
#   Complejidad esperada: O(m * n) tiempo y espacio. Pista: en vez de
#   simular el flujo desde cada celda (que sería O((m*n)^2)), haz DFS/BFS
#   hacia atrás desde los bordes de cada océano: desde una celda de borde,
#   se puede "retroceder" a una vecina si su altura es MAYOR O IGUAL (el
#   agua fluiría de esa vecina hacia aquí). El resultado es la
#   intersección de las celdas alcanzables desde ambos océanos.
# ---------------------------------------------------------------------------
def pacific_atlantic(heights: List[List[int]]) -> List[List[int]]:
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
