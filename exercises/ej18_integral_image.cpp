// EJ 18 — Imagen integral (summed-area table) y box blur en O(1) por píxel
//
// CÓMO USARLO
//   1. Rellena las funciones marcadas con  // TODO.
//   2. Compila y ejecuta:   make ej18
//   3. Cronométrate: apunta a ~25 min.
//
// CONTEXTO TIPO ENTREVISTA
//   "Tenemos que calcular la media de miles de ventanas rectangulares sobre cada
//    frame (detector tipo Viola-Jones, features de fondo, ROIs de estadísticas).
//    Hacerlo a lo bruto es O(k²) por ventana. Dame algo mejor."
//
//   Respuesta: imagen integral. Precómputo O(H*W) una vez y luego CADA suma de
//   rectángulo es O(1) con 4 accesos. Es la base de Viola-Jones, de los box
//   filters rápidos y de muchos descriptores.
//
// GOTCHAS
//   - OVERFLOW: la suma de una imagen 8-bit de 3000x3000 pasa de 2^31. La tabla
//     debe ser de 64 bits (long long), no int. Esto lo preguntan.
//   - Se usa una tabla de (H+1) x (W+1) con fila y columna 0 a cero: evita los
//     "if (y==0)" dentro del bucle y hace la fórmula uniforme.
//   - La fórmula de inclusión-exclusión es +D -B -C +A: pinta el rectángulo en
//     un papel si dudas del signo.
//   - Aquí el borde NO se replica: la ventana se recorta y se divide entre el
//     número REAL de píxeles incluidos.

#include <algorithm>
#include <cmath>
#include <iostream>
#include <string>
#include <vector>
using namespace std;

using Image    = vector<vector<int>>;         // escala de grises 0..255
using Integral = vector<vector<long long>>;   // (H+1) x (W+1)

// ===========================================================================
// 18.a — integralImage
//   Devuelve S de tamaño (H+1) x (W+1) tal que
//       S[y][x] = suma de img[0..y-1][0..x-1]
//   (fila 0 y columna 0 llenas de ceros).
//   Recurrencia: S[y][x] = img[y-1][x-1] + S[y-1][x] + S[y][x-1] - S[y-1][x-1]
// ---------------------------------------------------------------------------
Integral integralImage(const Image& img) {
    int W = img.size();
    int H = img[0].size();
    vector<vector<long long>> Integral(H+1, vector<long long>(W+1)); 
    for (int y = 1;y <= H; ++y) {
        for (int x = 1;x <= W; ++x) {
            Integral[y][x] = img[y-1][x-1] + Integral[y-1][x] + Integral[y][x-1] - Integral[y-1][x-1]; 
        }
    }
    return Integral;
}

// ===========================================================================
// 18.b — rectSum
//   Suma de img en el rectángulo INCLUSIVO [y0..y1] x [x0..x1], en O(1).
//   Asume 0 <= y0 <= y1 < H y 0 <= x0 <= x1 < W.
// ---------------------------------------------------------------------------
long long rectSum(const Integral& S, int y0, int x0, int y1, int x1) {
    // TODO
    auto result = S[y1][x1] - S[y0][x1] - S[y1][x0] + S[y0][x0]; 
    return result;
}

// ===========================================================================
// 18.c — boxBlurFast
//   Blur de media con ventana k x k (k impar) usando la imagen integral:
//   O(1) por píxel, independiente de k.
//   En los bordes la ventana se RECORTA y se divide entre el número real de
//   píxeles. Redondea al entero más cercano.
// ---------------------------------------------------------------------------
Image boxBlurFast(const Image& img, int k) {
    // TODO
    return {};
}

// ===========================================================================
//                        TEST HARNESS (no tocar)
// ===========================================================================
static int g_pass = 0, g_fail = 0;
void check(bool ok, const string& name) {
    (ok ? g_pass : g_fail)++;
    cout << (ok ? "  [PASS] " : "  [FAIL] ") << name << "\n";
}

// Referencia lenta O(H*W*k*k) para contrastar 18.c
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
    Image img = {{1,2,3},
                 {4,5,6},
                 {7,8,9}};

    // --- 18.a ---------------------------------------------------------------
    {
        Integral S = integralImage(img);
        bool okDim = S.size() == 4 && S[0].size() == 4;
        check(okDim, "18.a tabla de (H+1)x(W+1)");
        if (okDim) {
            check(S[0][0] == 0 && S[0][3] == 0 && S[3][0] == 0, "18.a fila y columna 0 a cero");
            check(S[1][1] == 1 && S[2][2] == 12 && S[3][3] == 45, "18.a acumulados correctos");
        }
        check(integralImage({}).size() <= 1, "18.a imagen vacía no revienta");
    }

    // --- 18.b ---------------------------------------------------------------
    {
        Integral S = integralImage(img);
        check(rectSum(S, 0, 0, 2, 2) == 45, "18.b suma de toda la imagen");
        check(rectSum(S, 1, 1, 2, 2) == 28, "18.b esquina inferior derecha 2x2");
        check(rectSum(S, 0, 1, 1, 2) == 16, "18.b rectángulo no cuadrado");
        check(rectSum(S, 1, 1, 1, 1) == 5,  "18.b un solo píxel");
        check(rectSum(S, 0, 0, 0, 2) == 6,  "18.b una fila entera");
    }

    // --- 18.c ---------------------------------------------------------------
    {
        Image b = boxBlurFast(img, 3);
        bool okDim = b.size() == 3 && b[0].size() == 3;
        check(okDim, "18.c mantiene el tamaño");
        if (okDim) {
            check(b[1][1] == 5, "18.c centro = 45/9 = 5");
            check(b[0][0] == 3, "18.c esquina = (1+2+4+5)/4 = 3 (ventana recortada)");
        }
        Image id = boxBlurFast(img, 1);
        check(id == img, "18.c k=1 es la identidad");

        // Contraste con la implementación lenta sobre datos aleatorios
        srand(7);
        Image big(20, vector<int>(30));
        for (auto& row : big) for (auto& v : row) v = rand() % 256;
        bool same = true;
        for (int k : {3, 5, 7}) same = same && (boxBlurFast(big, k) == boxBlurNaive(big, k));
        check(same, "18.c coincide con la referencia O(k^2) para k=3,5,7");
    }

    // --- overflow -----------------------------------------------------------
    {
        // 3000*3000*255 = 2.295e9 > INT_MAX (2.147e9): con int se desborda.
        const int N = 3000;
        Image white(N, vector<int>(N, 255));
        Integral S = integralImage(white);
        long long total = S.empty() ? -1 : S[N][N];
        check(total == 2295000000LL, "18.a/b sin overflow: la tabla es de 64 bits");
    }

    cout << "\nResultado: " << g_pass << " passed, " << g_fail << " failed\n";
    return g_fail ? 1 : 0;
}
