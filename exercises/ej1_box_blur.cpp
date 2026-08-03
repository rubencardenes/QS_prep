// EJ 1 — Box blur 3x3 (media)  [warm-up]
//
// CÓMO USARLO
//   1. Rellena la función marcada con  // TODO.
//   2. Compila y ejecuta:
//        g++ -std=c++17 -O2 -Wall exercises/ej1_box_blur.cpp -o ej1 && ./ej1
//   3. Cronométrate: apunta a ~10-15 min.
//   4. Solo si te atascas, mira solutions/ej1_box_blur.cpp.

#include <algorithm>
#include <iostream>
#include <string>
#include <vector>
using namespace std;

using Image = vector<vector<int>>;   // escala de grises, valores 0..255

// ===========================================================================
// EJ 1 — Box blur 3x3 (media)
//   Sustituye cada píxel por la media entera (suma/9) de su vecindario 3x3.
//   Bordes: replica el píxel del borde (clamp de coordenadas).
//   Pistas de senior que valoran: cuidado con overflow al sumar (usa int),
//   evita copias innecesarias, comenta la complejidad O(H*W).
// ---------------------------------------------------------------------------
Image boxBlur3(const Image& img) {
    // TODO
    const int H = img.size();
    const int W = img[0].size();
    auto clamp = [](int v, int low, int high) {
        return min(max(v, low), high);
    };
    Image out(H, vector<int>(W, 0)); 
    for (int y=0; y < H; ++y) {
        for (int x=0; x < W; ++x) {
            float accum = 0;
            for (int ky=-1; ky <=1; ++ky) {
                for (int kx=-1; kx <=1; ++kx) {
                    accum += img[clamp(y+ky,0,H-1)][clamp(x+kx,0,W-1)];
                }
            } 
            out[y][x] = accum/9.0;
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
    { Image in = {{0,0,0},{0,90,0},{0,0,0}};
      check(boxBlur3(in)[1][1] == 10, "EJ1 blur centro (90/9=10)");
      Image flat(4, vector<int>(4, 50));
      check(boxBlur3(flat)[0][0] == 50, "EJ1 zona uniforme conserva valor"); }

    cout << "\nResultado: " << g_pass << " passed, " << g_fail << " failed\n";
    return g_fail ? 1 : 0;
}
