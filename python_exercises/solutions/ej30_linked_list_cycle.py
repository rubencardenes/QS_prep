# EJ 30 — Linked List Cycle — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej30_linked_list_cycle.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

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


# ---------------------------------------------------------------------------
# EJ 30 — Linked List Cycle. Complejidad: O(n) tiempo, O(1) espacio.
# Algoritmo de Floyd: un puntero lento avanza un nodo por paso y uno
# rapido avanza dos. Si hay ciclo, el rapido "da la vuelta" y acaba
# alcanzando al lento; si no hay ciclo, el rapido llega a None primero.
def has_cycle(head: Optional[ListNode]) -> bool:
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            return True
    return False


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
