// EJ 4 — IoU (Intersection over Union) de dos cajas
//
// CÓMO USARLO
//   1. Rellena la función marcada con  // TODO.
//   2. Compila y ejecuta:
//        g++ -std=c++17 -O2 -Wall exercises/ej4_iou.cpp -o ej4 && ./ej4
//   3. Cronométrate: apunta a ~10-15 min.
//   4. Solo si te atascas, mira solutions/ej4_iou.cpp.

#include <algorithm>
#include <cmath>
#include <iostream>
#include <string>
using namespace std;

struct Box { double x1, y1, x2, y2, score; };

// ===========================================================================
// EJ 4 — IoU (Intersection over Union) de dos cajas
//   Caja = [x1,y1,x2,y2] con x2>x1, y2>y1. Devuelve inter/union en [0,1].
//   Edge cases: cajas disjuntas -> 0; misma caja -> 1; area 0 -> 0.
// ---------------------------------------------------------------------------
double overlap_onedim(double a1, double a2, double b1, double b2) {
    double ov = 0;
    ov = max(min(a2, b2) - max(a1, b1), 0.0);
    return ov;
}

double iou(const Box& a, const Box& b) {
    double ovx = 0, ovy = 0; 
    ovx = overlap_onedim(a.x1, a.x2, b.x1, b.x2);
    ovy = overlap_onedim(a.y1, a.y2, b.y1, b.y2);

    double inters = ovx * ovy; 
    double un = max(0.0, (a.x2 - a.x1)) * max(0.0, (a.y2 - a.y1)) + max(0.0, (b.x2 - b.x1)) * max(0.0, (b.y2 - b.y1)) - inters;
    return inters / un;
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
    { Box a{0,0,2,2,1.0}, b{1,1,3,3,1.0};
      check(fabs(iou(a,b) - (1.0/7.0)) < 1e-9, "EJ4 IoU solapamiento parcial");
      Box c{0,0,2,2,1.0}, d{5,5,6,6,1.0};
      check(iou(c,d)==0.0, "EJ4 IoU disjuntas -> 0");
      check(fabs(iou(a,a)-1.0)<1e-9, "EJ4 IoU consigo misma -> 1"); }

    cout << "\nResultado: " << g_pass << " passed, " << g_fail << " failed\n";
    return g_fail ? 1 : 0;
}
