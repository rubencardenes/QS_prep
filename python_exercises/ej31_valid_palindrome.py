# EJ 31 — Valid Palindrome (dos punteros)  [warm-up]
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej31_valid_palindrome.py
#   3. Cronométrate: apunta a ~15 min.
#   4. Solo si te atascas, mira solutions/ej31_valid_palindrome.py.

import sys


# ===========================================================================
# EJ 31 — Valid Palindrome
#   Dada una cadena `s`, determina si es un palíndromo considerando SOLO
#   los caracteres alfanuméricos e ignorando mayúsculas/minúsculas (se
#   ignoran espacios, comas, dos puntos, etc). La cadena vacía tras
#   filtrar cuenta como palíndromo válido. Complejidad esperada: O(n)
#   tiempo, O(1) espacio extra usando dos punteros desde los extremos.
# ---------------------------------------------------------------------------
def is_palindrome2(s: str) -> bool:
    t = ""
    for c in s:
        if c.isalnum():
            t = t + c.lower()
    print(f"{t=}")
    if t == t[::-1]:
        return True
    return False

def is_palindrome(s: str) -> bool:
    # Using two points 
    f, l = 0, len(s)-1
    while f < l:
        if not s[f].isalnum():
            f += 1
            continue
        if not s[l].isalnum():
            l -= 1
            continue
        if s[f].lower() != s[l].lower():
            return False
        else:
            f += 1
            l -= 1
    return True


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
    check(is_palindrome("A man, a plan, a canal: Panama") is True,
          "EJ31 frase clasica con puntuacion y mayusculas")
    check(is_palindrome("race a car") is False, "EJ31 no es palindromo")
    check(is_palindrome(" ") is True, "EJ31 solo espacios (vacio tras filtrar)")
    check(is_palindrome("0P") is False, "EJ31 caracteres alfanumericos distintos")
    check(is_palindrome(".,") is True, "EJ31 solo puntuacion (vacio tras filtrar)")
    check(is_palindrome("Was it a car or a cat I saw?") is True,
          "EJ31 otra frase clasica")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
