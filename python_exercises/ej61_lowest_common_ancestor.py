# EJ 61 — Lowest Common Ancestor of a Binary Tree (recursion)
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej61_lowest_common_ancestor.py
#   3. Cronométrate: apunta a ~20-25 min.
#   4. Solo si te atascas, mira solutions/ej61_lowest_common_ancestor.py.

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


def find_node(root: Optional[TreeNode], val: int) -> Optional[TreeNode]:
    """Busca (BFS) el primer nodo con valor `val`. Util para obtener las
    referencias `p` y `q` que pide lowest_common_ancestor."""
    queue = deque([root]) if root else deque()
    while queue:
        node = queue.popleft()
        if node.val == val:
            return node
        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)
    return None


# ===========================================================================
# EJ 61 — Lowest Common Ancestor of a Binary Tree
#   Dado la raíz de un árbol binario (no necesariamente de búsqueda) y
#   dos nodos `p` y `q` que existen en el árbol, devuelve su ancestro
#   común más bajo (el nodo más profundo que es ancestro de ambos; un
#   nodo puede ser ancestro de sí mismo).
#   Complejidad esperada: O(n) tiempo, O(H) espacio de recursión.
#   Pista: recursión post-order. Si el nodo actual es None, o es igual a
#   `p` o a `q`, devuélvelo. Si tanto la búsqueda por la izquierda como
#   por la derecha encuentran algo, el nodo actual es el LCA. Si solo
#   una rama encuentra algo, propágalo hacia arriba.
# ---------------------------------------------------------------------------
def lowest_common_ancestor(root: Optional[TreeNode], p: TreeNode,
                            q: TreeNode) -> Optional[TreeNode]:
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
    tree = build_tree([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])

    lca1 = lowest_common_ancestor(tree, find_node(tree, 5), find_node(tree, 1))
    check(lca1 is not None and lca1.val == 3, "EJ61 LCA en la raiz")

    lca2 = lowest_common_ancestor(tree, find_node(tree, 5), find_node(tree, 4))
    check(lca2 is not None and lca2.val == 5, "EJ61 un nodo es ancestro del otro")

    lca3 = lowest_common_ancestor(tree, find_node(tree, 6), find_node(tree, 4))
    check(lca3 is not None and lca3.val == 5, "EJ61 LCA a media altura")

    lca4 = lowest_common_ancestor(tree, find_node(tree, 0), find_node(tree, 8))
    check(lca4 is not None and lca4.val == 1, "EJ61 LCA en subarbol derecho")

    small = build_tree([1, 2])
    lca5 = lowest_common_ancestor(small, find_node(small, 1), find_node(small, 2))
    check(lca5 is not None and lca5.val == 1, "EJ61 arbol de dos nodos")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
