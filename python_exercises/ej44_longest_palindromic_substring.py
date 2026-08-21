# EJ 44 — Longest Palindromic Substring (expandir desde el centro)
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej44_longest_palindromic_substring.py
#   3. Cronométrate: apunta a ~20-25 min.
#   4. Solo si te atascas, mira solutions/ej44_longest_palindromic_substring.py.

import sys


# ===========================================================================
# EJ 44 — Longest Palindromic Substring
#   Devuelve la subcadena palíndroma más larga de `s`. Si hay varias con
#   la misma longitud máxima, puedes devolver cualquiera de ellas (el
#   test solo comprueba longitud y que sea un palíndromo válido dentro de
#   `s`, no un valor exacto). Complejidad esperada: O(n^2) tiempo, O(1)
#   espacio extra, expandiendo desde cada centro posible (hay 2n-1
#   centros: n de un solo caracter y n-1 entre caracteres, para cubrir
#   palíndromos de longitud impar y par).
# ---------------------------------------------------------------------------
def longest_palindrome(s: str) -> str:
    if len(s) == 0:
        return ""
    result = s[0]
    Lmax = 1
    print(f"{s=}")
    for i in range(len(s)-1):
        result_ = ""
        # check if s[i] is palindrome center
        f, l = -1, len(s)
        if s[i] == s[i+1]:
            f, l = i, i+1
            result_ = s[f:l+1]
        elif (i+2 < len(s) and s[i] == s[i+2]):
            f, l = i, i+2
            result_ = s[f:l+1]
        while f>=1 and l<len(s)-1 and s[f-1] == s[l+1]:
            f, l = f-1, l+1
            result_ = s[f:l+1]
        if len(result_) > Lmax:
            result = result_
            Lmax = len(result)

    print(f"{result=}")
    return result


# ===========================================================================
#                        TEST HARNESS (no tocar)
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
