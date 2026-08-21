# EJ 42 — 3Sum — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej42_three_sum.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import sys
from typing import List


# ---------------------------------------------------------------------------
# EJ 42 — 3Sum. Complejidad: O(n^2) tiempo, O(log n) a O(n) espacio (por
# el sort).
# Se ordena el array. Para cada indice i (evitando duplicados
# consecutivos), se buscan dos punteros left/right en el resto del array
# que sumen -nums[i], moviendolos como en Two Sum sobre array ordenado.
# Ordenar permite tanto los dos punteros como saltar duplicados
# facilmente comparando con el valor anterior.
def three_sum(nums: List[int]) -> List[List[int]]:
    nums = sorted(nums)
    n = len(nums)
    result = []
    for i in range(n - 2):
        if i > 0 and nums[i] == nums[i - 1]:
            continue
        if nums[i] > 0:
            break
        left, right = i + 1, n - 1
        while left < right:
            total = nums[i] + nums[left] + nums[right]
            if total < 0:
                left += 1
            elif total > 0:
                right -= 1
            else:
                result.append([nums[i], nums[left], nums[right]])
                left += 1
                right -= 1
                while left < right and nums[left] == nums[left - 1]:
                    left += 1
                while left < right and nums[right] == nums[right + 1]:
                    right -= 1
    return result


# ===========================================================================
#                               TEST HARNESS
# ===========================================================================
_pass = 0
_fail = 0


def check(ok: bool, name: str) -> None:
    global _pass, _fail
    _pass, _fail = (_pass + 1, _fail) if ok else (_pass, _fail + 1)
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}")


def normalize(triplets: List[List[int]]):
    """Convierte la lista de trios en un conjunto de tuplas ordenadas,
    para comparar resultados sin importar el orden."""
    return sorted(tuple(sorted(t)) for t in triplets)


def main() -> None:
    check(normalize(three_sum([-1, 0, 1, 2, -1, -4])) == normalize([[-1, -1, 2], [-1, 0, 1]]),
          "EJ42 caso general del enunciado")
    check(three_sum([]) == [], "EJ42 array vacio")
    check(three_sum([0, 1, 1]) == [], "EJ42 sin ningun trio valido")
    check(normalize(three_sum([0, 0, 0])) == normalize([[0, 0, 0]]), "EJ42 trio de ceros")
    check(normalize(three_sum([0, 0, 0, 0])) == normalize([[0, 0, 0]]),
          "EJ42 deduplica trios repetidos")
    check(normalize(three_sum([-2, 0, 1, 1, 2])) == normalize([[-2, 0, 2], [-2, 1, 1]]),
          "EJ42 varios trios validos")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
