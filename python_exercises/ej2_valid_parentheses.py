# EJ 2 — Valid Parentheses (pila)
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej2_valid_parentheses.py
#   3. Cronométrate: apunta a ~10-15 min.
#   4. Solo si te atascas, mira solutions/ej2_valid_parentheses.py.

import sys
from collections import deque

# ===========================================================================
# EJ 2 — Valid Parentheses
#   Dada una cadena que contiene solo '()[]{}',  determina si está bien
#   formada: cada apertura tiene su cierre correspondiente y en el orden
#   correcto. Complejidad esperada: O(n) tiempo, O(n) espacio.
# ---------------------------------------------------------------------------
def is_valid(s: str) -> bool:
    result = True
    par_stack = deque()
    for c in s:
        if c == "(" or c == "[" or c == "{":
            par_stack.append(c)
        if c == ")" or c == "]" or c == "}":
            if len(par_stack) == 0:
                return False 
            r = par_stack.pop()
            # Now check if r matchs c:
            if r == "(" and c != ")":
                return False
            if r == "[" and c != "]":
                return False
            if r == "{" and c != "}":
                return False

    if len(par_stack):
        result = False
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
    check(is_valid("()") is True, "EJ2 par simple")
    check(is_valid("()[]{}") is True, "EJ2 varios pares consecutivos")
    check(is_valid("(]") is False, "EJ2 tipos de cierre no coinciden")
    check(is_valid("([)]") is False, "EJ2 orden de cierre incorrecto")
    check(is_valid("{[]}") is True, "EJ2 anidados correctamente")
    check(is_valid("(") is False, "EJ2 apertura sin cerrar")
    check(is_valid("") is True, "EJ2 cadena vacia")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
