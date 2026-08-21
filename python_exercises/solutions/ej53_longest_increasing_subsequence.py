# EJ 53 — Longest Increasing Subsequence — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej53_longest_increasing_subsequence.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import bisect
import sys
from typing import List


# ---------------------------------------------------------------------------
# EJ 53 — Longest Increasing Subsequence. Complejidad: O(n log n) tiempo,
# O(n) espacio.
# `tails[i]` guarda el menor valor final posible de cualquier
# subsecuencia creciente de longitud i + 1 encontrada hasta ahora (no es
# necesariamente una subsecuencia real del array, pero su longitud sí lo
# es). Para cada número, buscamos con bisect_left la primera posición
# donde encaja: si es el final, la subsecuencia más larga crece en uno;
# si no, mejoramos (bajamos) el valor final de una subsecuencia de esa
# longitud, lo que deja más margen para futuros números.
def length_of_lis(nums: List[int]) -> int:
    tails: List[int] = []
    for num in nums:
        pos = bisect.bisect_left(tails, num)
        if pos == len(tails):
            tails.append(num)
        else:
            tails[pos] = num
    return len(tails)


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
