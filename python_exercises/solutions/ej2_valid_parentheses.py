# EJ 2 — Valid Parentheses (pila) — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej2_valid_parentheses.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import sys


# ---------------------------------------------------------------------------
# EJ 2 — Valid Parentheses. Complejidad: O(n) tiempo, O(n) espacio.
# Apila aperturas; ante un cierre, debe coincidir con el tope de la pila.
def is_valid(s: str) -> bool:
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in s:
        if ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
        else:
            stack.append(ch)
    return not stack


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
