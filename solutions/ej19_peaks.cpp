// EJ 19 — Máximos locales 3x3 + top-K — solución de referencia
// Compilar:  make sol19
// Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

#include <algorithm>
#include <iostream>
#include <string>
#include <vector>
using namespace std;

using Response = vector<vector<double>>;

struct Peak {
    int y, x;
    double score;
};

// ---------------------------------------------------------------------------
// 19 — Una pasada O(H*W*9) para detectar y luego una ordenación.
//   Claves de diseño:
//   - Comparación ESTRICTA (v > vecino): con >= una meseta de N píxeles iguales
//     devolvería N picos solapados. Si te pidieran soportar mesetas, lo correcto
//     es quedarse con el centroide de cada meseta (eso ya es connected components).
//   - El bucle de vecinos salta el propio píxel y los que caen fuera: nada de
//     duplicar código para los bordes.
//   - Orden total explícito (score desc, luego y, luego x) -> salida reproducible.
//   - Para topK, partial_sort ordena solo los K primeros: O(N log K).
// ---------------------------------------------------------------------------
vector<Peak> findPeaks(const Response& resp, double thr, int topK) {
    int H = resp.size(), W = H ? resp[0].size() : 0;
    vector<Peak> peaks;

    for (int y = 0; y < H; ++y) {
        for (int x = 0; x < W; ++x) {
            double v = resp[y][x];
            if (v < thr) continue;
            bool isMax = true;
            for (int dy = -1; dy <= 1 && isMax; ++dy)
                for (int dx = -1; dx <= 1; ++dx) {
                    if (dy == 0 && dx == 0) continue;
                    int yy = y + dy, xx = x + dx;
                    if (yy < 0 || yy >= H || xx < 0 || xx >= W) continue;
                    if (resp[yy][xx] >= v) { isMax = false; break; }
                }
            if (isMax) peaks.push_back({y, x, v});
        }
    }

    auto better = [](const Peak& a, const Peak& b) {
        if (a.score != b.score) return a.score > b.score;
        if (a.y != b.y) return a.y < b.y;
        return a.x < b.x;
    };

    if (topK > 0 && (size_t)topK < peaks.size()) {
        partial_sort(peaks.begin(), peaks.begin() + topK, peaks.end(), better);
        peaks.resize(topK);
    } else {
        sort(peaks.begin(), peaks.end(), better);
    }
    return peaks;
}

// ===========================================================================
//                               TEST HARNESS
// ===========================================================================
static int g_pass = 0, g_fail = 0;
void check(bool ok, const string& name) {
    (ok ? g_pass : g_fail)++;
    cout << (ok ? "  [PASS] " : "  [FAIL] ") << name << "\n";
}

static bool eq(const Peak& p, int y, int x, double s) {
    return p.y == y && p.x == x && abs(p.score - s) < 1e-9;
}

int main() {
    Response r = {{0,0,0,0,0},
                  {0,9,0,0,0},
                  {0,0,0,5,0},
                  {0,0,0,0,0},
                  {0,3,0,0,0}};
    {
        vector<Peak> p = findPeaks(r, 1.0, 0);
        check(p.size() == 3, "19 encuentra los 3 picos (obtenidos " + to_string(p.size()) + ")");
        check(eq(p[0], 1, 1, 9), "19 ordenado por score descendente");
        check(eq(p[1], 2, 3, 5) && eq(p[2], 4, 1, 3), "19 resto del orden correcto");
    }
    {
        check(findPeaks(r, 4.0, 0).size() == 2, "19 el umbral descarta el pico de 3");
        vector<Peak> p = findPeaks(r, 1.0, 1);
        check(p.size() == 1 && eq(p[0], 1, 1, 9), "19 topK=1 devuelve solo el mejor");
        check(findPeaks(r, 1.0, 99).size() == 3, "19 topK mayor que el total no rellena");
        check(findPeaks(r, 100.0, 0).empty(), "19 umbral alto -> vacío");
    }
    {
        Response flat = {{0,0,0,0},{0,7,7,0},{0,0,0,0}};
        check(findPeaks(flat, 1.0, 0).empty(), "19 una meseta no genera picos (comparación estricta)");
        Response zeros(4, vector<double>(4, 0.0));
        check(findPeaks(zeros, 0.0, 0).empty(), "19 mapa constante no genera picos");
        Response corner = {{8,0,0},{0,0,0},{0,0,4}};
        vector<Peak> p = findPeaks(corner, 1.0, 0);
        check(p.size() == 2 && eq(p[0], 0, 0, 8), "19 los picos en el borde también cuentan");
    }
    {
        Response tie = {{0,0,0,0,0},{0,5,0,0,0},{0,0,0,0,0},{0,0,0,5,0},{0,0,0,0,0}};
        vector<Peak> p = findPeaks(tie, 1.0, 0);
        check(p.size() == 2 && eq(p[0], 1, 1, 5) && eq(p[1], 3, 3, 5),
              "19 empate resuelto por (y,x) ascendente");
    }
    {
        check(findPeaks({}, 0.0, 0).empty(), "19 mapa vacío");
        Response one = {{42}};
        check(findPeaks(one, 1.0, 0).size() == 1, "19 un solo píxel es su propio máximo");
        Response neg = {{-5,-1,-5}};
        vector<Peak> p = findPeaks(neg, -100.0, 0);
        check(p.size() == 1 && eq(p[0], 0, 1, -1), "19 funciona con scores negativos");
    }

    cout << "\nResultado: " << g_pass << " passed, " << g_fail << " failed\n";
    return g_fail ? 1 : 0;
}
