# EJ 14 — Validate Binary Search Tree — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej14_validate_bst.py
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
# EJ 14 — Validate Binary Search Tree. Complejidad: O(n).
# Propaga una cota (low, high) hacia abajo: cada nodo debe caer estrictamente
# dentro de la cota heredada de sus ancestros, no solo respecto a sus hijos.
def is_valid_bst(root: Optional[TreeNode]) -> bool:
    def validate(node: Optional[TreeNode], low: float, high: float) -> bool:
        if node is None:
            return True
        if not (low < node.val < high):
            return False
        return validate(node.left, low, node.val) and validate(node.right, node.val, high)

    return validate(root, float("-inf"), float("inf"))


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
    check(is_valid_bst(build_tree([2, 1, 3])) is True, "EJ14 BST valido simple")
    check(is_valid_bst(build_tree([5, 1, 4, None, None, 3, 6])) is False,
          "EJ14 hijo derecho viola el ancestro (3 < 5)")
    check(is_valid_bst(build_tree([1])) is True, "EJ14 un solo nodo")
    check(is_valid_bst(build_tree([])) is True, "EJ14 arbol vacio")
    check(is_valid_bst(build_tree([2, 2, 3])) is False, "EJ14 valores iguales no son BST valido")
    check(is_valid_bst(build_tree([10, 5, 15, 1, 8, 12, 20])) is True, "EJ14 BST valido mas grande")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
