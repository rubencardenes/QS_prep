// EJ 10 — std::optional, std::variant y std::string_view
//
// CÓMO USARLO
//   1. Rellena las funciones marcadas con  // TODO.
//   2. Compila y ejecuta:
//        g++ -std=c++17 -O2 -Wall exercises/ej10_optional_variant.cpp -o ej10 && ./ej10
//   3. Cronométrate: apunta a ~15-20 min.
//   4. Solo si te atascas, mira solutions/ej10_optional_variant.cpp.

#include <charconv>
#include <iostream>
#include <optional>
#include <string>
#include <string_view>
#include <variant>
using namespace std;

// ===========================================================================
// EJ 10a — parseResolution
//   Parsea un string tipo "1920x1080" a pair<int,int> {width, height}.
//   Sin crear substrings con alloc: usa string_view::substr + std::from_chars.
//   Devuelve nullopt si el formato es inválido (no hay 'x', o alguna de las
//   dos partes no es un número válido).
// ---------------------------------------------------------------------------
optional<pair<int,int>> parseResolution(string_view s) {
    s.substr("x");
    return nullopt;
}

// ===========================================================================
// EJ 10b — formatSensorValue
//   SensorValue puede ser int, float o string. Usa std::visit para formatear:
//     int    -> "int:<valor>"
//     float  -> "float:<valor con 2 decimales>"
//     string -> "str:<valor>"
// ---------------------------------------------------------------------------
using SensorValue = variant<int, float, string>;

string formatSensorValue(const SensorValue& v) {
    // TODO
    return "";
}

// ===========================================================================
//                        TEST HARNESS (no tocar)
// ===========================================================================
static int g_pass = 0, g_fail = 0;
void check(bool ok, const string& name) {
    (ok ? g_pass : g_fail)++;
    cout << (ok ? "  [PASS] " : "  [FAIL] ") << name << "\n";
}

int main() {
    { auto r = parseResolution("1920x1080");
      check(r.has_value() && r->first == 1920 && r->second == 1080,
            "EJ10a parsea resolucion valida"); }

    { auto r = parseResolution("bad_input");
      check(!r.has_value(), "EJ10a input sin 'x' devuelve nullopt"); }

    { auto r = parseResolution("640xabc");
      check(!r.has_value(), "EJ10a parte no numerica devuelve nullopt"); }

    { SensorValue v = 42;
      check(formatSensorValue(v) == "int:42", "EJ10b formatea int"); }

    { SensorValue v = 3.5f;
      check(formatSensorValue(v) == "float:3.50", "EJ10b formatea float con 2 decimales"); }

    { SensorValue v = string("ok");
      check(formatSensorValue(v) == "str:ok", "EJ10b formatea string"); }

    cout << "\nResultado: " << g_pass << " passed, " << g_fail << " failed\n";
    return g_fail ? 1 : 0;
}
