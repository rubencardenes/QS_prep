# EJ 9 — Number of Islands (DFS/BFS en grid) — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej9_number_of_islands.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import sys
from typing import List


# ---------------------------------------------------------------------------
# EJ 9 — Number of Islands. Complejidad: O(filas * columnas).
# Por cada celda de tierra no visitada, cuenta una isla nueva y "hunde" (DFS)
# toda la componente conectada marcándola como agua para no recontarla.
def num_islands(grid: List[List[str]]) -> int:
    if not grid:
        return 0
    rows, cols = len(grid), len(grid[0])

    def sink(r: int, c: int) -> None:
        if r < 0 or r >= rows or c < 0 or c >= cols or grid[r][c] != "1":
            return
        grid[r][c] = "0"
        sink(r + 1, c)
        sink(r - 1, c)
        sink(r, c + 1)
        sink(r, c - 1)

    count = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1":
                count += 1
                sink(r, c)
    return count


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
