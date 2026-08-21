# EJ 17 — Word Search (backtracking en grid)
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej17_word_search.py
#   3. Cronométrate: apunta a ~20-25 min.
#   4. Solo si te atascas, mira solutions/ej17_word_search.py.

import sys
from typing import List
from collections import deque

# ===========================================================================
# EJ 17 — Word Search
#   Dado un `board` de letras y una `word`, determina si la palabra puede
#   construirse a partir de letras adyacentes (horizontal o verticalmente,
#   no en diagonal), sin reutilizar la misma celda dos veces dentro de la
#   misma palabra. Complejidad esperada: O(filas * columnas * 4^L).
# ---------------------------------------------------------------------------
def exist(board: List[List[str]], word: str) -> bool:
    if len(board) == 0:
        return False
    rows = len(board)
    cols = len(board[0])
    if cols == 0:
        return False
    q = deque()
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    v = [0 for x in range(cols)]
    visited = [v.copy() for x in range(rows)]
    for c in range(cols):
        for r in range(rows):
            if word[0] == board[r][c]:
                print(f"word[0] {word[0]}")
                if len(word) == 1:
                    return True
                # Search in four directions
                d = 0
                q.append((r, c, d))
                visited[r][c] = 1
                while(q):
                    nr_, nc_, d = q.popleft()
                    for dir in directions:
                        nr = nr_+dir[0]
                        nc = nc_+dir[1]
                        if nr < 0 or nc < 0 or nr >= rows or nc >= cols:
                            continue
                        if board[nr][nc] == word[d+1] and visited[nr][nc] == 0:
                            if d+1 == len(word)-1:
                                print("Found word")
                                return True
                            q.append((nr, nc, d+1))
                            visited[nr][nc] = 1

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
    board = [
        list("ABCE"),
        list("BFCS"),
        list("ADEE"),
    ]
    check(exist(board, "ABCCED") is True, "EJ17 palabra existe con giro en L")
    check(exist(board, "ABC") is True, "EJ17 palabra existe")
    check(exist(board, "SEE") is True, "EJ17 palabra existe en linea recta")
    check(exist(board, "ABCB") is False, "EJ17 palabra reutilizaria la misma celda")
    check(exist([["A"]], "A") is True, "EJ17 tablero de una celda, coincide")
    check(exist([["A"]], "B") is False, "EJ17 tablero de una celda, no coincide")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
