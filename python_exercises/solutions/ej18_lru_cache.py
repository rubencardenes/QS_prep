# EJ 18 — LRU Cache — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej18_lru_cache.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import sys


class _Node:
    __slots__ = ("key", "value", "prev", "next")

    def __init__(self, key: int = 0, value: int = 0):
        self.key = key
        self.value = value
        self.prev: "_Node" = None  # type: ignore[assignment]
        self.next: "_Node" = None  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# EJ 18 — LRU Cache. get/put en O(1).
# dict clave->nodo para acceso O(1) + lista doblemente enlazada con dos
# nodos centinela (head/tail) que mantiene el orden de uso: el nodo más
# reciente vive junto a `head`, el menos reciente junto a `tail`.
class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache: dict[int, _Node] = {}
        self.head = _Node()
        self.tail = _Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: _Node) -> None:
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_front(self, node: _Node) -> None:
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        node = self.cache[key]
        self._remove(node)
        self._add_front(node)
        return node.value

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self._remove(self.cache[key])
        node = _Node(key, value)
        self.cache[key] = node
        self._add_front(node)
        if len(self.cache) > self.capacity:
            lru = self.tail.prev
            self._remove(lru)
            del self.cache[lru.key]


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
    cache = LRUCache(2)
    cache.put(1, 1)
    cache.put(2, 2)
    check(cache.get(1) == 1, "EJ18 get de clave existente")
    cache.put(3, 3)  # expulsa la clave 2 (la menos usada recientemente)
    check(cache.get(2) == -1, "EJ18 clave expulsada por capacidad")
    cache.put(4, 4)  # expulsa la clave 1
    check(cache.get(1) == -1, "EJ18 otra clave expulsada")
    check(cache.get(3) == 3, "EJ18 clave 3 sigue presente")
    check(cache.get(4) == 4, "EJ18 clave 4 sigue presente")

    cache2 = LRUCache(1)
    cache2.put(10, 100)
    check(cache2.get(10) == 100, "EJ18 capacidad 1: get tras put")
    cache2.put(20, 200)
    check(cache2.get(10) == -1, "EJ18 capacidad 1: put expulsa la unica clave")
    check(cache2.get(20) == 200, "EJ18 capacidad 1: nueva clave presente")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
