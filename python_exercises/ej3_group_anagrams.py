# EJ 3 — Group Anagrams (hashmap)
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej3_group_anagrams.py
#   3. Cronométrate: apunta a ~15 min.
#   4. Solo si te atascas, mira solutions/ej3_group_anagrams.py.

import sys
from typing import List


# ===========================================================================
# EJ 3 — Group Anagrams
#   Agrupa las cadenas de `strs` que son anagramas entre sí. El orden de
#   los grupos y de las cadenas dentro de cada grupo no importa.
#   Complejidad esperada: O(n * k log k), con k = longitud media de cadena.
# ---------------------------------------------------------------------------
def group_anagrams(strs: List[str]) -> List[List[str]]:
    print(strs)
    groups = {}
    for s in strs:
        key = "".join(sorted(s))
        if key not in groups:
            groups[key] = [s]
        else: 
            groups[key].append(s)
    return [g for g in groups.values()] 

# ===========================================================================
#                        TEST HARNESS (no tocar)
# ===========================================================================
_pass = 0
_fail = 0


def check(ok: bool, name: str) -> None:
    global _pass, _fail
    _pass, _fail = (_pass + 1, _fail) if ok else (_pass, _fail + 1)
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}")


def _normalize(groups: List[List[str]]) -> set:
    return {tuple(sorted(g)) for g in groups}


def main() -> None:
    result = group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"])
    expected = _normalize([["eat", "tea", "ate"], ["tan", "nat"], ["bat"]])
    check(_normalize(result) == expected, "EJ3 agrupa anagramas correctamente")

    check(group_anagrams([""]) == [[""]], "EJ3 cadena vacia")
    check(_normalize(group_anagrams(["a"])) == _normalize([["a"]]), "EJ3 un solo elemento")

    result2 = group_anagrams(["abc", "cba", "bac", "xyz"])
    expected2 = _normalize([["abc", "cba", "bac"], ["xyz"]])
    check(_normalize(result2) == expected2, "EJ3 grupo mixto con no-anagramas")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
