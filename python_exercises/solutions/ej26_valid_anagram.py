# EJ 26 — Valid Anagram — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej26_valid_anagram.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import sys
from collections import Counter


# ---------------------------------------------------------------------------
# EJ 26 — Valid Anagram. Complejidad: O(n) tiempo, O(1) espacio extra (el
# alfabeto es de tamaño acotado).
# Si las longitudes difieren no pueden ser anagramas. Si coinciden, basta
# comparar el conteo de frecuencias de cada caracter con Counter.
def is_anagram(s: str, t: str) -> bool:
    if len(s) != len(t):
        return False
    return Counter(s) == Counter(t)


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
