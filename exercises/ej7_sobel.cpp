// EJ 7 — Magnitud del gradiente Sobel (detección de bordes)  [el más completo]
//
// CÓMO USARLO
//   1. Rellena la función marcada con  // TODO.
//   2. Compila y ejecuta:
//        g++ -std=c++17 -O2 -Wall exercises/ej7_sobel.cpp -o ej7 && ./ej7
//   3. Cronométrate: apunta a ~10-15 min.
//   4. Solo si te atascas, mira solutions/ej7_sobel.cpp.

#include <algorithm>
#include <cmath>
#include <iostream>
#include <string>
#include <vector>
using namespace std;

using Image = vector<vector<int>>;   // escala de grises, valores 0..255

// ===========================================================================
// EJ 7 — Magnitud del gradiente Sobel (detección de bordes)
//   Aplica los kernels Sobel Kx (horizontal) y Ky (vertical), calcula
//   mag = sqrt(gx^2 + gy^2), redondea y recorta a 0..255. Bordes con clamp.
//     Kx = [[-1,0,1],[-2,0,2],[-1,0,1]]
//     Ky = [[-1,-2,-1],[0,0,0],[1,2,1]]
// ---------------------------------------------------------------------------
Image sobelMagnitude(const Image& img) {
    const int H = img.size();
    const int W = img[0].size();
    Image out(H, vector<int>(W));
    vector<vector<int>> Kx = {{-1,0,1},{-2,0,2},{-1,0,1}};
    vector<vector<int>> Ky = {{-1,-2,-1}, {0,0,0}, {1,2,1}};
    auto clamp = [](int v, int low, int high) {return min(max(v, low), high);};
    for (int y=0; y<H; ++y) {
        for (int x=0;x<W; ++x) {
            int sob_x = 0, sob_y = 0;
            for (int ny = -1;ny <= 1;++ny) {
                for (int nx = -1;nx <= 1;++nx) {
                    sob_x += img[clamp(y+ny, 0, H-1)][clamp(x+nx, 0, W-1)]*Kx[ny+1][nx+1];
                    sob_y += img[clamp(y+ny, 0, H-1)][clamp(x+nx, 0, W-1)]*Ky[ny+1][nx+1];
                }
            }
            out[y][x] = (int)sqrt(sob_x*sob_x + sob_y*sob_y);
        }
    }
    return out;
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
    // Borde vertical: mitad izq 0, mitad der 255 -> gradiente fuerte en el centro
    { Image in = {{0,0,255,255},
                  {0,0,255,255},
                  {0,0,255,255},
                  {0,0,255,255}};
      Image m = sobelMagnitude(in);
      check(m.size()==4 && m[0].size()==4 && m[1][1] > m[1][0],
            "EJ7 magnitud mayor junto al borde");
      check(m.size()==4 && m[0][0] >= 0 && m[3][3] <= 255, "EJ7 valores en rango 0..255"); }

    cout << "\nResultado: " << g_pass << " passed, " << g_fail << " failed\n";
    return g_fail ? 1 : 0;
}
