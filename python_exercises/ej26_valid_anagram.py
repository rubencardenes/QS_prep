# EJ 26 — Valid Anagram (hashmap)  [warm-up]
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej26_valid_anagram.py
#   3. Cronométrate: apunta a ~10-15 min.
#   4. Solo si te atascas, mira solutions/ej26_valid_anagram.py.

import sys


# ===========================================================================
# EJ 26 — Valid Anagram
#   Dadas dos cadenas `s` y `t`, devuelve True si `t` es un anagrama de
#   `s` (usa exactamente las mismas letras, con la misma frecuencia cada
#   una, en cualquier orden). Complejidad esperada: O(n) usando un
#   contador de frecuencias.
# ---------------------------------------------------------------------------
def is_anagram(s: str, t: str) -> bool:
    count_s, count_t = {}, {}
    if len(s) != len(t):
        return False
    for i in range(len(s)):
        count_s.setdefault(s[i], 0)
        count_s[s[i]] += 1
        count_t.setdefault(t[i], 0)
        count_t[t[i]] += 1
    if count_s == count_t:
        return True
    return False


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
    check(is_anagram("anagram", "nagaram") is True, "EJ26 anagrama valido")
    check(is_anagram("rat", "car") is False, "EJ26 mismas letras distintas, no anagrama")
    check(is_anagram("a", "ab") is False, "EJ26 longitudes distintas")
    check(is_anagram("", "") is True, "EJ26 dos cadenas vacias")
    check(is_anagram("aacc", "ccac") is False, "EJ26 frecuencias distintas")
    check(is_anagram("listen", "silent") is True, "EJ26 anagrama clasico")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
