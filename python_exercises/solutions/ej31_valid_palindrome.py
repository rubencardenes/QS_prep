# EJ 31 — Valid Palindrome — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej31_valid_palindrome.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import sys


# ---------------------------------------------------------------------------
# EJ 31 — Valid Palindrome. Complejidad: O(n) tiempo, O(1) espacio extra.
# Dos punteros desde ambos extremos hacia el centro: se saltan los
# caracteres no alfanumericos y se comparan en minusculas; si en algun
# punto difieren, no es palindromo.
def is_palindrome(s: str) -> bool:
    left, right = 0, len(s) - 1
    while left < right:
        while left < right and not s[left].isalnum():
            left += 1
        while left < right and not s[right].isalnum():
            right -= 1
        if s[left].lower() != s[right].lower():
            return False
        left += 1
        right -= 1
    return True


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
