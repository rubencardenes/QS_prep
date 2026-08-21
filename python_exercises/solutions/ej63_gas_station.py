# EJ 63 — Gas Station — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej63_gas_station.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import sys
from typing import List


# ---------------------------------------------------------------------------
# EJ 63 — Gas Station. Complejidad: O(n) tiempo, O(1) espacio.
# Si la gasolina total es menor que el coste total, es matemáticamente
# imposible completar el circuito desde cualquier punto: -1. Si no, se
# garantiza que existe una única estación válida. Recorremos una vez
# acumulando el tanque; si en la estación i el tanque se queda negativo,
# ninguna estación entre el `start` actual e i puede servir de arranque
# (llegarían a i con el tanque igual o más vacío), así que probamos
# start = i + 1 con el tanque a cero.
def can_complete_circuit(gas: List[int], cost: List[int]) -> int:
    if sum(gas) < sum(cost):
        return -1

    start = 0
    tank = 0
    for i in range(len(gas)):
        tank += gas[i] - cost[i]
        if tank < 0:
            start = i + 1
            tank = 0

    return start


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
