// EJ 4 — IoU (Intersection over Union) — solución de referencia
// Compilar:  g++ -std=c++17 -O2 -Wall solutions/ej4_iou.cpp -o sol4 && ./sol4
// Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

#include <algorithm>
#include <cmath>
#include <iostream>
#include <string>
using namespace std;

struct Box { double x1, y1, x2, y2, score; };

// ---------------------------------------------------------------------------
// EJ 4 — IoU (Intersection over Union) de dos cajas [x1,y1,x2,y2].
double iou(const Box& a, const Box& b) {
    double ix1 = max(a.x1, b.x1), iy1 = max(a.y1, b.y1);
    double ix2 = min(a.x2, b.x2), iy2 = min(a.y2, b.y2);
    double iw = max(0.0, ix2 - ix1), ih = max(0.0, iy2 - iy1);
    double inter = iw * ih;
    double areaA = max(0.0,(a.x2-a.x1)) * max(0.0,(a.y2-a.y1));
    double areaB = max(0.0,(b.x2-b.x1)) * max(0.0,(b.y2-b.y1));
    double uni = areaA + areaB - inter;
    return uni <= 0.0 ? 0.0 : inter / uni;
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
    {
        Box a{0,0,2,2,1.0}, b{1,1,3,3,1.0};
        check(fabs(iou(a,b) - (1.0/7.0)) < 1e-9, "EJ4 IoU solapamiento parcial");
        Box c{0,0,2,2,1.0}, d{5,5,6,6,1.0};
        check(iou(c,d)==0.0, "EJ4 IoU disjuntas -> 0");
        check(fabs(iou(a,a)-1.0)<1e-9, "EJ4 IoU consigo misma -> 1");
    }

    cout << "\nResultado: " << g_pass << " passed, " << g_fail << " failed\n";
    return g_fail ? 1 : 0;
}
