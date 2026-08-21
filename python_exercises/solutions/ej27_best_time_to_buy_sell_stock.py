# EJ 27 — Best Time to Buy and Sell Stock — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej27_best_time_to_buy_sell_stock.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import sys
from typing import List


# ---------------------------------------------------------------------------
# EJ 27 — Best Time to Buy and Sell Stock. Complejidad: O(n) tiempo, O(1)
# espacio.
# Recorre los precios una vez guardando el mínimo visto hasta ahora
# (mejor día de compra hasta el momento) y, en cada día, calcula el
# beneficio de vender ese día con ese mínimo, quedandose con el mejor.
def max_profit(prices: List[int]) -> int:
    if not prices:
        return 0
    min_price = prices[0]
    best = 0
    for price in prices[1:]:
        best = max(best, price - min_price)
        min_price = min(min_price, price)
    return best


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
