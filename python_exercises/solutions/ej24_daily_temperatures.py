# EJ 24 — Daily Temperatures — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej24_daily_temperatures.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import sys
from typing import List


# ---------------------------------------------------------------------------
# EJ 24 — Daily Temperatures. Complejidad: O(n).
# Pila monotona decreciente de indices: al ver una temperatura mas alta que
# la del indice en el tope de la pila, esa temperatura "resuelve" el dia
# guardado (se calcula la distancia y se desapila); se sigue asi hasta que
# la pila queda vacia o el tope ya no es superado, y entonces se apila el
# indice actual.
def daily_temperatures(temperatures: List[int]) -> List[int]:
    result = [0] * len(temperatures)
    stack: List[int] = []  # indices con temperatura aun sin superar
    for i, t in enumerate(temperatures):
        while stack and temperatures[stack[-1]] < t:
            prev = stack.pop()
            result[prev] = i - prev
        stack.append(i)
    return result


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
    check(daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73]) == [1, 1, 4, 2, 1, 1, 0, 0],
          "EJ24 caso general del enunciado")

    check(daily_temperatures([30, 40, 50, 60]) == [1, 1, 1, 0],
          "EJ24 temperaturas estrictamente crecientes")

    check(daily_temperatures([30, 60, 90]) == [1, 1, 0],
          "EJ24 cada dia mas caliente que el anterior")

    check(daily_temperatures([90, 60, 30]) == [0, 0, 0],
          "EJ24 temperaturas estrictamente decrecientes")

    check(daily_temperatures([70]) == [0], "EJ24 un solo dia")

    check(daily_temperatures([70, 70, 70]) == [0, 0, 0],
          "EJ24 temperaturas iguales no cuentan como mas calidas")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
