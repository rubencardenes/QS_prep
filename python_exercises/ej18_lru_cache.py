# EJ 18 — LRU Cache (diseño: dict + lista doblemente enlazada)
#
# CÓMO USARLO
#   1. Rellena los métodos marcados con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej18_lru_cache.py
#   3. Cronométrate: apunta a ~25-30 min.
#   4. Solo si te atascas, mira solutions/ej18_lru_cache.py.

import sys


# ===========================================================================
# EJ 18 — LRU Cache
#   Implementa una caché LRU (Least Recently Used) con capacidad fija.
#     get(key)      -> devuelve el valor si existe (y lo marca como usado
#                       recientemente), o -1 si no existe.
#     put(key, val) -> inserta/actualiza el valor. Si al insertar se supera
#                       la capacidad, expulsa la entrada usada menos
#                       recientemente.
#   Ambas operaciones deben ser O(1). Pista: dict para acceso O(1) + lista
#   doblemente enlazada para mantener el orden de uso.
# ---------------------------------------------------------------------------
class LRUCache:
    def __init__(self, capacity: int):
        # TODO
        raise NotImplementedError

    def get(self, key: int) -> int:
        # TODO
        raise NotImplementedError

    def put(self, key: int, value: int) -> None:
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
