// EJ 18 — Imagen integral y box blur en O(1) — solución de referencia
// Compilar:  make sol18
// Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

#include <algorithm>
#include <cmath>
#include <iostream>
#include <string>
#include <vector>
using namespace std;

using Image    = vector<vector<int>>;
using Integral = vector<vector<long long>>;

// ---------------------------------------------------------------------------
// 18.a — El borde de ceros (fila y columna 0) es el truco que hace que la
//   recurrencia sea uniforme: sin él harían falta casos especiales para y==0
//   y x==0 dentro del bucle caliente.
//   long long es obligatorio: 3000x3000 píxeles a 255 ya desbordan un int.
//   Complejidad O(H*W), una sola pasada, secuencial en memoria.
// ---------------------------------------------------------------------------
Integral integralImage(const Image& img) {
    int H = img.size(), W = H ? img[0].size() : 0;
    Integral S(H + 1, vector<long long>(W + 1, 0));
    for (int y = 1; y <= H; ++y)
        for (int x = 1; x <= W; ++x)
            S[y][x] = img[y-1][x-1] + S[y-1][x] + S[y][x-1] - S[y-1][x-1];
    return S;
}

// ---------------------------------------------------------------------------
// 18.b — Inclusión-exclusión: la suma de A..D es
//     S[y1+1][x1+1] - S[y0][x1+1] - S[y1+1][x0] + S[y0][x0]
//   (el término +S[y0][x0] compensa la esquina restada dos veces).
//   4 accesos y 3 operaciones -> O(1) sea cual sea el tamaño de la ventana.
// ---------------------------------------------------------------------------
long long rectSum(const Integral& S, int y0, int x0, int y1, int x1) {
    return S[y1+1][x1+1] - S[y0][x1+1] - S[y1+1][x0] + S[y0][x0];
}

// ---------------------------------------------------------------------------
// 18.c — Coste total O(H*W) INDEPENDIENTE de k: ahí está la gracia frente al
//   O(H*W*k^2) ingenuo. Para k grandes la diferencia es de órdenes de magnitud.
//   Alternativa clásica sin tabla extra: blur separable (fila y luego columna),
//   O(H*W*k), que gasta menos memoria — buen trade-off que comentar en voz alta.
// ---------------------------------------------------------------------------
Image boxBlurFast(const Image& img, int k) {
    int H = img.size(), W = H ? img[0].size() : 0, r = k / 2;
    Integral S = integralImage(img);
    Image out(H, vector<int>(W, 0));
    for (int y = 0; y < H; ++y) {
        int y0 = max(0, y - r), y1 = min(H - 1, y + r);
        for (int x = 0; x < W; ++x) {
            int x0 = max(0, x - r), x1 = min(W - 1, x + r);
            long long sum = rectSum(S, y0, x0, y1, x1);
            int cnt = (y1 - y0 + 1) * (x1 - x0 + 1);
            out[y][x] = (int)llround((double)sum / cnt);
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

static Image boxBlurNaive(const Image& img, int k) {
    int H = img.size(), W = H ? img[0].size() : 0, r = k / 2;
    Image out(H, vector<int>(W, 0));
    for (int y = 0; y < H; ++y)
        for (int x = 0; x < W; ++x) {
            long long sum = 0; int cnt = 0;
            for (int dy = -r; dy <= r; ++dy)
                for (int dx = -r; dx <= r; ++dx) {
                    int yy = y + dy, xx = x + dx;
                    if (yy < 0 || yy >= H || xx < 0 || xx >= W) continue;
                    sum += img[yy][xx]; ++cnt;
                }
            out[y][x] = (int)llround((double)sum / cnt);
        }
    return out;
}

int main() {
    Image img = {{1,2,3},{4,5,6},{7,8,9}};
    {
        Integral S = integralImage(img);
        check(S.size() == 4 && S[0].size() == 4, "18.a tabla de (H+1)x(W+1)");
        check(S[0][0] == 0 && S[0][3] == 0 && S[3][0] == 0, "18.a fila y columna 0 a cero");
        check(S[1][1] == 1 && S[2][2] == 12 && S[3][3] == 45, "18.a acumulados correctos");
        check(integralImage({}).size() <= 1, "18.a imagen vacía no revienta");
    }
    {
        Integral S = integralImage(img);
        check(rectSum(S, 0, 0, 2, 2) == 45, "18.b suma de toda la imagen");
        check(rectSum(S, 1, 1, 2, 2) == 28, "18.b esquina inferior derecha 2x2");
        check(rectSum(S, 0, 1, 1, 2) == 16, "18.b rectángulo no cuadrado");
        check(rectSum(S, 1, 1, 1, 1) == 5,  "18.b un solo píxel");
        check(rectSum(S, 0, 0, 0, 2) == 6,  "18.b una fila entera");
    }
    {
        Image b = boxBlurFast(img, 3);
        check(b.size() == 3 && b[0].size() == 3, "18.c mantiene el tamaño");
        check(b[1][1] == 5, "18.c centro = 45/9 = 5");
        check(b[0][0] == 3, "18.c esquina = (1+2+4+5)/4 = 3 (ventana recortada)");
        check(boxBlurFast(img, 1) == img, "18.c k=1 es la identidad");

        srand(7);
        Image big(20, vector<int>(30));
        for (auto& row : big) for (auto& v : row) v = rand() % 256;
        bool same = true;
        for (int k : {3, 5, 7}) same = same && (boxBlurFast(big, k) == boxBlurNaive(big, k));
        check(same, "18.c coincide con la referencia O(k^2) para k=3,5,7");
    }
    {
        const int N = 3000;
        Image white(N, vector<int>(N, 255));
        Integral S = integralImage(white);
        check(S[N][N] == 2295000000LL, "18.a/b sin overflow: la tabla es de 64 bits");
    }

    cout << "\nResultado: " << g_pass << " passed, " << g_fail << " failed\n";
    return g_fail ? 1 : 0;
}
