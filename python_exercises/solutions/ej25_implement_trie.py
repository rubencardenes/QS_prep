# EJ 25 — Implement Trie / Prefix Tree — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej25_implement_trie.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import sys


# ---------------------------------------------------------------------------
# EJ 25 — Implement Trie. Complejidad: O(L) por operacion, donde L es la
# longitud de la palabra/prefijo.
# Cada nodo es un dict {caracter: nodo hijo} mas un flag `is_word` que
# marca si el camino recorrido hasta ese nodo forma una palabra completa
# insertada. insert/search/starts_with simplemente recorren o crean el
# camino caracter a caracter.
class _TrieNode:
    def __init__(self):
        self.children: dict = {}
        self.is_word: bool = False


class Trie:
    def __init__(self):
        self.root = _TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = _TrieNode()
            node = node.children[ch]
        node.is_word = True

    def _find_node(self, prefix: str):
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node

    def search(self, word: str) -> bool:
        node = self._find_node(word)
        return node is not None and node.is_word

    def starts_with(self, prefix: str) -> bool:
        return self._find_node(prefix) is not None


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
