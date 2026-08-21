# EJ 10 — Coin Change (programacion dinamica) — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej10_coin_change.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import sys
from typing import List


# ---------------------------------------------------------------------------
# EJ 10 — Coin Change. Complejidad: O(amount * len(coins)).
# dp[a] = número mínimo de monedas para formar `a`. dp[0] = 0; para cada
# cantidad se prueba añadir una moneda más sobre un subproblema ya resuelto.
def coin_change(coins: List[int], amount: int) -> int:
    INF = float("inf")
    dp = [0] + [INF] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and dp[a - c] + 1 < dp[a]:
                dp[a] = dp[a - c] + 1
    return dp[amount] if dp[amount] != INF else -1


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
    check(coin_change([1, 2, 5], 11) == 3, "EJ10 caso general -> 3 monedas (5+5+1)")
    check(coin_change([2], 3) == -1, "EJ10 cantidad imposible -> -1")
    check(coin_change([1], 0) == 0, "EJ10 amount 0 -> 0 monedas")
    check(coin_change([1], 2) == 2, "EJ10 solo monedas de 1")
    check(coin_change([2, 5, 10, 1], 27) == 4, "EJ10 combinacion optima -> 4 monedas")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
