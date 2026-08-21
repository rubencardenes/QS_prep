# EJ 54 — Copy List with Random Pointer — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej54_copy_list_random_pointer.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import sys
from typing import Dict, List, Optional


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


# ---------------------------------------------------------------------------
# EJ 54 — Copy List with Random Pointer. Complejidad: O(n) tiempo, O(n)
# espacio.
# Primera pasada: recorremos la lista original y creamos un nodo copia
# por cada nodo (solo con el valor), guardando en un hashmap la relacion
# original -> copia. Segunda pasada: recorremos de nuevo la lista
# original y, usando el hashmap, enlazamos next y random de cada copia.
# El hashmap resuelve el problema de que `random` puede apuntar hacia
# adelante en la lista, a un nodo que todavia no se hubiera copiado.
def copy_random_list(head: Optional[Node]) -> Optional[Node]:
    if head is None:
        return None

    mapping: Dict[Node, Node] = {}
    current = head
    while current:
        mapping[current] = Node(current.val)
        current = current.next

    current = head
    while current:
        copy = mapping[current]
        copy.next = mapping[current.next] if current.next else None
        copy.random = mapping[current.random] if current.random else None
        current = current.next

    return mapping[head]


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
