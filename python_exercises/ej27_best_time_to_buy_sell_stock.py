# EJ 27 — Best Time to Buy and Sell Stock (greedy)  [warm-up]
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej27_best_time_to_buy_sell_stock.py
#   3. Cronométrate: apunta a ~15 min.
#   4. Solo si te atascas, mira solutions/ej27_best_time_to_buy_sell_stock.py.

import sys
from typing import List
import math

# ===========================================================================
# EJ 27 — Best Time to Buy and Sell Stock
#   `prices[i]` es el precio de la acción el día i. Solo puedes hacer UNA
#   compra y UNA venta (la venta debe ser en un día posterior a la
#   compra). Devuelve el máximo beneficio posible, o 0 si no conviene
#   comprar nunca. Complejidad esperada: O(n), un solo recorrido.
# ---------------------------------------------------------------------------
def max_profit(prices: List[int]) -> int:
    max_benefit = 0
    current_min = 0
    for i in range(1, len(prices)):
        if prices[i] <= prices[current_min]:
            current_min = i
        if prices[i] - prices[current_min] > max_benefit:
            max_benefit = prices[i] - prices[current_min]
    print(f"{prices=} {max_benefit=} {current_min=}")
    return max_benefit


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
    check(max_profit([7, 1, 5, 3, 6, 4]) == 5, "EJ27 caso general (compra dia 2, vende dia 5)")
    check(max_profit([7, 6, 4, 3, 1]) == 0, "EJ27 precios solo bajan, no conviene comprar")
    check(max_profit([1, 2]) == 1, "EJ27 dos dias")
    check(max_profit([2, 4, 1, 7]) == 6, "EJ27 el minimo no es el primer dia")
    check(max_profit([]) == 0, "EJ27 lista vacia")
    check(max_profit([5]) == 0, "EJ27 un solo dia")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
