# EJ 7 — Reverse Linked List (lista enlazada)
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej7_reverse_linked_list.py
#   3. Cronométrate: apunta a ~15 min.
#   4. Solo si te atascas, mira solutions/ej7_reverse_linked_list.py.

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


# ===========================================================================
# EJ 7 — Reverse Linked List
#   Invierte una lista enlazada simple y devuelve la nueva cabeza.
#   Hazlo de forma iterativa, en O(n) tiempo y O(1) espacio extra.
# ---------------------------------------------------------------------------
def reverse_list(head: Optional[ListNode]) -> Optional[ListNode]:
    print(to_list(head))
    current = head
    previous = None
    while current is not None:
        next = current.next
        current.next = previous
        previous = current
        head = current
        current = next
    print(to_list(head))
    return head


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
    check(to_list(reverse_list(build_list([1, 2, 3, 4, 5]))) == [5, 4, 3, 2, 1],
          "EJ7 lista de varios elementos")
    check(to_list(reverse_list(build_list([1, 2]))) == [2, 1], "EJ7 lista de dos elementos")
    check(to_list(reverse_list(build_list([1]))) == [1], "EJ7 lista de un elemento")
    check(to_list(reverse_list(build_list([]))) == [], "EJ7 lista vacia")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
