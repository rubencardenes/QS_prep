# EJ 61 — Lowest Common Ancestor of a Binary Tree — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej61_lowest_common_ancestor.py
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


# ---------------------------------------------------------------------------
# EJ 61 — Lowest Common Ancestor of a Binary Tree. Complejidad: O(n)
# tiempo, O(H) espacio de recursión.
# Recursión post-order: en cada nodo, si es None o coincide con p o q,
# lo devolvemos tal cual (ya hemos encontrado lo que buscábamos por esa
# rama). Si no, buscamos en ambos subárboles. Si los dos devuelven algo
# no-None, es que p y q están en ramas distintas y el nodo actual es su
# LCA. Si solo uno de los dos devuelve algo, ese resultado se propaga
# hacia arriba sin cambios (p y q están ambos en esa misma rama, o
# ninguno está en el árbol).
def lowest_common_ancestor(root: Optional[TreeNode], p: TreeNode,
                            q: TreeNode) -> Optional[TreeNode]:
    if root is None or root is p or root is q:
        return root

    left = lowest_common_ancestor(root.left, p, q)
    right = lowest_common_ancestor(root.right, p, q)

    if left and right:
        return root
    return left if left else right


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
