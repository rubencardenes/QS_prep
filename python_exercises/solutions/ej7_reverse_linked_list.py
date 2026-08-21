# EJ 7 — Reverse Linked List (lista enlazada) — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej7_reverse_linked_list.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import sys
from typing import List, Optional


class ListNode:
    def __init__(self, val: int = 0, next: "Optional[ListNode]" = None):
        self.val = val
        self.next = next


def build_list(values: List[int]) -> Optional[ListNode]:
    head = None
    tail = None
    for v in values:
        node = ListNode(v)
        if head is None:
            head = node
        else:
            tail.next = node
        tail = node
    return head


def to_list(head: Optional[ListNode]) -> List[int]:
    out = []
    while head:
        out.append(head.val)
        head = head.next
    return out


# ---------------------------------------------------------------------------
# EJ 7 — Reverse Linked List. Complejidad: O(n) tiempo, O(1) espacio.
# Tres punteros: prev, curr y nxt; en cada paso invierte el enlace y avanza.
def reverse_list(head: Optional[ListNode]) -> Optional[ListNode]:
    prev = None
    curr = head
    while curr:
        nxt = curr.next
        curr.next = prev
        prev = curr
        curr = nxt
    return prev


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
    check(to_list(reverse_list(build_list([1, 2, 3, 4, 5]))) == [5, 4, 3, 2, 1],
          "EJ7 lista de varios elementos")
    check(to_list(reverse_list(build_list([1, 2]))) == [2, 1], "EJ7 lista de dos elementos")
    check(to_list(reverse_list(build_list([1]))) == [1], "EJ7 lista de un elemento")
    check(to_list(reverse_list(build_list([]))) == [], "EJ7 lista vacia")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
