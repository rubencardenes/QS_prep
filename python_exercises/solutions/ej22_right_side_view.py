# EJ 22 — Binary Tree Right Side View — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej22_right_side_view.py
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
# EJ 22 — Binary Tree Right Side View. Complejidad: O(n).
# BFS nivel a nivel: en cada nivel se recorren todos sus nodos y se guarda
# el valor del último (el más a la derecha) antes de pasar al siguiente.
def right_side_view(root: Optional[TreeNode]) -> List[int]:
    if root is None:
        return []
    result = []
    q = deque([root])
    while q:
        level_size = len(q)
        for i in range(level_size):
            node = q.popleft()
            if i == level_size - 1:
                result.append(node.val)
            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)
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
    tree = build_tree([1, 2, 3, None, 5, None, 4])
    check(right_side_view(tree) == [1, 3, 4], "EJ22 arbol con huecos a la izquierda")

    tree2 = build_tree([1, None, 3])
    check(right_side_view(tree2) == [1, 3], "EJ22 solo hijos derechos")

    check(right_side_view(build_tree([])) == [], "EJ22 arbol vacio")
    check(right_side_view(build_tree([1])) == [1], "EJ22 un solo nodo")

    tree3 = build_tree([1, 2, 3, 4])
    check(right_side_view(tree3) == [1, 3, 4], "EJ22 el ultimo nivel solo tiene hijo izquierdo")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
