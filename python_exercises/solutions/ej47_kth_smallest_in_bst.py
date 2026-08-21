# EJ 47 — Kth Smallest Element in a BST — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej47_kth_smallest_in_bst.py
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
# EJ 47 — Kth Smallest Element in a BST. Complejidad: O(H + k) tiempo,
# O(H) espacio.
# Recorrido inorder iterativo con una pila explícita: bajamos siempre por
# la izquierda apilando nodos, y al no poder bajar más desapilamos (ese es
# el siguiente valor en orden ascendente). Nos detenemos en cuanto hemos
# desapilado k veces, sin necesidad de recorrer el resto del árbol.
def kth_smallest(root: Optional[TreeNode], k: int) -> int:
    stack: List[TreeNode] = []
    node = root
    count = 0
    while stack or node is not None:
        while node is not None:
            stack.append(node)
            node = node.left
        node = stack.pop()
        count += 1
        if count == k:
            return node.val
        node = node.right
    raise ValueError("k fuera de rango")


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
