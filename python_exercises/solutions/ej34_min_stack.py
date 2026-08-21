# EJ 34 — Min Stack — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej34_min_stack.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import sys


# ---------------------------------------------------------------------------
# EJ 34 — Min Stack. Complejidad: O(1) para las cuatro operaciones.
# Ademas de la pila normal, se mantiene una pila paralela `mins` donde
# cada posicion guarda el minimo de la pila principal hasta ese punto.
# Al apilar, se empuja min(val, minimo actual); al desapilar, se
# desapilan ambas pilas a la vez, asi que el tope de `mins` siempre
# refleja el minimo correcto para el estado actual de la pila.
class MinStack:
    def __init__(self):
        self._stack = []
        self._mins = []

    def push(self, val: int) -> None:
        self._stack.append(val)
        current_min = val if not self._mins else min(val, self._mins[-1])
        self._mins.append(current_min)

    def pop(self) -> None:
        self._stack.pop()
        self._mins.pop()

    def top(self) -> int:
        return self._stack[-1]

    def get_min(self) -> int:
        return self._mins[-1]


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
    s = MinStack()
    s.push(-2)
    s.push(0)
    s.push(-3)
    check(s.get_min() == -3, "EJ34 minimo tras tres push")
    s.pop()
    check(s.top() == 0, "EJ34 top tras pop")
    check(s.get_min() == -2, "EJ34 minimo se actualiza tras el pop")

    s2 = MinStack()
    s2.push(5)
    check(s2.top() == 5 and s2.get_min() == 5, "EJ34 un solo elemento")
    s2.push(3)
    s2.push(3)
    check(s2.get_min() == 3, "EJ34 minimo repetido")
    s2.pop()
    check(s2.get_min() == 3, "EJ34 minimo repetido sigue siendo el minimo tras un pop")
    s2.pop()
    check(s2.get_min() == 5, "EJ34 minimo vuelve al valor anterior")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
