# EJ 58 — Unique Paths (programacion dinamica: grid)
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej58_unique_paths.py
#   3. Cronométrate: apunta a ~15-20 min.
#   4. Solo si te atascas, mira solutions/ej58_unique_paths.py.

import sys


# ===========================================================================
# EJ 58 — Unique Paths
#   Un robot está en la esquina superior izquierda de una rejilla de
#   `m` filas y `n` columnas. Solo puede moverse hacia abajo o hacia la
#   derecha en cada paso. Devuelve cuántos caminos únicos existen hasta
#   la esquina inferior derecha.
#   Complejidad esperada: O(m * n) tiempo, O(n) espacio. Pista: el
#   número de caminos hasta una celda es la suma de los caminos hasta la
#   celda de arriba y la celda de la izquierda (dp[i][j] = dp[i-1][j] +
#   dp[i][j-1]); la primera fila y la primera columna valen 1.
# ---------------------------------------------------------------------------
def unique_paths(m: int, n: int) -> int:
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
    check(unique_paths(3, 7) == 28, "EJ58 rejilla 3x7")
    check(unique_paths(3, 2) == 3, "EJ58 rejilla 3x2")
    check(unique_paths(1, 1) == 1, "EJ58 una sola celda")
    check(unique_paths(1, 5) == 1, "EJ58 una sola fila")
    check(unique_paths(5, 1) == 1, "EJ58 una sola columna")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
