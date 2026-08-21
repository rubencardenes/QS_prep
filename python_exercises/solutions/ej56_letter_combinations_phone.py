# EJ 56 — Letter Combinations of a Phone Number — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej56_letter_combinations_phone.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import sys
from typing import List

# ---------------------------------------------------------------------------
# EJ 56 — Letter Combinations of a Phone Number. Complejidad: O(4^n * n)
# tiempo en el peor caso, O(n) espacio de recursión (sin contar la
# salida).
# Backtracking clásico: en cada nivel de la recursión elegimos una letra
# posible para el dígito actual, la añadimos al `path`, recursamos sobre
# el resto de dígitos, y al volver la quitamos (backtrack) para probar
# la siguiente letra.
_DIGIT_TO_LETTERS = {
    "2": "abc", "3": "def", "4": "ghi", "5": "jkl",
    "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz",
}


def letter_combinations(digits: str) -> List[str]:
    if not digits:
        return []

    result: List[str] = []
    path: List[str] = []

    def backtrack(index: int) -> None:
        if index == len(digits):
            result.append("".join(path))
            return
        for letter in _DIGIT_TO_LETTERS[digits[index]]:
            path.append(letter)
            backtrack(index + 1)
            path.pop()

    backtrack(0)
    return result


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
    check(letter_combinations("23") ==
          ["ad", "ae", "af", "bd", "be", "bf", "cd", "ce", "cf"],
          "EJ56 dos digitos")
    check(letter_combinations("") == [], "EJ56 string vacio")
    check(letter_combinations("2") == ["a", "b", "c"], "EJ56 un solo digito")
    check(len(letter_combinations("79")) == 16, "EJ56 digitos de 4 letras (7 y 9)")
    check(letter_combinations("9") == ["w", "x", "y", "z"], "EJ56 digito 9")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
