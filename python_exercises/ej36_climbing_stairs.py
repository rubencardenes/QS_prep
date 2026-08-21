# EJ 36 — Climbing Stairs (programacion dinamica)  [warm-up]
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej36_climbing_stairs.py
#   3. Cronométrate: apunta a ~10-15 min.
#   4. Solo si te atascas, mira solutions/ej36_climbing_stairs.py.

import sys


# ===========================================================================
# EJ 36 — Climbing Stairs
#   Hay una escalera de `n` escalones. En cada paso puedes subir 1 o 2
#   escalones. ¿De cuántas formas distintas puedes llegar arriba del
#   todo? Complejidad esperada: O(n) tiempo, O(1) espacio (es una
#   recurrencia tipo Fibonacci).
# ---------------------------------------------------------------------------
def climb_stairs(n: int) -> int:
    if n == 0:
        return 0
    if n == 1:
        return 1
    if n == 2: 
        return 2
    sum_prev2 = 1
    sum_prev1 = 2
    for _ in range(3,n+1):
        sum = sum_prev2 + sum_prev1 
        sum_prev2 = sum_prev1 
        sum_prev1 = sum
    return sum


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
    check(climb_stairs(1) == 1, "EJ36 un escalon")
    check(climb_stairs(2) == 2, "EJ36 dos escalones")
    check(climb_stairs(3) == 3, "EJ36 tres escalones")
    check(climb_stairs(4) == 5, "EJ36 cuatro escalones")
    check(climb_stairs(5) == 8, "EJ36 cinco escalones")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
