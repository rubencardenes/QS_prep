# EJ 57 — Decode Ways — solución de referencia
# Ejecutar:  python3 python_exercises/solutions/ej57_decode_ways.py
# Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

import sys


# ---------------------------------------------------------------------------
# EJ 57 — Decode Ways. Complejidad: O(n) tiempo, O(1) espacio.
# dp_prev2, dp_prev1 representan dp[i-2] y dp[i-1] (formas de decodificar
# los primeros i-2 y i-1 caracteres). dp[0] = 1 (string vacio, una unica
# forma "no decodificar nada"). Para cada posicion, sumamos dp_prev1 si
# el digito actual por si solo es valido (1-9), y sumamos dp_prev2 si
# los dos ultimos digitos forman un numero entre 10 y 26.
def num_decodings(s: str) -> int:
    if not s:
        return 0

    prev2 = 1  # dp[i-2], arranca como dp[0]
    prev1 = 1 if s[0] != "0" else 0  # dp[1]

    for i in range(1, len(s)):
        current = 0
        if s[i] != "0":
            current += prev1
        two_digit = int(s[i - 1:i + 1])
        if 10 <= two_digit <= 26:
            current += prev2
        prev2, prev1 = prev1, current

    return prev1


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
    check(num_decodings("12") == 2, "EJ57 AB o L")
    check(num_decodings("226") == 3, "EJ57 BZ, VF o BBF")
    check(num_decodings("06") == 0, "EJ57 cero inicial invalido")
    check(num_decodings("0") == 0, "EJ57 solo un cero")
    check(num_decodings("27") == 1, "EJ57 27 no es letra valida, solo B G")
    check(num_decodings("1") == 1, "EJ57 un solo digito valido")
    check(num_decodings("10") == 1, "EJ57 diez es J")

    print(f"\nResultado: {_pass} passed, {_fail} failed")
    sys.exit(1 if _fail else 0)


if __name__ == "__main__":
    main()
