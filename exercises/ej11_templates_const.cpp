// EJ 11 — Templates y const correctness
//
// CÓMO USARLO
//   1. Rellena las funciones/métodos marcados con  // TODO.
//   2. Compila y ejecuta:
//        g++ -std=c++17 -O2 -Wall exercises/ej11_templates_const.cpp -o ej11 && ./ej11
//   3. Cronométrate: apunta a ~15-20 min.
//   4. Solo si te atascas, mira solutions/ej11_templates_const.cpp.

#include <iostream>
#include <string>
using namespace std;

// ===========================================================================
// EJ 11a — clampValue<T>
//   Reimplementa std::clamp: si v < lo devuelve lo, si v > hi devuelve hi,
//   en otro caso devuelve v. Debe funcionar con int, float, double...
// ---------------------------------------------------------------------------
template<typename T>
T clampValue(T v, T lo, T hi) {
    // TODO
    return v;
}

// ===========================================================================
// EJ 11b — BoundingBox<T>
//   Caja delimitadora genérica: (x1,y1) top-left, (x2,y2) bottom-right.
//   area(): (x2-x1)*(y2-y1). contains(px,py): true si el punto cae dentro
//   (bordes incluidos). Ambos métodos deben ser const (no mutan la caja).
// ---------------------------------------------------------------------------
template<typename T>
struct BoundingBox {
    T x1, y1, x2, y2;

    T area() const {
        // TODO
        return T{};
    }

    bool contains(T px, T py) const {
        // TODO
        return false;
    }
};

// ===========================================================================
//                        TEST HARNESS (no tocar)
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
