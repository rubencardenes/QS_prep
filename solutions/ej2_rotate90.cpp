// EJ 2 — Rotar 90° en sentido horario — solución de referencia
// Compilar:  g++ -std=c++17 -O2 -Wall solutions/ej2_rotate90.cpp -o sol2 && ./sol2
// Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

#include <iostream>
#include <string>
#include <vector>
using namespace std;

using Image = vector<vector<int>>;   // escala de grises, valores 0..255

// ---------------------------------------------------------------------------
// EJ 2 — Rotar imagen 90° en sentido horario. Devuelve nueva matriz.
Image rotate90(const Image& img) {
    int H = img.size(), W = H ? img[0].size() : 0;
    Image out(W, vector<int>(H, 0));
    for (int y = 0; y < H; ++y)
        for (int x = 0; x < W; ++x)
            out[x][H-1-y] = img[y][x];
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
        Image in = {{1,2,3},{4,5,6}};      // 2x3
        Image out = rotate90(in);           // 3x2 esperado: {{4,1},{5,2},{6,3}}
        check(out.size()==3 && out[0].size()==2, "EJ2 dimensiones 90");
        check(out[0][0]==4 && out[0][1]==1 && out[2][1]==3, "EJ2 valores 90");
    }

    cout << "\nResultado: " << g_pass << " passed, " << g_fail << " failed\n";
    return g_fail ? 1 : 0;
}
