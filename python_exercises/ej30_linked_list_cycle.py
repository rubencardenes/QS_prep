# EJ 30 — Linked List Cycle (dos punteros: tortuga y liebre)
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej30_linked_list_cycle.py
#   3. Cronométrate: apunta a ~15-20 min.
#   4. Solo si te atascas, mira solutions/ej30_linked_list_cycle.py.

import sys
from typing import List, Optional


class ListNode:
    def __init__(self, val: int = 0, next: "Optional[ListNode]" = None):
        self.val = val
        self.next = next


def build_list_with_cycle(values: List[int], cycle_pos: int) -> Optional[ListNode]:
    """Construye una lista enlazada a partir de `values`. Si cycle_pos >= 0,
    el ultimo nodo apunta de vuelta al nodo en ese indice (0-based),
    formando un ciclo. cycle_pos == -1 significa "sin ciclo"."""
    if not values:
        return None
    nodes = [ListNode(v) for v in values]
    for i in range(len(nodes) - 1):
        nodes[i].next = nodes[i + 1]
    if cycle_pos >= 0:
        nodes[-1].next = nodes[cycle_pos]
    return nodes[0]


# ===========================================================================
# EJ 30 — Linked List Cycle
#   Determina si una lista enlazada tiene un ciclo (algún nodo apunta de
#   vuelta a un nodo anterior en vez de a None). NO puedes usar un
#   set/lista para guardar nodos visitados: hazlo en O(1) espacio con dos
#   punteros (tortuga y liebre / Floyd's cycle detection). Complejidad
#   esperada: O(n) tiempo, O(1) espacio.
# ---------------------------------------------------------------------------
def has_cycle(head: Optional[ListNode]) -> bool:
    if head is None:
        return False
    L = head
    T = head
    while L and L.next:
        if T.next is None or L.next is None or L.next.next is None:
            return False
        T = T.next
        L = L.next.next
        if T == L:
            return True
    return False


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
    check(has_cycle(build_list_with_cycle([3, 2, 0, -4], 1)) is True,
          "EJ30 ciclo que vuelve al segundo nodo")
    check(has_cycle(build_list_with_cycle([1, 2], 0)) is True,
          "EJ30 ciclo que vuelve al primer nodo")
    check(has_cycle(build_list_with_cycle([1], -1)) is False, "EJ30 un nodo sin ciclo")
    check(has_cycle(build_list_with_cycle([], -1)) is False, "EJ30 lista vacia")
    check(has_cycle(build_list_with_cycle([1, 2, 3, 4, 5], -1)) is False,
          "EJ30 lista normal sin ciclo")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
