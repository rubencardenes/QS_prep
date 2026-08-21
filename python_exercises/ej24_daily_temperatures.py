# EJ 24 — Daily Temperatures (pila monotona)
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej24_daily_temperatures.py
#   3. Cronométrate: apunta a ~20 min.
#   4. Solo si te atascas, mira solutions/ej24_daily_temperatures.py.

import sys
from typing import List
from collections import deque

# ===========================================================================
# EJ 24 — Daily Temperatures
#   Dado un array `temperatures` con la temperatura de cada día, devuelve
#   un array donde cada posición indica cuántos días hay que esperar hasta
#   que haya una temperatura más alta que la de ese día. Si no hay ningún
#   día futuro más cálido, pon 0. Complejidad esperada: O(n) usando una
#   pila que guarda índices de temperaturas aun sin "resolver".
# ---------------------------------------------------------------------------
def daily_temperatures(temperatures: List[int]) -> List[int]:
   # Recorremos en orden inverso
   stack = deque()
   result = [0 for x in range(len(temperatures))]
   stack.append(len(temperatures) -1)
   for i in range(len(temperatures)-2, -1, -1):
      if temperatures[i] < temperatures[i+1]:
         result[i] = 1
         stack.append(i)
      else:
         while(stack):
            j = stack.pop()
            if (temperatures[j] > temperatures[i]):
               stack.append(j)
               result[i] = j - i
               break
         stack.append(i)
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
