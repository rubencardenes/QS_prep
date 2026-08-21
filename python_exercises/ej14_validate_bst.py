# EJ 14 — Validate Binary Search Tree (arboles)
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej14_validate_bst.py
#   3. Cronométrate: apunta a ~15-20 min.
#   4. Solo si te atascas, mira solutions/ej14_validate_bst.py.

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
# EJ 14 — Validate Binary Search Tree
#   Determina si un árbol binario es un BST válido: para cada nodo, TODOS
#   los valores de su subárbol izquierdo son estrictamente menores y TODOS
#   los del derecho estrictamente mayores (no basta comparar solo con los
#   hijos directos). Complejidad esperada: O(n).
# ---------------------------------------------------------------------------
def is_valid_bst(root: Optional[TreeNode]) -> bool:
    # BFS 
    if root is None:
        return True
    q = deque()
    result = {}
    D = 0
    q.append((root, D))
    while q:
        node, D = q.popleft()
        result.setdefault(D, []).append(node.val)
        if D > 0 and node.val < result[D][-1]:
            return False
        if node.left:
            if node.left.val >= node.val:
                return False
            q.append((node.left, D+1))
        if node.right:
            if node.right.val <= node.val:
                return False
            q.append((node.right, D+1))

    return True


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
