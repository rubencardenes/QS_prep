# EJ 3 — Group Anagrams (hashmap) — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej3_group_anagrams.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import sys
from typing import List


# ---------------------------------------------------------------------------
# EJ 3 — Group Anagrams. Complejidad: O(n * k log k).
# La clave es la palabra con sus letras ordenadas: dos anagramas comparten clave.
def group_anagrams(strs: List[str]) -> List[List[str]]:
    groups = {}
    for s in strs:
        key = "".join(sorted(s))
        groups.setdefault(key, []).append(s)
    return list(groups.values())


# ===========================================================================
#                               TEST HARNESS
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
