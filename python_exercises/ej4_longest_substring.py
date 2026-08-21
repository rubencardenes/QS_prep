# EJ 4 — Longest Substring Without Repeating Characters (ventana deslizante)
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej4_longest_substring.py
#   3. Cronométrate: apunta a ~15-20 min.
#   4. Solo si te atascas, mira solutions/ej4_longest_substring.py.

import sys


# ===========================================================================
# EJ 4 — Longest Substring Without Repeating Characters
#   Devuelve la longitud de la subcadena más larga de `s` sin caracteres
#   repetidos. Usa una ventana deslizante con dos punteros y un dict para
#   saber qué hay dentro de la ventana. Complejidad esperada: O(n).
# ---------------------------------------------------------------------------
def length_of_longest_substring(s: str) -> int:
    # Use two pointers, one to the first, second to the last 
    first, last , L = 0, 1, 1
    if len(s) == 0:
        return 0
    sub = s[0]
    for i, c in enumerate(s[1:]):
        last = i + 2
        if c not in sub:
            sub = s[first:last]
            if len(sub) > L:
                L = len(sub)
        else:
            first = i+2

    return L

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
    check(length_of_longest_substring("abcabcbb") == 3, "EJ4 caso general 'abcabcbb' -> 3")
    check(length_of_longest_substring("bbbbb") == 1, "EJ4 todo repetido -> 1")
    check(length_of_longest_substring("pwwkew") == 3, "EJ4 'pwwkew' -> 3")
    check(length_of_longest_substring("") == 0, "EJ4 cadena vacia -> 0")
    check(length_of_longest_substring(" ") == 1, "EJ4 un solo caracter -> 1")
    check(length_of_longest_substring("dvdf") == 3, "EJ4 solape de ventana 'dvdf' -> 3")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
