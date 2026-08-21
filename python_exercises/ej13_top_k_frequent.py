# EJ 13 — Top K Frequent Elements (heap / bucket sort)
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej13_top_k_frequent.py
#   3. Cronométrate: apunta a ~15-20 min.
#   4. Solo si te atascas, mira solutions/ej13_top_k_frequent.py.

import sys
from typing import List


# ===========================================================================
# EJ 13 — Top K Frequent Elements
#   Devuelve los k elementos más frecuentes de `nums`. Si hay empate en
#   frecuencia, cualquier orden entre ellos es válido (los tests comparan
#   como conjunto). Complejidad esperada: O(n log k) o O(n) con bucket sort.
# ---------------------------------------------------------------------------
def top_k_frequent(nums: List[int], k: int) -> List[int]:
    # Construimos el histograma de frecuencias
    freq = {}
    for n in nums:
        freq.setdefault(n, 0)
        freq[n] += 1
    # Extramos los k mayores 
    freq_v = [(k, v) for k,v in freq.items()]
    a = sorted(freq_v, key = lambda x: x[1], reverse=True)
    result = [x[0] for x in a[:k]]
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
    check(set(top_k_frequent([1, 1, 1, 2, 2, 3], 2)) == {1, 2}, "EJ13 caso general k=2")
    check(set(top_k_frequent([1], 1)) == {1}, "EJ13 un solo elemento")
    check(len(top_k_frequent([1, 2, 3, 4], 4)) == 4, "EJ13 k igual al numero de distintos")
    check(set(top_k_frequent([4, 4, 4, 5, 5, 6], 1)) == {4}, "EJ13 el mas frecuente claro")
    check(set(top_k_frequent([7, 7, 8, 8, 9], 2)) == {7, 8}, "EJ13 empate entre dos")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
