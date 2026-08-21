# EJ 47 — Kth Smallest Element in a BST (arboles: recorrido inorder)
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej47_kth_smallest_in_bst.py
#   3. Cronométrate: apunta a ~15-20 min.
#   4. Solo si te atascas, mira solutions/ej47_kth_smallest_in_bst.py.

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
# EJ 47 — Kth Smallest Element in a BST
#   Dado un árbol binario de búsqueda (BST) y un entero `k`, devuelve el
#   k-ésimo elemento más pequeño (1-indexado).
#   Complejidad esperada: O(H + k) tiempo, donde H es la altura del árbol.
#   Pista: en un BST, el recorrido inorder (izquierda, nodo, derecha)
#   visita los valores en orden ascendente.
# ---------------------------------------------------------------------------
def kth_smallest(root: Optional[TreeNode], k: int) -> int:
    if root is None:
        return None
    stack = []
    node = root 
    count = 0
    while stack or node is not None:
        while node is not None:
            stack.append(node)
            node = node.left
        node = stack[-1]
        node = stack.pop()
        count += 1
        R = node.val
        # print(f"{R=}")
        if count == k:
            return R
        node = node.right
    
    return R

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
    tree1 = build_tree([3, 1, 4, None, 2])
    check(kth_smallest(tree1, 1) == 1, "EJ47 el mas pequeño")
    tree1b = build_tree([3, 1, 4, None, 2])
    check(kth_smallest(tree1b, 3) == 3, "EJ47 tercero mas pequeño")

    tree2 = build_tree([5, 3, 6, 2, 4, None, None, 1])
    check(kth_smallest(tree2, 3) == 3, "EJ47 arbol mas profundo, k=3")
    tree2b = build_tree([5, 3, 6, 2, 4, None, None, 1])
    check(kth_smallest(tree2b, 6) == 6, "EJ47 el mas grande (k = n)")

    check(kth_smallest(build_tree([1]), 1) == 1, "EJ47 un solo nodo")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
