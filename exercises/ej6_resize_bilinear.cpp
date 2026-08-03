// EJ 6 — Redimensionar con interpolación bilineal
//
// CÓMO USARLO
//   1. Rellena la función marcada con  // TODO.
//   2. Compila y ejecuta:
//        g++ -std=c++17 -O2 -Wall exercises/ej6_resize_bilinear.cpp -o ej6 && ./ej6
//   3. Cronométrate: apunta a ~10-15 min.
//   4. Solo si te atascas, mira solutions/ej6_resize_bilinear.cpp.

#include <algorithm>
#include <cmath>
#include <iostream>
#include <string>
#include <vector>
using namespace std;

using Image = vector<vector<int>>;   // escala de grises, valores 0..255

// ===========================================================================
// EJ 6 — Redimensionar con interpolación bilineal
//   Escala img a (newH x newW). Para cada píxel destino calcula la coordenada
//   fuente con centrado de píxel:  srcX = (x+0.5)*W/newW - 0.5  (idem Y).
//   Mezcla los 4 vecinos con pesos fx, fy. Clamp de coordenadas en bordes.
//   Redondea el resultado a entero.
// ---------------------------------------------------------------------------
Image resizeBilinear(const Image& img, int newH, int newW) {
    const int H = img.size();
    const int W = img[0].size();
    Image out(H, vector<int>(W));
    int idx[] = {0, 0, +1, -1};
    int idy[] = {+1, -1, 0, 0};
    auto clamp = [](int v, int low, int high) {return min(max(v, low), high);};
    for (int y=0; y<newH; ++y) {
        double srcY = (y+0.5)*H/newH - 0.5;
        fy = srcY - (int)floor(srcY);
        for (int x=0;x<newW; ++x) {
            double srcX = (x+0.5)*W/newW - 0.5;
            fx = srcX - (int)floor(srcY);
            int sum = 0;
            for (int i=0;i<4;++i) {
                int nx = int(srcX)+idx[i]*fx;
                int ny = int(srcY)+idy[i]*fy;
                sum += img[clamp(ny, 0, H)][clamp(nx, 0, W)];
            }
            out[y][x] = int(sum/4);
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
    { Image in = {{0,0},{0,0}};
      check(resizeBilinear(in,4,4).size()==4 && resizeBilinear(in,4,4)[2][2]==0,
            "EJ6 uniforme 0 se mantiene");
      Image in2 = {{0,10},{0,10}};
      Image up = resizeBilinear(in2,2,4);        // ancho x2
      check(up.size()==2 && up[0].size()==4, "EJ6 dimensiones destino");
      check(up.size()==2 && up[0].size()==4 && up[0][0] <= up[0][3],
            "EJ6 gradiente horizontal creciente"); }

    cout << "\nResultado: " << g_pass << " passed, " << g_fail << " failed\n";
    return g_fail ? 1 : 0;
}
