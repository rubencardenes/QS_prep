# EJ 39 — Middle of the Linked List — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej39_middle_linked_list.py
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
# EJ 39 — Middle of the Linked List. Complejidad: O(n) tiempo, O(1)
# espacio.
# Puntero lento avanza un nodo por paso, puntero rapido avanza dos.
# Cuando el rapido llega al final, el lento esta exactamente en el medio
# (y en listas de longitud par, en el segundo de los dos centrales,
# porque el rapido llega un paso antes al final).
def middle_node(head: Optional[ListNode]) -> Optional[ListNode]:
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow


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
    check(to_list(middle_node(build_list([1, 2, 3, 4, 5]))) == [3, 4, 5],
          "EJ39 longitud impar")
    check(to_list(middle_node(build_list([1, 2, 3, 4, 5, 6]))) == [4, 5, 6],
          "EJ39 longitud par: devuelve el segundo de los dos centrales")
    check(to_list(middle_node(build_list([1]))) == [1], "EJ39 un solo nodo")
    check(to_list(middle_node(build_list([1, 2]))) == [2], "EJ39 dos nodos")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
