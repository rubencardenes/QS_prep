# EJ 15 — Subsets (backtracking)
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej15_subsets.py
#   3. Cronométrate: apunta a ~15-20 min.
#   4. Solo si te atascas, mira solutions/ej15_subsets.py.

import sys
from typing import List


# ===========================================================================
# EJ 15 — Subsets
#   Dado un array `nums` de enteros distintos, devuelve todos los
#   subconjuntos posibles (el conjunto potencia), incluyendo el vacío y el
#   propio array. El orden de los subconjuntos y de sus elementos no
#   importa. Complejidad esperada: O(2^n).
# ---------------------------------------------------------------------------
def subsets2(nums: List[int]) -> List[List[int]]:
    print("nums ", nums)
    result = [[] for x in range(len(nums)+1)]
    result[1] = [[n] for n in nums]
    for s in range(2,len(nums)+1):
        # s is the size of the subsets
        # For each subset in the previous size create new bucket 
        subset_dict = {}
        for subset in result[s-1]:
            print(f"s {s} subset {subset}")
            for n in nums:
                new_subset = set(subset)
                new_subset.add(n)
                if len(new_subset) != s:
                    continue
                # check for existence 
                a = sorted(list(new_subset))
                st = [str(x) for x in a]
                key = "".join(st)
                if key not in subset_dict:
                    subset_dict[key] = 1
                    print(f"s {s} n {n} subset {subset} newsubset {list(new_subset)}")
                    result[s].append(list(new_subset))
    final_result = []
    for x in result:
        final_result.extend(x)
    final_result.append([])
    print(f"result {final_result}")
    return final_result

def subsets(nums: List[int]) -> List[List[int]]:
    result: List[List[int]] = []

    def backtrack(start: int, path: List[int]) -> None:
        result.append(path[:])
        for i in range(start, len(nums)):
            path.append(nums[i])
            backtrack(i + 1, path)
            path.pop()

    backtrack(0, [])
    print("result ", result)
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


def _normalize(subs: List[List[int]]) -> set:
    return {tuple(sorted(s)) for s in subs}


def main() -> None:
    result = subsets([1, 2, 3])
    expected = _normalize([[], [1], [2], [3], [1, 2], [1, 3], [2, 3], [1, 2, 3]])
    check(len(result) == 8, "EJ15 numero total de subconjuntos = 2^3")
    check(_normalize(result) == expected, "EJ15 contenido correcto para [1,2,3]")

    check(_normalize(subsets([])) == {()}, "EJ15 array vacio -> solo el subconjunto vacio")

    result2 = subsets([0])
    check(_normalize(result2) == _normalize([[], [0]]), "EJ15 un solo elemento")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
