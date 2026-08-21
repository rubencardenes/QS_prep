# EJ 54 — Copy List with Random Pointer (lista enlazada + hashmap)
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej54_copy_list_random_pointer.py
#   3. Cronométrate: apunta a ~20-25 min.
#   4. Solo si te atascas, mira solutions/ej54_copy_list_random_pointer.py.

import sys
from typing import List, Optional


class Node:
    def __init__(self, x: int, next: "Optional[Node]" = None,
                 random: "Optional[Node]" = None):
        self.val = x
        self.next = next
        self.random = random


def build_list(pairs: List[List[Optional[int]]]) -> Optional[Node]:
    """`pairs` es una lista de [valor, indice_random] estilo LeetCode,
    donde indice_random es la posicion (0-indexada) del nodo al que
    apunta `random`, o None si no apunta a ninguno."""
    if not pairs:
        return None
    nodes = [Node(val) for val, _ in pairs]
    for i, (_, random_idx) in enumerate(pairs):
        nodes[i].next = nodes[i + 1] if i + 1 < len(nodes) else None
        nodes[i].random = nodes[random_idx] if random_idx is not None else None
    return nodes[0]


def to_pairs(head: Optional[Node]) -> List[List[Optional[int]]]:
    """Serializa la lista de vuelta al formato [valor, indice_random]."""
    nodes = []
    current = head
    while current:
        nodes.append(current)
        current = current.next
    index_of = {id(node): i for i, node in enumerate(nodes)}
    result: List[List[Optional[int]]] = []
    for node in nodes:
        random_idx = index_of[id(node.random)] if node.random else None
        result.append([node.val, random_idx])
    return result


def is_deep_copy(original_head: Optional[Node], copy_head: Optional[Node]) -> bool:
    """Comprueba que ningun nodo de la copia sea el mismo objeto que su
    correspondiente en la lista original."""
    o, c = original_head, copy_head
    while o and c:
        if o is c:
            return False
        o, c = o.next, c.next
    return o is None and c is None


# ===========================================================================
# EJ 54 — Copy List with Random Pointer
#   Cada nodo de una lista enlazada tiene, además de `next`, un puntero
#   `random` que puede apuntar a cualquier nodo de la lista (o a None).
#   Devuelve una copia profunda (deep copy) de la lista completa.
#   Complejidad esperada: O(n) tiempo, O(n) espacio. Pista: usa un
#   hashmap nodo_original -> nodo_copia. Con dos pasadas: primero crea
#   todos los nodos copia (solo con su valor), y luego, en una segunda
#   pasada, asigna `next` y `random` de cada copia usando el hashmap.
# ---------------------------------------------------------------------------
from collections import deque
def copy_random_list(head: Optional[Node]) -> Optional[Node]:
    if head is None:
        return None
    print(f"{to_pairs(head)}")
    h = {}
    # Primera pasada creamos hashmap
    head_c = Node(head.val)
    h[head] = head_c
    node = head.next
    while node is not None:
        node_c = Node(node.val)
        h[node] = node_c
        node = node.next
    
    # Segunda pasada pos las copias 
    node = head 
    while node is not None:
        if node.next:
            h[node].next = h[node.next]
        if node.random:
            h[node].random = h[node.random]
        node = node.next
        
    print(f"{to_pairs(head_c)}")

    return head_c

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
    pairs1 = [[7, None], [13, 0], [11, 4], [10, 2], [1, 0]]
    original1 = build_list(pairs1)
    copy1 = copy_random_list(original1)
    check(to_pairs(copy1) == pairs1, "EJ54 lista de 5 nodos con randoms")
    check(is_deep_copy(original1, copy1), "EJ54 la copia usa nodos distintos")

    pairs2 = [[3, None], [3, 0], [3, None]]
    original2 = build_list(pairs2)
    copy2 = copy_random_list(original2)
    check(to_pairs(copy2) == pairs2, "EJ54 valores repetidos")

    check(copy_random_list(None) is None, "EJ54 lista vacia")

    pairs4 = [[1, 0]]
    original4 = build_list(pairs4)
    copy4 = copy_random_list(original4)
    check(to_pairs(copy4) == pairs4, "EJ54 un solo nodo con random a si mismo")
    check(is_deep_copy(original4, copy4), "EJ54 nodo unico tambien se clona")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
