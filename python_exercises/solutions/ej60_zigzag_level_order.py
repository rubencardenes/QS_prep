# EJ 60 — Binary Tree Zigzag Level Order Traversal — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej60_zigzag_level_order.py
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
# EJ 60 — Binary Tree Zigzag Level Order Traversal. Complejidad: O(n)
# tiempo, O(n) espacio.
# BFS estándar por niveles con una cola: en cada iteración procesamos
# todos los nodos que ya estaban en la cola (un nivel completo) antes de
# añadir sus hijos. Llevamos la cuenta del número de nivel para decidir
# si hay que invertir la lista de valores de ese nivel antes de
# guardarla.
def zigzag_level_order(root: Optional[TreeNode]) -> List[List[int]]:
    if root is None:
        return []

    result: List[List[int]] = []
    queue = deque([root])
    left_to_right = True

    while queue:
        level_size = len(queue)
        level_values = []
        for _ in range(level_size):
            node = queue.popleft()
            level_values.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        if not left_to_right:
            level_values.reverse()
        result.append(level_values)
        left_to_right = not left_to_right

    return result


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
    check(zigzag_level_order(build_tree([3, 9, 20, None, None, 15, 7])) ==
          [[3], [20, 9], [15, 7]], "EJ60 arbol de tres niveles")
    check(zigzag_level_order(build_tree([1])) == [[1]], "EJ60 un solo nodo")
    check(zigzag_level_order(build_tree([])) == [], "EJ60 arbol vacio")
    check(zigzag_level_order(build_tree([1, 2, 3, 4, 5, 6, 7])) ==
          [[1], [3, 2], [4, 5, 6, 7]], "EJ60 arbol completo de tres niveles")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
