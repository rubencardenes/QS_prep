# EJ 49 — Word Break (programacion dinamica: strings)
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej49_word_break.py
#   3. Cronométrate: apunta a ~20-25 min.
#   4. Solo si te atascas, mira solutions/ej49_word_break.py.

import sys
from typing import List


# ===========================================================================
# EJ 49 — Word Break
#   Dado un string `s` y una lista de palabras `word_dict`, determina si
#   `s` se puede segmentar en una secuencia de una o más palabras del
#   diccionario, separadas por espacios (las palabras se pueden repetir).
#   Complejidad esperada: O(n^2) tiempo, O(n) espacio, con n = len(s).
#   Pista: dp[i] = True si s[:i] se puede segmentar; dp[0] = True.
# ---------------------------------------------------------------------------
def word_break(s: str, word_dict: List[str]) -> bool:
    print(f"{s=} {word_dict=}")
    f = 0
    for i in range(len(s)):
      if s[f:i+1] in word_dict:
          f = i+1
    if f == len(s):
        return True
    else:
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
    check(word_break("leetcode", ["leet", "code"]) is True,
          "EJ49 se segmenta en dos palabras")
    check(word_break("applepenapple", ["apple", "pen"]) is True,
          "EJ49 palabras repetidas")
    check(word_break("catsandog", ["cats", "dog", "sand", "and", "cat"]) is False,
          "EJ49 no se puede segmentar")
    check(word_break("a", []) is False, "EJ49 diccionario vacio")
    check(word_break("", ["a"]) is True, "EJ49 string vacio")
    check(word_break("cars", ["car", "ca", "rs"]) is True,
          "EJ49 requiere elegir la particion correcta")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
