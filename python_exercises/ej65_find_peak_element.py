# EJ 65 — Find Peak Element (busqueda binaria)
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej65_find_peak_element.py
#   3. Cronométrate: apunta a ~20-25 min.
#   4. Solo si te atascas, mira solutions/ej65_find_peak_element.py.

import sys
from typing import List


def is_peak(nums: List[int], idx: int) -> bool:
    """Un elemento es un pico si es estrictamente mayor que sus vecinos
    (los limites del array cuentan como -infinito)."""
    left_ok = idx == 0 or nums[idx - 1] < nums[idx]
    right_ok = idx == len(nums) - 1 or nums[idx] > nums[idx + 1]
    return left_ok and right_ok


# ===========================================================================
# EJ 65 — Find Peak Element
#   Un "pico" es un elemento estrictamente mayor que sus vecinos
#   inmediatos. Dado un array `nums` donde nums[i] != nums[i+1] para
#   todo i, y asumiendo nums[-1] = nums[n] = -infinito, devuelve el
#   índice de CUALQUIER pico (si hay varios, cualquiera es válido).
#   Complejidad esperada: O(log n) tiempo. Pista: búsqueda binaria. Si
#   nums[mid] < nums[mid + 1], la pendiente sube hacia la derecha, así
#   que hay garantizado un pico en [mid + 1, right]. Si no, hay un pico
#   garantizado en [left, mid].
# ---------------------------------------------------------------------------
def find_peak_element(nums: List[int]) -> int:
    # TODO
    raise NotImplementedError


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
    check(find_peak_element([1, 2, 3, 1]) == 2, "EJ65 pico unico en el medio")
    check(is_peak([1, 2, 1, 3, 5, 6, 4], find_peak_element([1, 2, 1, 3, 5, 6, 4])),
          "EJ65 varios picos posibles, cualquiera vale")
    check(find_peak_element([1]) == 0, "EJ65 un solo elemento")
    check(find_peak_element([1, 2]) == 1, "EJ65 creciente hasta el borde")
    check(find_peak_element([2, 1]) == 0, "EJ65 decreciente desde el borde")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
