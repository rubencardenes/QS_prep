# EJ 63 — Gas Station (greedy)
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej63_gas_station.py
#   3. Cronométrate: apunta a ~20-25 min.
#   4. Solo si te atascas, mira solutions/ej63_gas_station.py.

import sys
from typing import List


# ===========================================================================
# EJ 63 — Gas Station
#   Hay `n` gasolineras en una ruta circular. `gas[i]` es la gasolina
#   disponible en la estación i, y `cost[i]` es la gasolina necesaria
#   para viajar desde la estación i hasta la i + 1. Empiezas con el
#   depósito vacío en alguna estación. Devuelve el índice de la
#   estación de salida que te permite completar el circuito una vez, o
#   -1 si no existe ninguna. Se garantiza que si existe solución, es
#   única.
#   Complejidad esperada: O(n) tiempo, O(1) espacio. Pista: si la suma
#   total de gas es menor que la suma total de cost, es imposible. Si
#   no, recorre las estaciones acumulando el "tanque"; en cuanto el
#   tanque se queda negativo en la estación i, ninguna estación entre el
#   punto de partida actual e i puede ser válida — reinicia el punto de
#   partida en i + 1.
# ---------------------------------------------------------------------------
def can_complete_circuit(gas: List[int], cost: List[int]) -> int:
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
    check(can_complete_circuit([1, 2, 3, 4, 5], [3, 4, 5, 1, 2]) == 3,
          "EJ63 existe solucion unica")
    check(can_complete_circuit([2, 3, 4], [3, 4, 3]) == -1,
          "EJ63 no hay suficiente gasolina en total")
    check(can_complete_circuit([5, 1, 2, 3, 4], [4, 4, 1, 5, 1]) == 4,
          "EJ63 cinco estaciones")
    check(can_complete_circuit([5], [4]) == 0, "EJ63 una sola estacion")
    check(can_complete_circuit([5, 8, 2, 8, 7, 9], [3, 9, 6, 9, 6, 5]) == 4,
          "EJ63 requiere varios reinicios del punto de partida")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
