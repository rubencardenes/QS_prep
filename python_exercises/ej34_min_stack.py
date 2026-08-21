# EJ 34 — Min Stack (diseño: pila + pila auxiliar)
#
# CÓMO USARLO
#   1. Rellena los métodos marcados con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej34_min_stack.py
#   3. Cronométrate: apunta a ~20 min.
#   4. Solo si te atascas, mira solutions/ej34_min_stack.py.

import sys


# ===========================================================================
# EJ 34 — Min Stack
#   Implementa una pila que además soporta obtener el mínimo actual en
#   O(1):
#     push(val)  -> apila val.
#     pop()      -> desapila el elemento superior.
#     top()      -> devuelve el elemento superior sin desapilarlo.
#     get_min()  -> devuelve el valor mínimo actualmente en la pila.
#   Las CUATRO operaciones deben ser O(1). Pista: mantén una segunda pila
#   con el mínimo "hasta ese momento" en paralelo a la principal.
# ---------------------------------------------------------------------------
class MinStack:
    def __init__(self):
        self.stack: list[int] = []
        self.stack_min: list[int] = []

    def push(self, val: int) -> None:
        self.stack.append(val)
        if len(self.stack_min) == 0 or val <= self.stack_min[-1]:
            self.stack_min.append(val)

    def pop(self) -> None:
        val = self.stack[-1]
        if val == self.stack_min[-1]:
            self.stack_min.pop()
        self.stack.pop()

    def top(self) -> int:
        if self.stack:
            return self.stack[-1]
        else:
            return None

    def get_min(self) -> int:
        return self.stack_min[-1]


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
