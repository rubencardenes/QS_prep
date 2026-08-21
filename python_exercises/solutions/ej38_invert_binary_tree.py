# EJ 38 — Invert Binary Tree — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej38_invert_binary_tree.py
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


def tree_to_list(root: Optional[TreeNode]) -> List[Optional[int]]:
    """Serializa el arbol por niveles (BFS), incluyendo None donde falta
    un hijo, y recorta los None finales. Sirve para comparar arboles."""
    if root is None:
        return []
    result: List[Optional[int]] = []
    q = deque([root])
    while q:
        node = q.popleft()
        if node is None:
            result.append(None)
            continue
        result.append(node.val)
        q.append(node.left)
        q.append(node.right)
    while result and result[-1] is None:
        result.pop()
    return result


# ---------------------------------------------------------------------------
# EJ 38 — Invert Binary Tree. Complejidad: O(n).
# Recursion: se invierten primero los dos subarboles y luego se
# intercambian; el caso base es el arbol vacio, que es su propio
# invertido.
def invert_tree(root: Optional[TreeNode]) -> Optional[TreeNode]:
    if root is None:
        return None
    root.left, root.right = invert_tree(root.right), invert_tree(root.left)
    return root


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
    got = tree_to_list(invert_tree(build_tree([4, 2, 7, 1, 3, 6, 9])))
    expected = tree_to_list(build_tree([4, 7, 2, 9, 6, 3, 1]))
    check(got == expected, "EJ38 arbol de 3 niveles")

    check(tree_to_list(invert_tree(build_tree([]))) == [], "EJ38 arbol vacio")
    check(tree_to_list(invert_tree(build_tree([1]))) == [1], "EJ38 un solo nodo")

    got2 = tree_to_list(invert_tree(build_tree([2, 1, 3])))
    check(got2 == [2, 3, 1], "EJ38 arbol pequeño")

    got3 = tree_to_list(invert_tree(build_tree([1, 2, None])))
    expected3 = tree_to_list(build_tree([1, None, 2]))
    check(got3 == expected3, "EJ38 solo hijo izquierdo pasa a ser derecho")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
