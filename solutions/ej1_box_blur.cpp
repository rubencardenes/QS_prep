// EJ 1 — Box blur 3x3 (media) — solución de referencia
// Compilar:  g++ -std=c++17 -O2 -Wall solutions/ej1_box_blur.cpp -o sol1 && ./sol1
// Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

#include <algorithm>
#include <iostream>
#include <string>
#include <vector>
using namespace std;

using Image = vector<vector<int>>;   // escala de grises, valores 0..255

// ---------------------------------------------------------------------------
// EJ 1 — Box blur 3x3 (media). Bordes: replicar el píxel del borde (clamp).
// Complejidad: O(H*W) con 9 accesos por píxel (constante).
Image boxBlur3(const Image& img) {
    int H = img.size(), W = H ? img[0].size() : 0;
    Image out(H, vector<int>(W, 0));
    auto clamp = [](int v, int lo, int hi){ return max(lo, min(v, hi)); };
    for (int y = 0; y < H; ++y)
        for (int x = 0; x < W; ++x) {
            int sum = 0;
            for (int dy = -1; dy <= 1; ++dy)
                for (int dx = -1; dx <= 1; ++dx)
                    sum += img[clamp(y+dy,0,H-1)][clamp(x+dx,0,W-1)];
            out[y][x] = sum / 9;   // división entera
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
        Image in = {{0,0,0},{0,90,0},{0,0,0}};
        Image out = boxBlur3(in);
        check(out[1][1] == 10, "EJ1 blur centro (90/9=10)");
        Image flat(4, vector<int>(4, 50));
        check(boxBlur3(flat)[0][0] == 50, "EJ1 blur zona uniforme conserva valor");
    }

    cout << "\nResultado: " << g_pass << " passed, " << g_fail << " failed\n";
    return g_fail ? 1 : 0;
}
