# EJ 48 — Clone Graph (grafos: BFS/DFS + hashmap)
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej48_clone_graph.py
#   3. Cronométrate: apunta a ~20-25 min.
#   4. Solo si te atascas, mira solutions/ej48_clone_graph.py.

import sys
from typing import List, Optional
from collections import deque

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


# ===========================================================================
# EJ 48 — Clone Graph
#   Dado un nodo de un grafo no dirigido y conexo, devuelve una copia
#   profunda (deep copy) de todo el grafo. Cada nodo tiene un valor y una
#   lista de referencias a sus vecinos.
#   Complejidad esperada: O(V + E) tiempo y espacio. Pista: usa un
#   hashmap nodo_original -> nodo_clonado para no clonar el mismo nodo dos
#   veces y para poder reconstruir las referencias entre vecinos.
# ---------------------------------------------------------------------------
def clone_graph(node: Optional[Node]) -> Optional[Node]:
    if node is None:
        return None
    print(f"{to_adj_list(node)=}")
    h = {}
    q = deque()
    q.append(node)
    # Recorremos el grafo con BFS
    while q:
        node = q.popleft()
        # Create copy 
        node_c = Node(val = node.val)
        h[node] = node_c
        # Fill up neighbors
        for n in node.neighbors:
            if n not in h:
                continue
            print(f"{node.val=} -- {n.val=}")
            if n is not None and h[n] not in node_c.neighbors:
                node_c.neighbors.append(h[n]) 
        for neigh in node.neighbors:
            if neigh is not None:
                # Creamos nodos copia de los vecinos 
                if neigh not in h:
                    node_n = Node(val = node.val)
                    node_c.neighbors.append(node_n)
                    q.append(neigh)

    print(f"{to_adj_list(node_c)=}")
    return node_c


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
