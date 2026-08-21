# EJ 53 — Longest Increasing Subsequence (programacion dinamica + busqueda binaria)  [dificil]
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej53_longest_increasing_subsequence.py
#   3. Cronométrate: apunta a ~25-30 min.
#   4. Solo si te atascas, mira solutions/ej53_longest_increasing_subsequence.py.

import sys
from typing import List


# ===========================================================================
# EJ 53 — Longest Increasing Subsequence
#   Dado un array de enteros `nums`, devuelve la longitud de la
#   subsecuencia estrictamente creciente más larga (no hace falta que
#   los elementos sean contiguos en el array).
#   Complejidad esperada: O(n log n) tiempo. Pista: mantén un array
#   `tails` donde tails[i] es el menor valor final posible de una
#   subsecuencia creciente de longitud i + 1; para cada número, sustituye
#   (con búsqueda binaria) la primera cola >= él, o añádelo al final si
#   es mayor que todas.
# ---------------------------------------------------------------------------
def length_of_lis(nums: List[int]) -> int:
    if len(nums) == 0:
        return 0
    L = 1
    for i in range(1,len(nums)):
        if nums[i] > nums[i-1]:
            L += 1 
    return L

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
    check(length_of_lis([10, 9, 2, 5, 3, 7, 101, 18]) == 4,
          "EJ53 secuencia clasica")
    check(length_of_lis([0, 1, 0, 3, 2, 3]) == 4, "EJ53 con repeticiones")
    check(length_of_lis([7, 7, 7, 7, 7, 7, 7]) == 1,
          "EJ53 todos iguales (estrictamente creciente)")
    check(length_of_lis([]) == 0, "EJ53 array vacio")
    check(length_of_lis([1, 2, 3, 4, 5]) == 5, "EJ53 ya esta ordenado")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
