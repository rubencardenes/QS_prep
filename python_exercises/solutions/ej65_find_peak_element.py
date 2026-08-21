# EJ 65 — Find Peak Element — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej65_find_peak_element.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import sys
from typing import List


def is_peak(nums: List[int], idx: int) -> bool:
    """Un elemento es un pico si es estrictamente mayor que sus vecinos
    (los limites del array cuentan como -infinito)."""
    left_ok = idx == 0 or nums[idx - 1] < nums[idx]
    right_ok = idx == len(nums) - 1 or nums[idx] > nums[idx + 1]
    return left_ok and right_ok


# ---------------------------------------------------------------------------
# EJ 65 — Find Peak Element. Complejidad: O(log n) tiempo, O(1) espacio.
# Búsqueda binaria sobre la "pendiente" del array. Si nums[mid] <
# nums[mid + 1], estamos en una pendiente ascendente, así que a la
# derecha de mid tiene que haber un pico (en el peor caso, el propio
# final del array, que actúa como pared con -infinito detrás).
# Descartamos la mitad izquierda. Si no, la pendiente baja (o es un
# pico), y el pico garantizado está en [left, mid], incluyendo mid.
def find_peak_element(nums: List[int]) -> int:
    left, right = 0, len(nums) - 1

    while left < right:
        mid = (left + right) // 2
        if nums[mid] < nums[mid + 1]:
            left = mid + 1
        else:
            right = mid

    return left


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
