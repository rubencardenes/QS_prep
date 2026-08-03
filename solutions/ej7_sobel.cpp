// EJ 7 — Magnitud del gradiente Sobel — solución de referencia
// Compilar:  g++ -std=c++17 -O2 -Wall solutions/ej7_sobel.cpp -o sol7 && ./sol7
// Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

#include <algorithm>
#include <cmath>
#include <iostream>
#include <string>
#include <vector>
using namespace std;

using Image = vector<vector<int>>;   // escala de grises, valores 0..255

// ---------------------------------------------------------------------------
// EJ 7 — Magnitud del gradiente Sobel. Bordes con clamp. Devuelve
// round(sqrt(gx^2+gy^2)) recortado a 0..255.
//   Kx = [[-1,0,1],[-2,0,2],[-1,0,1]]   Ky = Kx transpuesto (vertical)
Image sobelMagnitude(const Image& img) {
    int H = img.size(), W = H ? img[0].size() : 0;
    Image out(H, vector<int>(W, 0));
    int Kx[3][3] = {{-1,0,1},{-2,0,2},{-1,0,1}};
    int Ky[3][3] = {{-1,-2,-1},{0,0,0},{1,2,1}};
    auto clampi = [](int v, int lo, int hi){ return max(lo, min(v, hi)); };
    for (int y = 0; y < H; ++y)
        for (int x = 0; x < W; ++x) {
            int gx = 0, gy = 0;
            for (int dy = -1; dy <= 1; ++dy)
                for (int dx = -1; dx <= 1; ++dx) {
                    int v = img[clampi(y+dy,0,H-1)][clampi(x+dx,0,W-1)];
                    gx += Kx[dy+1][dx+1]*v;
                    gy += Ky[dy+1][dx+1]*v;
                }
            int mag = (int)llround(sqrt((double)gx*gx + (double)gy*gy));
            out[y][x] = clampi(mag, 0, 255);
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
        // Borde vertical: mitad izq 0, mitad der 255 -> gradiente fuerte en el centro
        Image in = {
            {0,0,255,255},
            {0,0,255,255},
            {0,0,255,255},
            {0,0,255,255}};
        Image m = sobelMagnitude(in);
        check(m[1][1] > m[1][0], "EJ7 magnitud mayor junto al borde");
        check(m[0][0] >= 0 && m[3][3] <= 255, "EJ7 valores en rango 0..255");
    }

    cout << "\nResultado: " << g_pass << " passed, " << g_fail << " failed\n";
    return g_fail ? 1 : 0;
}
