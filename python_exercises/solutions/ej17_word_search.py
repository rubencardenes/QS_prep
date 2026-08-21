# EJ 17 — Word Search — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej17_word_search.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import sys
from typing import List


# ---------------------------------------------------------------------------
# EJ 17 — Word Search. Complejidad: O(filas * columnas * 4^L).
# Backtracking desde cada celda: si la letra coincide, se marca como
# visitada temporalmente ("#") y se explora en las 4 direcciones; al volver
# se restaura la celda para permitir otros caminos de búsqueda.
def exist(board: List[List[str]], word: str) -> bool:
    if not board or not board[0]:
        return False
    rows, cols = len(board), len(board[0])

    def backtrack(r: int, c: int, i: int) -> bool:
        if i == len(word):
            return True
        if r < 0 or r >= rows or c < 0 or c >= cols or board[r][c] != word[i]:
            return False

        temp = board[r][c]
        board[r][c] = "#"
        found = (backtrack(r + 1, c, i + 1) or backtrack(r - 1, c, i + 1) or
                 backtrack(r, c + 1, i + 1) or backtrack(r, c - 1, i + 1))
        board[r][c] = temp
        return found

    for r in range(rows):
        for c in range(cols):
            if backtrack(r, c, 0):
                return True
    return False


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
    board = [
        list("ABCE"),
        list("SFCS"),
        list("ADEE"),
    ]
    check(exist(board, "ABCCED") is True, "EJ17 palabra existe con giro en L")
    check(exist(board, "SEE") is True, "EJ17 palabra existe en linea recta")
    check(exist(board, "ABCB") is False, "EJ17 palabra reutilizaria la misma celda")
    check(exist([["A"]], "A") is True, "EJ17 tablero de una celda, coincide")
    check(exist([["A"]], "B") is False, "EJ17 tablero de una celda, no coincide")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
