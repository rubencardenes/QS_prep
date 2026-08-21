# EJ 9 — Number of Islands (DFS/BFS en grid)
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej9_number_of_islands.py
#   3. Cronométrate: apunta a ~20-25 min.
#   4. Solo si te atascas, mira solutions/ej9_number_of_islands.py.

import sys
from typing import List
from collections import deque


# ===========================================================================
# EJ 9 — Number of Islands
#   `grid` es una matriz de '1' (tierra) y '0' (agua). Una isla es un grupo
#   de '1's conectados horizontal o verticalmente (no en diagonal), rodeado
#   de agua. Devuelve el número de islas. Puedes modificar `grid` in-place
#   para marcar celdas visitadas. Complejidad esperada: O(filas * columnas).
# ---------------------------------------------------------------------------
def num_islands(grid: List[List[str]]) -> int:
    # Using BFS
    num_islands = 0
    if len(grid) == 0:
        return 0
    q = deque()
    COLS = len(grid)
    ROWS = len(grid[0])
    neihgbors = [(-1,0), (0, 1), (0, -1), (1, 0)]
    print("COLS, ROWS ", COLS, ROWS)
    for c in range(COLS):
        for r in range(ROWS):
            if (grid[c][r] == "1"):
                num_islands += 1 
                # BFS
                q.append((c, r))
                while q:
                    c_, r_ = q.popleft()
                    grid[c_][r_] = "2"
                    for n in neihgbors:
                        nr = r_+n[0]
                        nc = c_+n[1]
                        if nr < 0 or nc < 0 or nr >= ROWS or nc >= COLS:
                            continue 
                        if grid[nc][nr] == "1":
                            q.append((nc, nr))

    return num_islands


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
    grid1 = [
        list("11110"),
        list("11010"),
        list("11000"),
        list("00000"),
    ]
    check(num_islands(grid1) == 1, "EJ9 una isla grande conectada")

    grid2 = [
        list("11000"),
        list("11000"),
        list("00100"),
        list("00011"),
    ]
    check(num_islands(grid2) == 3, "EJ9 varias islas separadas")

    check(num_islands([list("0")]) == 0, "EJ9 grid de solo agua")
    check(num_islands([list("1")]) == 1, "EJ9 grid de una sola celda de tierra")
    check(num_islands([]) == 0, "EJ9 grid vacio")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
