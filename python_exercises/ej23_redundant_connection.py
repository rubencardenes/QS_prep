# EJ 23 — Redundant Connection (Union-Find)
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej23_redundant_connection.py
#   3. Cronométrate: apunta a ~20-25 min.
#   4. Solo si te atascas, mira solutions/ej23_redundant_connection.py.

import sys
from typing import List


# ===========================================================================
# EJ 23 — Redundant Connection
#   Un grafo empezó siendo un árbol de n nodos (numerados 1..n) y se le
#   añadió una arista de más, formando exactamente un ciclo. Se te da la
#   lista de aristas en el orden en que se añadieron. Devuelve la arista
#   que, si se elimina, deja un árbol válido. Si hay varias aristas que
#   cumplirían esto, devuelve la que aparece última en la lista `edges`.
#   Pista: procesa las aristas en orden con Union-Find; la primera arista
#   que conecta dos nodos ya conectados es la respuesta.
# ---------------------------------------------------------------------------
def find_redundant_connection(edges: List[List[int]]) -> List[int]:
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
