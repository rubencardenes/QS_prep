# EJ 8 — Binary Tree Level Order Traversal (BFS) — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej8_level_order_traversal.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

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


# ---------------------------------------------------------------------------
# EJ 8 — Level Order Traversal. Complejidad: O(n).
# BFS con una cola; en cada iteración se vacía exactamente el nivel actual
# (se guarda su tamaño antes de empezar a añadir hijos del siguiente nivel).
def level_order(root: Optional[TreeNode]) -> List[List[int]]:
    if not root:
        return []
    result = []
    queue = deque([root])
    while queue:
        level = []
        for _ in range(len(queue)):
            node = queue.popleft()
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        result.append(level)
    return result


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
