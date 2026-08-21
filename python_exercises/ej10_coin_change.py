# EJ 10 — Coin Change (programacion dinamica)
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej10_coin_change.py
#   3. Cronométrate: apunta a ~20-25 min.
#   4. Solo si te atascas, mira solutions/ej10_coin_change.py.

import sys
from typing import List


# ===========================================================================
# EJ 10 — Coin Change
#   Dado un array `coins` con las denominaciones disponibles (cantidad
#   ilimitada de cada una) y una cantidad `amount`, devuelve el número
#   mínimo de monedas necesario para formar exactamente `amount`, o -1 si
#   es imposible. Complejidad esperada: O(amount * len(coins)), DP bottom-up.
# ---------------------------------------------------------------------------
def coin_change2(coins: List[int], amount: int) -> int:
    coins_sort = sorted(coins, reverse="True")
    sol = []
    res = amount
    count = 0
    i = 0
    while res  > 0:
        res = res - coins_sort[i]
        if res < 0:
            # Exceeded, go to next coin
            res = res + coins_sort[i]
            i += 1
            if i == len(coins):
                break
        else:
            sol.append(coins_sort[i])
            count += 1

    print("amount: ", amount, " coins: ", coins, " sol: ", sol)
    if res > 0:
        return -1

    print("amount: ", amount, " coins: ", coins, " sol: ", sol)
    return count

def coin_change(coins: List[int], amount: int) -> int:
    INF = float("inf")
    dp = [0] + [INF] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and dp[a - c] + 1 < dp[a]:
                dp[a] = dp[a - c] + 1
    return dp[amount] if dp[amount] != INF else -1

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
    check(coin_change([1, 2, 5], 11) == 3, "EJ10 caso general -> 3 monedas (5+5+1)")
    check(coin_change([3, 2], 10) == 4, "EJ10 caso con repetidas -> 4 monedas (3+3+2+2)")
    check(coin_change([2], 3) == -1, "EJ10 cantidad imposible -> -1")
    check(coin_change([1], 0) == 0, "EJ10 amount 0 -> 0 monedas")
    check(coin_change([1], 2) == 2, "EJ10 solo monedas de 1")
    check(coin_change([2, 5, 10, 1], 27) == 4, "EJ10 combinacion optima -> 4 monedas")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
