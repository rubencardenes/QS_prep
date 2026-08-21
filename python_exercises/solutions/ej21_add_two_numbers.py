# EJ 21 — Add Two Numbers — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej21_add_two_numbers.py
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
# EJ 21 — Add Two Numbers. Complejidad: O(max(n, m)) tiempo, O(max(n, m))
# espacio para el resultado.
# Recorre ambas listas a la vez sumando dígito a dígito junto con el
# arrastre (carry) de la suma anterior. Si una lista es más corta se trata
# como 0. Al final, si queda arrastre, se añade un último nodo.
def add_two_numbers(l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
    dummy = ListNode()
    tail = dummy
    carry = 0
    while l1 or l2 or carry:
        v1 = l1.val if l1 else 0
        v2 = l2.val if l2 else 0
        total = v1 + v2 + carry
        carry, digit = divmod(total, 10)
        tail.next = ListNode(digit)
        tail = tail.next
        l1 = l1.next if l1 else None
        l2 = l2.next if l2 else None
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
