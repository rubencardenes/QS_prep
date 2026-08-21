# EJ 56 — Letter Combinations of a Phone Number (backtracking)
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej56_letter_combinations_phone.py
#   3. Cronométrate: apunta a ~20-25 min.
#   4. Solo si te atascas, mira solutions/ej56_letter_combinations_phone.py.

import sys
from typing import List


# ===========================================================================
# EJ 56 — Letter Combinations of a Phone Number
#   Dado un string `digits` con dígitos del 2 al 9, devuelve todas las
#   combinaciones de letras que ese número podría representar, según el
#   mapeo clásico del teclado telefónico:
#     2->abc  3->def  4->ghi  5->jkl  6->mno  7->pqrs  8->tuv  9->wxyz
#   Si `digits` está vacío, devuelve una lista vacía.
#   Complejidad esperada: O(4^n * n) en el peor caso (dígitos 7 y 9 dan
#   4 letras). Pista: backtracking dígito a dígito, acumulando el
#   prefijo de letras elegido hasta ahora.
# ---------------------------------------------------------------------------
def letter_combinations(digits: str) -> List[str]:
    if digits == "":
        return []
    print(f"{digits=}")
    coding = {}
    coding["2"] = ["a", "b", "c"]
    coding["3"] = ["d", "e", "f"]
    coding["4"] = ["g", "h", "i"]
    coding["5"] = ["j", "k", "l"]
    coding["6"] = ["m", "n", "o"]
    coding["7"] = ["p", "q", "r", "s"]
    coding["8"] = ["t", "u", "v"]
    coding["9"] = ["w", "x", "y", "z"]

    result = []
    def backtrack(comb, i):
        if len(comb) == len(digits):
            result.append(comb)
            return
        for letter in coding[digits[i]]:
            backtrack(comb + letter, i+1)

    backtrack("", 0)
    print("result ", result)
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
