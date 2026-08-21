# EJ 57 — Decode Ways (programacion dinamica: strings)
#
# CÓMO USARLO
#   1. Rellena la función marcada con  # TODO.
#   2. Ejecuta:  python3 python_exercises/ej57_decode_ways.py
#   3. Cronométrate: apunta a ~20-25 min.
#   4. Solo si te atascas, mira solutions/ej57_decode_ways.py.

import sys


# ===========================================================================
# EJ 57 — Decode Ways
#   Un mensaje de letras A-Z se codifica a números: A=1, B=2, ..., Z=26.
#   Dado un string `s` de dígitos, devuelve de cuántas formas distintas
#   se puede decodificar. Un '0' nunca es válido por sí solo (ninguna
#   letra se codifica como 0), así que un '0' solo es válido como parte
#   de "10" o "20".
#   Complejidad esperada: O(n) tiempo, O(1) espacio (o O(n) si usas un
#   array dp). Pista: dp[i] = formas de decodificar s[:i]. dp[i] suma
#   dp[i-1] si s[i-1] es un dígito válido por sí solo (!= '0'), y suma
#   dp[i-2] si s[i-2:i] forma un número entre 10 y 26.
# ---------------------------------------------------------------------------
def num_decodings(s: str) -> int:
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
