# EJ 4 — Longest Substring Without Repeating Characters — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej4_longest_substring.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import sys


# ---------------------------------------------------------------------------
# EJ 4 — Longest Substring Without Repeating Characters. Complejidad: O(n).
# Ventana [start, i]: si el caracter actual ya está dentro de la ventana,
# salta `start` justo después de su última aparición.
def length_of_longest_substring(s: str) -> int:
    last_seen = {}
    start = 0
    best = 0
    for i, ch in enumerate(s):
        if ch in last_seen and last_seen[ch] >= start:
            start = last_seen[ch] + 1
        last_seen[ch] = i
        best = max(best, i - start + 1)
    return best


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
