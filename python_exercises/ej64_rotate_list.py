# EJ 64 — Rotate List (lista enlazada)
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej64_rotate_list.py
#   3. Cronométrate: apunta a ~20-25 min.
#   4. Solo si te atascas, mira solutions/ej64_rotate_list.py.

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
# EJ 64 — Rotate List
#   Dada la cabeza de una lista enlazada y un entero `k`, rota la lista
#   hacia la derecha `k` posiciones (el último elemento pasa a ser el
#   primero, y así sucesivamente) y devuelve la nueva cabeza.
#   Complejidad esperada: O(n) tiempo, O(1) espacio extra.
#   Pista: calcula la longitud de la lista, reduce k con `k %= n`
#   (rotar n veces devuelve la lista a su estado original). Cierra la
#   lista en un círculo (cola.next = cabeza), avanza hasta la nueva
#   cola (en la posición n - k - 1) y rompe el enlace ahí.
# ---------------------------------------------------------------------------
def rotate_right(head: Optional[ListNode], k: int) -> Optional[ListNode]:
    # TODO
    raise NotImplementedError


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
