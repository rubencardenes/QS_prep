// EJ 10 — std::optional, std::variant y std::string_view — solución de referencia
// Compilar:  g++ -std=c++17 -O2 -Wall solutions/ej10_optional_variant.cpp -o sol10 && ./sol10
// Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

#include <charconv>
#include <iostream>
#include <optional>
#include <sstream>
#include <string>
#include <string_view>
#include <type_traits>
#include <variant>
using namespace std;

// ---------------------------------------------------------------------------
// EJ 10a — parseResolution. Sin allocaciones de substrings: string_view +
// std::from_chars (parseo directo sobre el buffer original).
optional<pair<int,int>> parseResolution(string_view s) {
    auto xpos = s.find('x');
    if (xpos == string_view::npos) return nullopt;

    string_view wPart = s.substr(0, xpos);
    string_view hPart = s.substr(xpos + 1);

    int w = 0, h = 0;
    auto rw = from_chars(wPart.data(), wPart.data() + wPart.size(), w);
    auto rh = from_chars(hPart.data(), hPart.data() + hPart.size(), h);
    if (rw.ec != errc{} || rw.ptr != wPart.data() + wPart.size()) return nullopt;
    if (rh.ec != errc{} || rh.ptr != hPart.data() + hPart.size()) return nullopt;

    return make_pair(w, h);
}

// ---------------------------------------------------------------------------
// EJ 10b — formatSensorValue con std::visit y una lambda genérica (if constexpr).
using SensorValue = variant<int, float, string>;

string formatSensorValue(const SensorValue& v) {
    return visit([](const auto& val) -> string {
        using T = decay_t<decltype(val)>;
        if constexpr (is_same_v<T, int>) {
            return "int:" + to_string(val);
        } else if constexpr (is_same_v<T, float>) {
            ostringstream oss;
            oss.precision(2);
            oss << fixed << val;
            return "float:" + oss.str();
        } else {
            return "str:" + val;
        }
    }, v);
}

// ===========================================================================
//                               TEST HARNESS
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
