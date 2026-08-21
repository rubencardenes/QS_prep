# EJ 64 — Rotate List — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej64_rotate_list.py
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
# EJ 64 — Rotate List. Complejidad: O(n) tiempo, O(1) espacio extra.
# Primero recorremos la lista para medir su longitud n y quedarnos con
# la cola. Reducimos k con k %= n (si k es multiplo de n, la lista
# vuelve a quedar igual). Cerramos la lista en un anillo (cola.next =
# cabeza) y avanzamos n - k - 1 pasos desde la cabeza para encontrar la
# nueva cola; el siguiente nodo es la nueva cabeza, y rompemos el
# anillo ahi.
def rotate_right(head: Optional[ListNode], k: int) -> Optional[ListNode]:
    if head is None or head.next is None:
        return head

    length = 1
    tail = head
    while tail.next:
        tail = tail.next
        length += 1

    k %= length
    if k == 0:
        return head

    tail.next = head  # cerramos el anillo

    steps_to_new_tail = length - k - 1
    new_tail = head
    for _ in range(steps_to_new_tail):
        new_tail = new_tail.next

    new_head = new_tail.next
    new_tail.next = None
    return new_head


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
    check(to_list(rotate_right(build_list([1, 2, 3, 4, 5]), 2)) ==
          [4, 5, 1, 2, 3], "EJ64 rota dos posiciones")
    check(to_list(rotate_right(build_list([0, 1, 2]), 4)) == [2, 0, 1],
          "EJ64 k mayor que la longitud de la lista")
    check(to_list(rotate_right(build_list([]), 0)) == [], "EJ64 lista vacia")
    check(to_list(rotate_right(build_list([1]), 99)) == [1],
          "EJ64 un solo nodo, cualquier k")
    check(to_list(rotate_right(build_list([1, 2]), 1)) == [2, 1],
          "EJ64 dos nodos")
    check(to_list(rotate_right(build_list([1, 2, 3]), 0)) == [1, 2, 3],
          "EJ64 k=0 no rota nada")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
