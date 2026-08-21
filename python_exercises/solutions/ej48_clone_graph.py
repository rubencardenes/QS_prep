# EJ 48 — Clone Graph — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej48_clone_graph.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import sys
from typing import Dict, List, Optional


class Node:
    def __init__(self, val: int = 0, neighbors: "Optional[List[Node]]" = None):
        self.val = val
        self.neighbors = neighbors if neighbors is not None else []


def build_graph(adj_list: List[List[int]]) -> Optional[Node]:
    """Construye el grafo a partir de una lista de adyacencia estilo
    LeetCode: adj_list[i] son los valores de los vecinos del nodo con
    valor i + 1. Devuelve el nodo con valor 1 (o None si esta vacio)."""
    if not adj_list:
        return None
    nodes = {i + 1: Node(i + 1) for i in range(len(adj_list))}
    for i, neighbor_vals in enumerate(adj_list):
        nodes[i + 1].neighbors = [nodes[v] for v in neighbor_vals]
    return nodes[1]


def to_adj_list(node: Optional[Node]) -> List[List[int]]:
    """Serializa el grafo (alcanzable desde `node`) de vuelta a la lista
    de adyacencia, con los vecinos de cada nodo ordenados."""
    if node is None:
        return []
    visited = {}

    def dfs(n: Node) -> None:
        if n.val in visited:
            return
        visited[n.val] = sorted(neigh.val for neigh in n.neighbors)
        for neigh in n.neighbors:
            dfs(neigh)

    dfs(node)
    return [visited[val] for val in sorted(visited)]


# ---------------------------------------------------------------------------
# EJ 48 — Clone Graph. Complejidad: O(V + E) tiempo y espacio.
# DFS recursivo con un hashmap `clones` que mapea nodo original -> nodo
# clonado. Al visitar un nodo por primera vez creamos su clon (sin
# vecinos todavia) y lo guardamos en el hashmap ANTES de recorrer sus
# vecinos, para que los ciclos no provoquen recursion infinita: si un
# vecino ya esta en el hashmap, simplemente reutilizamos su clon.
def clone_graph(node: Optional[Node]) -> Optional[Node]:
    if node is None:
        return None

    clones: Dict[Node, Node] = {}

    def dfs(original: Node) -> Node:
        if original in clones:
            return clones[original]
        clone = Node(original.val)
        clones[original] = clone
        clone.neighbors = [dfs(neigh) for neigh in original.neighbors]
        return clone

    return dfs(node)


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
    adj1 = [[2, 4], [1, 3], [2, 4], [1, 3]]
    original1 = build_graph(adj1)
    clone1 = clone_graph(original1)
    check(to_adj_list(clone1) == adj1, "EJ48 grafo de 4 nodos en ciclo")
    check(clone1 is not original1, "EJ48 el clon no es el mismo objeto raiz")

    check(clone_graph(None) is None, "EJ48 grafo vacio")

    adj3 = [[]]
    original3 = build_graph(adj3)
    clone3 = clone_graph(original3)
    check(to_adj_list(clone3) == adj3, "EJ48 un solo nodo sin vecinos")
    check(clone3 is not original3, "EJ48 nodo unico clonado es otro objeto")

    adj4 = [[2], [1]]
    original4 = build_graph(adj4)
    clone4 = clone_graph(original4)
    check(to_adj_list(clone4) == adj4, "EJ48 dos nodos conectados")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
