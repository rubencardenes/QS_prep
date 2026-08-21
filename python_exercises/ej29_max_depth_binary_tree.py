# EJ 29 — Maximum Depth of Binary Tree (recursion)  [warm-up]
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej29_max_depth_binary_tree.py
#   3. Cronométrate: apunta a ~10-15 min.
#   4. Solo si te atascas, mira solutions/ej29_max_depth_binary_tree.py.

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
# EJ 29 — Maximum Depth of Binary Tree
#   Devuelve la profundidad máxima de un árbol binario (número de nodos en
#   el camino más largo desde la raíz hasta la hoja más lejana). Un árbol
#   vacío tiene profundidad 0. Complejidad esperada: O(n).
# ---------------------------------------------------------------------------
def max_depth(root: Optional[TreeNode]) -> int:
    if root is None:
        return 0

    # Using BFS 
    q = deque()
    q.append((root,1))
    while(q):
        node, d = q.popleft()
        if node.left:
            q.append((node.left, d+1))
        if node.right:
            q.append((node.right, d+1))
    return d


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
