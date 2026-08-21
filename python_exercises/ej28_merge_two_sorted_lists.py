# EJ 28 — Merge Two Sorted Lists (lista enlazada)
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej28_merge_two_sorted_lists.py
#   3. Cronométrate: apunta a ~15-20 min.
#   4. Solo si te atascas, mira solutions/ej28_merge_two_sorted_lists.py.

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
# EJ 28 — Merge Two Sorted Lists
#   Dadas dos listas enlazadas ya ordenadas de forma ascendente, fusiónalas
#   en una sola lista ordenada y devuelve su cabeza. Reutiliza los nodos
#   existentes (no crees nodos nuevos). Complejidad esperada: O(n + m).
# ---------------------------------------------------------------------------
def merge_two_lists(l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
    if l1 is None and l2 is None:
        return None
    if l1 is None:
        return l2
    if l2 is None:
        return l1
    print(f"{to_list(l1)} --- {to_list(l2)}")
    prev = None
    while l1 is not None and l2 is not None:
        if l1.val <= l2.val:
            c_pointer = l1
            l1 = l1.next
        else:
            c_pointer = l2
            l2 = l2.next
        if prev is not None:
            prev.next = c_pointer
        else:
            root = c_pointer
        prev = c_pointer
    # Connect pointer to last elements if existing, 
    # because the while lopps stops when one of them ends 
    # so the other can still have elements
    c_pointer.next = l2 if l2 else l1   
    return root


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
    r = merge_two_lists(build_list([1, 2, 4]), build_list([1, 3, 4]))
    check(to_list(r) == [1, 1, 2, 3, 4, 4], "EJ28 caso general intercalado")

    r = merge_two_lists(build_list([]), build_list([]))
    check(to_list(r) == [], "EJ28 ambas listas vacias")

    r = merge_two_lists(build_list([]), build_list([0]))
    check(to_list(r) == [0], "EJ28 una lista vacia")

    r = merge_two_lists(build_list([5]), build_list([1, 2, 3]))
    check(to_list(r) == [1, 2, 3, 5], "EJ28 un elemento se coloca al final")

    r = merge_two_lists(build_list([1, 2, 3]), build_list([4, 5, 6]))
    check(to_list(r) == [1, 2, 3, 4, 5, 6], "EJ28 sin solapamiento")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
