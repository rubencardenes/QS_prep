# EJ 29 — Maximum Depth of Binary Tree — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej29_max_depth_binary_tree.py
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
# EJ 29 — Maximum Depth of Binary Tree. Complejidad: O(n).
# Recursion simple: la profundidad de un arbol es 1 (el nodo actual) mas
# la mayor profundidad entre sus dos subarboles. Caso base: arbol vacio
# tiene profundidad 0.
def max_depth(root: Optional[TreeNode]) -> int:
    if root is None:
        return 0
    return 1 + max(max_depth(root.left), max_depth(root.right))


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
    check(max_depth(build_tree([3, 9, 20, None, None, 15, 7])) == 3, "EJ29 arbol de 3 niveles")
    check(max_depth(build_tree([])) == 0, "EJ29 arbol vacio")
    check(max_depth(build_tree([1])) == 1, "EJ29 un solo nodo")
    check(max_depth(build_tree([1, None, 2])) == 2, "EJ29 rama unica hacia la derecha")
    check(max_depth(build_tree([1, 2, 3, 4, None, None, None, 5])) == 4,
          "EJ29 rama izquierda mas profunda")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
