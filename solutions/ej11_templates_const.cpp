// EJ 11 — Templates y const correctness — solución de referencia
// Compilar:  g++ -std=c++17 -O2 -Wall solutions/ej11_templates_const.cpp -o sol11 && ./sol11
// Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

#include <iostream>
#include <string>
using namespace std;

// ---------------------------------------------------------------------------
// EJ 11a — clampValue<T>.
template<typename T>
T clampValue(T v, T lo, T hi) {
    if (v < lo) return lo;
    if (v > hi) return hi;
    return v;
}

// ---------------------------------------------------------------------------
// EJ 11b — BoundingBox<T>. area()/contains() son const: no mutan el estado.
template<typename T>
struct BoundingBox {
    T x1, y1, x2, y2;

    T area() const {
        return (x2 - x1) * (y2 - y1);
    }

    bool contains(T px, T py) const {
        return px >= x1 && px <= x2 && py >= y1 && py <= y2;
    }
};

// ===========================================================================
//                               TEST HARNESS
// ===========================================================================
static int g_pass = 0, g_fail = 0;
void check(bool ok, const string& name) {
    (ok ? g_pass : g_fail)++;
    cout << (ok ? "  [PASS] " : "  [FAIL] ") << name << "\n";
}

int main() {
    { check(clampValue(5, 0, 10) == 5, "EJ11a clamp dentro de rango (int)");
      check(clampValue(-3, 0, 10) == 0, "EJ11a clamp por debajo (int)");
      check(clampValue(99, 0, 10) == 10, "EJ11a clamp por encima (int)");
      check(clampValue(2.5f, 0.0f, 1.0f) == 1.0f, "EJ11a clamp por encima (float)"); }

    { BoundingBox<int> box{0, 0, 10, 10};
      check(box.area() == 100, "EJ11b area de caja entera");
      check(box.contains(5, 5), "EJ11b punto interior");
      check(box.contains(0, 0) && box.contains(10, 10), "EJ11b bordes incluidos");
      check(!box.contains(11, 5), "EJ11b punto fuera"); }

    { const BoundingBox<float> fbox{0.0f, 0.0f, 2.0f, 4.0f};
      check(fbox.area() == 8.0f, "EJ11b area de caja float (const)"); }

    cout << "\nResultado: " << g_pass << " passed, " << g_fail << " failed\n";
    return g_fail ? 1 : 0;
}
