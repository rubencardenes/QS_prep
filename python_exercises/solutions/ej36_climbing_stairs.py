# EJ 36 — Climbing Stairs — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej36_climbing_stairs.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import sys


# ---------------------------------------------------------------------------
# EJ 36 — Climbing Stairs. Complejidad: O(n) tiempo, O(1) espacio.
# El numero de formas de llegar al escalon n es la suma de las formas de
# llegar al n-1 (dando un ultimo paso de 1) y al n-2 (dando un ultimo
# paso de 2): es exactamente la recurrencia de Fibonacci. Se calcula
# iterativamente guardando solo los dos ultimos valores.
def climb_stairs(n: int) -> int:
    if n <= 2:
        return n
    prev2, prev1 = 1, 2
    for _ in range(3, n + 1):
        prev2, prev1 = prev1, prev2 + prev1
    return prev1


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
    check(climb_stairs(1) == 1, "EJ36 un escalon")
    check(climb_stairs(2) == 2, "EJ36 dos escalones")
    check(climb_stairs(3) == 3, "EJ36 tres escalones")
    check(climb_stairs(4) == 5, "EJ36 cuatro escalones")
    check(climb_stairs(5) == 8, "EJ36 cinco escalones")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
