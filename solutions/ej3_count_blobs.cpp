// EJ 3 — Contar componentes conexas (blobs) — solución de referencia
// Compilar:  g++ -std=c++17 -O2 -Wall solutions/ej3_count_blobs.cpp -o sol3 && ./sol3
// Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

#include <iostream>
#include <stack>
#include <string>
#include <utility>
#include <vector>
using namespace std;

using Image = vector<vector<int>>;   // escala de grises, valores 0..255

// ---------------------------------------------------------------------------
// EJ 3 — Binariza (>= thr -> 1, si no 0) y cuenta componentes conexas de 1s
// con conectividad-4 (flood fill con pila explícita: sin riesgo de stack
// overflow en imágenes grandes). Complejidad O(H*W).
int countBlobs(const Image& img, int thr) {
    int H = img.size(), W = H ? img[0].size() : 0;
    vector<vector<char>> seen(H, vector<char>(W, 0));
    int count = 0;
    int dx[] = {1,-1,0,0}, dy[] = {0,0,1,-1};
    for (int sy = 0; sy < H; ++sy)
        for (int sx = 0; sx < W; ++sx) {
            if (img[sy][sx] < thr || seen[sy][sx]) continue;
            ++count;
            stack<pair<int,int>> st;
            st.push({sy,sx}); seen[sy][sx] = 1;
            while (!st.empty()) {
                auto [y,x] = st.top(); st.pop();
                for (int k = 0; k < 4; ++k) {
                    int ny = y+dy[k], nx = x+dx[k];
                    if (ny<0||ny>=H||nx<0||nx>=W) continue;
                    if (img[ny][nx] >= thr && !seen[ny][nx]) {
                        seen[ny][nx] = 1; st.push({ny,nx});
                    }
                }
            }
        }
    return count;
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
        Image in = {
            {255,255,0,0,255},
            {255,0,0,0,255},
            {0,0,255,0,0},
            {0,0,0,0,0},
            {255,0,0,0,255}};
        check(countBlobs(in,128)==5, "EJ3 cuenta 5 blobs (conect-4)");
        Image empty = {{0,0},{0,0}};
        check(countBlobs(empty,128)==0, "EJ3 imagen vacia -> 0");
    }

    cout << "\nResultado: " << g_pass << " passed, " << g_fail << " failed\n";
    return g_fail ? 1 : 0;
}
