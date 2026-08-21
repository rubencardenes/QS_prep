# EJ 49 — Word Break — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej49_word_break.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import sys
from typing import List


# ---------------------------------------------------------------------------
# EJ 49 — Word Break. Complejidad: O(n^2) tiempo, O(n) espacio.
# dp[i] indica si s[:i] (los primeros i caracteres) se puede segmentar
# con palabras del diccionario. dp[0] = True (string vacio, caso base).
# Para cada posicion i, probamos todos los cortes j < i: si dp[j] es
# True y s[j:i] es una palabra valida, entonces dp[i] tambien es True.
def word_break(s: str, word_dict: List[str]) -> bool:
    words = set(word_dict)
    n = len(s)
    dp = [False] * (n + 1)
    dp[0] = True

    for i in range(1, n + 1):
        for j in range(i):
            if dp[j] and s[j:i] in words:
                dp[i] = True
                break

    return dp[n]


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
