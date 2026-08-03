// EJ 6 — Redimensionar con interpolación bilineal — solución de referencia
// Compilar:  g++ -std=c++17 -O2 -Wall solutions/ej6_resize_bilinear.cpp -o sol6 && ./sol6
// Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

#include <algorithm>
#include <cmath>
#include <iostream>
#include <string>
#include <vector>
using namespace std;

using Image = vector<vector<int>>;   // escala de grises, valores 0..255

// ---------------------------------------------------------------------------
// EJ 6 — Redimensiona a (newH,newW) con interpolación bilineal.
// Mapeo estándar: srcX = (x+0.5)*W/newW - 0.5 (align pixel centers).
Image resizeBilinear(const Image& img, int newH, int newW) {
    int H = img.size(), W = H ? img[0].size() : 0;
    Image out(newH, vector<int>(newW, 0));
    auto clampi = [](int v, int lo, int hi){ return max(lo, min(v, hi)); };
    for (int y = 0; y < newH; ++y) {
        double sy = (y + 0.5) * H / newH - 0.5;
        int y0 = (int)floor(sy); double fy = sy - y0;
        int y0c = clampi(y0,0,H-1), y1c = clampi(y0+1,0,H-1);
        for (int x = 0; x < newW; ++x) {
            double sx = (x + 0.5) * W / newW - 0.5;
            int x0 = (int)floor(sx); double fx = sx - x0;
            int x0c = clampi(x0,0,W-1), x1c = clampi(x0+1,0,W-1);
            double top = img[y0c][x0c]*(1-fx) + img[y0c][x1c]*fx;
            double bot = img[y1c][x0c]*(1-fx) + img[y1c][x1c]*fx;
            out[y][x] = (int)llround(top*(1-fy) + bot*fy);
        }
    }
    return out;
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
        Image in = {{0,0},{0,0}};
        check(resizeBilinear(in,4,4)[2][2]==0, "EJ6 uniforme 0 se mantiene");
        Image in2 = {{0,10},{0,10}};
        Image up = resizeBilinear(in2,2,4);   // ancho x2
        check(up.size()==2 && up[0].size()==4, "EJ6 dimensiones destino");
        check(up[0][0] <= up[0][3], "EJ6 gradiente horizontal creciente");
    }

    cout << "\nResultado: " << g_pass << " passed, " << g_fail << " failed\n";
    return g_fail ? 1 : 0;
}
