# EJ 21 — Add Two Numbers (lista enlazada)
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej21_add_two_numbers.py
#   3. Cronométrate: apunta a ~20 min.
#   4. Solo si te atascas, mira solutions/ej21_add_two_numbers.py.

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
# EJ 21 — Add Two Numbers
#   Dos números no negativos vienen representados como listas enlazadas en
#   orden inverso (la unidad primero); cada nodo contiene un solo dígito.
#   Suma los dos números y devuelve el resultado también como lista
#   enlazada en orden inverso. Ej: [2,4,3] + [5,6,4] representa 342 + 465,
#   y el resultado [7,0,8] representa 807.
# ---------------------------------------------------------------------------
def add_two_numbers(l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:

    root = ListNode()
    current = root
    i = 0
    resto = 0
    while l1 is not None or l2 is not None:
        if i > 0:
           current = ListNode()
           previous.next = current
        v1 = l1.val if l1 else 0
        v2 = l2.val if l2 else 0
        current.val = (v1 + v2 + resto) % 10
        resto = (v1 + v2 + resto) // 10
        previous = current
        l1 = l1.next if l1 else None
        l2 = l2.next if l2 else None
        i += 1

    if resto > 0:
        current = ListNode(1)
        previous.next = current

    print(to_list(root))
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
    r = add_two_numbers(build_list([2, 4, 3]), build_list([5, 6, 4]))
    check(to_list(r) == [7, 0, 8], "EJ21 caso general (342 + 465 = 807)")

    r = add_two_numbers(build_list([0]), build_list([0]))
    check(to_list(r) == [0], "EJ21 cero mas cero")

    r = add_two_numbers(build_list([9, 9, 9, 9, 9, 9, 9]), build_list([9, 9, 9, 9]))
    check(to_list(r) == [8, 9, 9, 9, 0, 0, 0, 1], "EJ21 arrastre en cascada")

    r = add_two_numbers(build_list([5]), build_list([5]))
    check(to_list(r) == [0, 1], "EJ21 arrastre genera un digito nuevo")

    r = add_two_numbers(build_list([1, 8]), build_list([0]))
    check(to_list(r) == [1, 8], "EJ21 uno de los numeros es cero")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
