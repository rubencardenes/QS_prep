# EJ 25 — Implement Trie / Prefix Tree (diseño)
#
# CÓMO USARLO
#   1. Rellena los métodos marcados con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej25_implement_trie.py
#   3. Cronométrate: apunta a ~20-25 min.
#   4. Solo si te atascas, mira solutions/ej25_implement_trie.py.

import sys


# ===========================================================================
# EJ 25 — Implement Trie (Prefix Tree)
#   Implementa un Trie con tres operaciones:
#     insert(word)        -> inserta la palabra en el trie.
#     search(word)        -> True si la palabra exacta fue insertada.
#     starts_with(prefix)  -> True si alguna palabra insertada empieza por
#                             ese prefijo.
#   Todas las operaciones deben ser O(L) donde L es la longitud de la
#   palabra/prefijo. Pista: cada nodo guarda un dict de {caracter: nodo
#   hijo} y un flag que marca el fin de una palabra.
# ---------------------------------------------------------------------------
class Trie:
    def __init__(self):
        # TODO
        raise NotImplementedError

    def insert(self, word: str) -> None:
        # TODO
        raise NotImplementedError

    def search(self, word: str) -> bool:
        # TODO
        raise NotImplementedError

    def starts_with(self, prefix: str) -> bool:
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
    trie = Trie()
    trie.insert("apple")
    check(trie.search("apple") is True, "EJ25 palabra insertada exacta")
    check(trie.search("app") is False, "EJ25 prefijo no insertado como palabra")
    check(trie.starts_with("app") is True, "EJ25 starts_with sobre prefijo valido")

    trie.insert("app")
    check(trie.search("app") is True, "EJ25 palabra mas corta insertada despues")
    check(trie.search("apples") is False, "EJ25 palabra mas larga no insertada")
    check(trie.starts_with("appl") is True, "EJ25 starts_with sigue funcionando")
    check(trie.starts_with("b") is False, "EJ25 prefijo inexistente")

    trie2 = Trie()
    check(trie2.search("cualquiera") is False, "EJ25 trie vacio no encuentra nada")
    check(trie2.starts_with("") is True, "EJ25 prefijo vacio siempre coincide")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
