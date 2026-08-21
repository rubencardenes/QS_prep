# EJ 60 — Binary Tree Zigzag Level Order Traversal (BFS)
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej60_zigzag_level_order.py
#   3. Cronométrate: apunta a ~20-25 min.
#   4. Solo si te atascas, mira solutions/ej60_zigzag_level_order.py.

import sys
from collections import deque
from typing import List, Optional


class TreeNode:
    def __init__(self, val: int = 0, left: "Optional[TreeNode]" = None,
                 right: "Optional[TreeNode]" = None):
        self.val = val
        self.left = left
        self.right = right


def build_tree(values: List[Optional[int]]) -> Optional[TreeNode]:
    """Construye un arbol binario a partir de una lista estilo LeetCode
    (recorrido por niveles; None indica ausencia de hijo)."""
    if not values or values[0] is None:
        return None
    root = TreeNode(values[0])
    queue = deque([root])
    i = 1
    while queue and i < len(values):
        node = queue.popleft()
        if i < len(values):
            if values[i] is not None:
                node.left = TreeNode(values[i])
                queue.append(node.left)
            i += 1
        if i < len(values):
            if values[i] is not None:
                node.right = TreeNode(values[i])
                queue.append(node.right)
            i += 1
    return root


# ===========================================================================
# EJ 60 — Binary Tree Zigzag Level Order Traversal
#   Recorre un árbol binario nivel a nivel, pero alternando la
#   dirección: el primer nivel de izquierda a derecha, el segundo de
#   derecha a izquierda, el tercero de izquierda a derecha, etc.
#   Devuelve una lista de listas, una por nivel.
#   Complejidad esperada: O(n) tiempo, O(n) espacio. Pista: haz un BFS
#   normal por niveles con una cola, y simplemente invierte la lista de
#   valores de los niveles impares antes de añadirla al resultado.
# ---------------------------------------------------------------------------
def zigzag_level_order(root: Optional[TreeNode]) -> List[List[int]]:
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
    check(zigzag_level_order(build_tree([3, 9, 20, None, None, 15, 7])) ==
          [[3], [20, 9], [15, 7]], "EJ60 arbol de tres niveles")
    check(zigzag_level_order(build_tree([1])) == [[1]], "EJ60 un solo nodo")
    check(zigzag_level_order(build_tree([])) == [], "EJ60 arbol vacio")
    check(zigzag_level_order(build_tree([1, 2, 3, 4, 5, 6, 7])) ==
          [[1], [3, 2], [4, 5, 6, 7]], "EJ60 arbol completo de tres niveles")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
