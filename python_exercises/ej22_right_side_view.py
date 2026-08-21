# EJ 22 — Binary Tree Right Side View (BFS)
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej22_right_side_view.py
#   3. Cronométrate: apunta a ~20 min.
#   4. Solo si te atascas, mira solutions/ej22_right_side_view.py.

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
# EJ 22 — Binary Tree Right Side View
#   Imagina que te colocas a la derecha del árbol y miras hacia la
#   izquierda: por cada nivel, solo ves un nodo (los demás quedan tapados
#   detrás). Devuelve esos valores, uno por nivel, ordenados de arriba a
#   abajo.
#
#   OJO: no es "coger el hijo derecho de cada nodo". Es el último nodo de
#   cada nivel al recorrerlo de izquierda a derecha, aunque ese nodo
#   cuelgue de una rama izquierda. Ejemplo:
#         1
#        / \
#       2   3
#        \   \
#         5   4
#   Nivel 0 -> [1]        (se ve el 1)
#   Nivel 1 -> [2, 3]     (se ve el 3, tapa al 2)
#   Nivel 2 -> [5, 4]     (se ve el 4, aunque 5 cuelgue de la rama izq.)
#   Resultado: [1, 3, 4]
#
#   Pista: BFS nivel a nivel (como en el EJ 8); en cada nivel guarda solo
#   el valor del último nodo procesado. Complejidad esperada: O(n).
# ---------------------------------------------------------------------------
def right_side_view(root: Optional[TreeNode]) -> List[int]:
    if root is None:
        return []
    q = deque()
    d = 0
    q.append((root, d))
    result = {}
    while(q):
        node, d = q.popleft()
        result[d] = node.val
        if node.left:
            q.append((node.left, d+1))
        if node.right:
            q.append((node.right, d+1))
    return [r for r in result.values()]
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
