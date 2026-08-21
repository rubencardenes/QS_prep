# EJ 28 — Merge Two Sorted Lists — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej28_merge_two_sorted_lists.py
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
# EJ 28 — Merge Two Sorted Lists. Complejidad: O(n + m) tiempo, O(1)
# espacio extra (reutiliza los nodos).
# Nodo "dummy" para simplificar el caso del primer nodo del resultado; en
# cada paso se engancha el nodo mas pequeño de las dos cabezas actuales y
# se avanza esa lista. Al final, se engancha el resto de la lista que
# quedó sin agotar.
def merge_two_lists(l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
    dummy = ListNode()
    tail = dummy
    while l1 and l2:
        if l1.val <= l2.val:
            tail.next = l1
            l1 = l1.next
        else:
            tail.next = l2
            l2 = l2.next
        tail = tail.next
    tail.next = l1 if l1 else l2
    return dummy.next


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
