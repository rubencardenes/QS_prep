# EJ 44 — Longest Palindromic Substring — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej44_longest_palindromic_substring.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import sys


# ---------------------------------------------------------------------------
# EJ 44 — Longest Palindromic Substring. Complejidad: O(n^2) tiempo, O(1)
# espacio extra.
# Para cada uno de los 2n-1 centros posibles (cada caracter, para
# palindromos de longitud impar, y cada hueco entre caracteres, para
# longitud par) se expande hacia afuera mientras los extremos coincidan,
# y se guarda el palindromo mas largo encontrado.
def _expand(s: str, left: int, right: int) -> str:
    while left >= 0 and right < len(s) and s[left] == s[right]:
        left -= 1
        right += 1
    return s[left + 1:right]


def longest_palindrome(s: str) -> str:
    best = ""
    for i in range(len(s)):
        odd = _expand(s, i, i)
        if len(odd) > len(best):
            best = odd
        even = _expand(s, i, i + 1)
        if len(even) > len(best):
            best = even
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


def is_valid_answer(s: str, answer: str, expected_len: int) -> bool:
    """Comprueba que `answer` sea un palindromo de la longitud esperada
    y que aparezca realmente como subcadena de `s` (sin exigir un valor
    exacto, ya que puede haber varias respuestas validas)."""
    return len(answer) == expected_len and answer == answer[::-1] and answer in s


def main() -> None:
    check(is_valid_answer("babad", longest_palindrome("babad"), 3),
          "EJ44 dos respuestas validas posibles (bab / aba)")
    check(longest_palindrome("cbbd") == "bb", "EJ44 respuesta unica")
    check(longest_palindrome("a") == "a", "EJ44 un solo caracter")
    check(longest_palindrome("") == "", "EJ44 cadena vacia")
    check(is_valid_answer("ac", longest_palindrome("ac"), 1),
          "EJ44 sin palindromos de mas de 1 caracter")
    check(longest_palindrome("forgeeksskeegfor") == "geeksskeeg",
          "EJ44 palindromo largo en medio de la cadena")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
