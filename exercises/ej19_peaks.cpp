// EJ 19 — Detección de picos: máximos locales 3x3 + top-K por score
//
// CÓMO USARLO
//   1. Rellena la función marcada con  // TODO.
//   2. Compila y ejecuta:   make ej19
//   3. Cronométrate: apunta a ~20 min.
//
// CONTEXTO TIPO ENTREVISTA
//   "matchTemplate / cornerHarris / el heatmap de una red te devuelven un mapa
//    de respuesta continuo. Un objeto genera decenas de píxeles altos contiguos.
//    Dame solo los centros: máximos locales por encima de un umbral, los K
//    mejores." Es el post-proceso de casi cualquier detector basado en heatmaps
//    (CenterNet, keypoints, plantillas).
//
// GOTCHAS
//   - "Máximo local" = ESTRICTAMENTE mayor que sus 8 vecinos. Con >= una meseta
//     de valores iguales devolvería un pico por cada píxel de la meseta.
//   - Los píxeles del borde se comparan solo contra los vecinos que existen.
//   - El orden de salida debe ser DETERMINISTA: score descendente y, a igualdad,
//     el de menor y, luego menor x. Si no, tus tests fallan un día de cada tres.
//   - Para el top-K no ordenes los N elementos: nth_element/partial_sort es
//     O(N log K) en vez de O(N log N). Dilo en voz alta aunque N sea pequeño.

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

// ===========================================================================
// 19 — findPeaks
//   Devuelve los máximos locales (8-vecindad, estrictos) con score >= thr,
//   ordenados por score descendente; a igualdad, menor y y luego menor x.
//   Si topK > 0 devuelve como mucho topK; si topK <= 0, todos.
// ---------------------------------------------------------------------------
vector<Peak> findPeaks(const Response& resp, double thr, int topK) {
    vector<Peak> peaks;
    if (resp.empty()) return {};
    int H = resp.size();
    int W = resp[0].size(); 
    for (int y=0;y<H;++y) {
        for (int x=0;x<W;++x) {
            bool flag_peak = true;
            if (resp[y][x] < thr) continue;
            for (int ny=-1;ny<=1;++ny) {
                for (int nx=-1;nx<=1;++nx) {
                    int yy = ny +y, xx=nx + x; 
                    if (yy < 0 || yy >= H || xx < 0 || xx >= W) continue;
                    if (nx == 0 && ny == 0) continue;
                    if (resp[y][x] <= resp[yy][xx]) {
                       flag_peak = false;
                       break;
                    }
                }
                if (flag_peak != true) break;
            }
            if (flag_peak) {
                peaks.push_back({y, x, resp[y][x]});
            }
        }
    }
    // Now we need to order them 
    sort(peaks.begin(), peaks.end(), [](Peak a, Peak b) {
        if (a.score != b.score) return a.score > b.score;
        if (a.y != b.y) return a.y < b.y;
        return a.x < b.x;
        });
    if (topK > 0 && (int)peaks.size() > topK) peaks.resize(topK);
    return peaks;
}

// ===========================================================================
//                        TEST HARNESS (no tocar)
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
    // Tres picos aislados sobre fondo 0
    Response r = {{0,0,0,0,0},
                  {0,9,0,0,0},
                  {0,0,0,5,0},
                  {0,0,0,0,0},
                  {0,3,0,0,0}};

    // --- básico -------------------------------------------------------------
    {
        vector<Peak> p = findPeaks(r, 1.0, 0);
        check(p.size() == 3, "19 encuentra los 3 picos (obtenidos " + to_string(p.size()) + ")");
        if (p.size() == 3) {
            check(eq(p[0], 1, 1, 9), "19 ordenado por score descendente");
            check(eq(p[1], 2, 3, 5) && eq(p[2], 4, 1, 3), "19 resto del orden correcto");
        }
    }

    // --- umbral y topK ------------------------------------------------------
    {
        check(findPeaks(r, 4.0, 0).size() == 2, "19 el umbral descarta el pico de 3");
        vector<Peak> p = findPeaks(r, 1.0, 1);
        check(p.size() == 1 && eq(p[0], 1, 1, 9), "19 topK=1 devuelve solo el mejor");
        check(findPeaks(r, 1.0, 99).size() == 3, "19 topK mayor que el total no rellena");
        check(findPeaks(r, 100.0, 0).empty(), "19 umbral alto -> vacío");
    }

    // --- mesetas y bordes ---------------------------------------------------
    {
        Response flat = {{0,0,0,0},
                         {0,7,7,0},     // dos vecinos iguales: ninguno es máximo estricto
                         {0,0,0,0}};
        check(findPeaks(flat, 1.0, 0).empty(), "19 una meseta no genera picos (comparación estricta)");

        Response zeros(4, vector<double>(4, 0.0));
        check(findPeaks(zeros, 0.0, 0).empty(), "19 mapa constante no genera picos");

        Response corner = {{8,0,0},
                           {0,0,0},
                           {0,0,4}};
        vector<Peak> p = findPeaks(corner, 1.0, 0);
        check(p.size() == 2 && eq(p[0], 0, 0, 8), "19 los picos en el borde también cuentan");
    }

    // --- desempate determinista ---------------------------------------------
    {
        Response tie = {{0,0,0,0,0},
                        {0,5,0,0,0},
                        {0,0,0,0,0},
                        {0,0,0,5,0},
                        {0,0,0,0,0}};
        vector<Peak> p = findPeaks(tie, 1.0, 0);
        check(p.size() == 2 && eq(p[0], 1, 1, 5) && eq(p[1], 3, 3, 5),
              "19 empate resuelto por (y,x) ascendente");
    }

    // --- degenerados --------------------------------------------------------
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
