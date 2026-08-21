# EJ 39 — Middle of the Linked List (punteros lento/rapido)  [warm-up]
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej39_middle_linked_list.py
#   3. Cronométrate: apunta a ~15 min.
#   4. Solo si te atascas, mira solutions/ej39_middle_linked_list.py.

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
# EJ 39 — Middle of the Linked List
#   Devuelve el nodo del medio de una lista enlazada. Si hay dos nodos
#   centrales (longitud par), devuelve el SEGUNDO de los dos. No cuentes
#   la longitud en una pasada previa: hazlo con dos punteros, uno que
#   avanza de 1 en 1 y otro de 2 en 2. Complejidad esperada: O(n) tiempo,
#   O(1) espacio.
# ---------------------------------------------------------------------------
def middle_node(head: Optional[ListNode]) -> Optional[ListNode]:
    if head is None:
        return None
    f = head
    s = head
    # print(to_list(head))
    while f is not None and f.next is not None:
        f = f.next.next
        s = s.next
    return s


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
