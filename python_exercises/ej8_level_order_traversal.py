# EJ 8 — Binary Tree Level Order Traversal (BFS)
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej8_level_order_traversal.py
#   3. Cronométrate: apunta a ~20 min.
#   4. Solo si te atascas, mira solutions/ej8_level_order_traversal.py.

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
# EJ 8 — Level Order Traversal
#   Devuelve los valores del árbol agrupados por nivel (de arriba a abajo,
#   izquierda a derecha), como lista de listas. Usa BFS con una cola.
#   Complejidad esperada: O(n).
# ---------------------------------------------------------------------------
def level_order(root: Optional[TreeNode]) -> List[List[int]]:
    # Usado BFS y cola
    if root is None:
        return []
    result = []
    q = deque()
    level = 0
    q.append((root, level))
    while q:
        node, level = q.popleft()
        if len(result) <= level:
            result.append([])
        result[level].append(node.val)
        if node.left is not None:
            q.append((node.left, level+1))
        if node.right is not None:
            q.append((node.right, level+1))
    return result


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
    tree = build_tree([3, 9, 20, None, None, 15, 7])
    check(level_order(tree) == [[3], [9, 20], [15, 7]], "EJ8 arbol de 3 niveles")

    check(level_order(build_tree([1])) == [[1]], "EJ8 un solo nodo")
    check(level_order(build_tree([])) == [], "EJ8 arbol vacio")

    tree2 = build_tree([1, 2, 3, 4, None, None, 5])
    check(level_order(tree2) == [[1], [2, 3], [4, 5]], "EJ8 arbol con huecos")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
