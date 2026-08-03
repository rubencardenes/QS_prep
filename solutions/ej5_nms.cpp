// EJ 5 — Non-Maximum Suppression (NMS) — solución de referencia
// Compilar:  g++ -std=c++17 -O2 -Wall solutions/ej5_nms.cpp -o sol5 && ./sol5
// Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

#include <algorithm>
#include <iostream>
#include <numeric>
#include <string>
#include <vector>
using namespace std;

struct Box { double x1, y1, x2, y2, score; };

// --- EJ 4, necesario aquí ---------------------------------------------------
double iou(const Box& a, const Box& b) {
    double ix1 = max(a.x1, b.x1), iy1 = max(a.y1, b.y1);
    double ix2 = min(a.x2, b.x2), iy2 = min(a.y2, b.y2);
    double iw = max(0.0, ix2 - ix1), ih = max(0.0, iy2 - iy1);
    double inter = iw * ih;
    double areaA = max(0.0,(a.x2-a.x1)) * max(0.0,(a.y2-a.y1));
    double areaB = max(0.0,(b.x2-b.x1)) * max(0.0,(b.y2-b.y1));
    double uni = areaA + areaB - inter;
    return uni <= 0.0 ? 0.0 : inter / uni;
}

// ---------------------------------------------------------------------------
// EJ 5 — Non-Maximum Suppression. Devuelve índices conservados, ordenados por
// score descendente, eliminando cajas con IoU > iou_thr respecto a una mejor.
// Complejidad O(n^2) en el peor caso (n = nº de cajas) + O(n log n) del sort.
vector<int> nms(const vector<Box>& boxes, double iou_thr) {
    int n = boxes.size();
    vector<int> idx(n);
    iota(idx.begin(), idx.end(), 0);
    sort(idx.begin(), idx.end(), [&](int i, int j){
        return boxes[i].score > boxes[j].score; });
    vector<char> removed(n, 0);
    vector<int> keep;
    for (int ii = 0; ii < n; ++ii) {
        int i = idx[ii];
        if (removed[i]) continue;
        keep.push_back(i);
        for (int jj = ii+1; jj < n; ++jj) {
            int j = idx[jj];
            if (removed[j]) continue;
            if (iou(boxes[i], boxes[j]) > iou_thr) removed[j] = 1;
        }
    }
    return keep;
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
        vector<Box> bs = {
            {0,0,2,2,0.9}, {0.1,0.1,2.1,2.1,0.8},  // muy solapadas -> se queda la 0
            {5,5,7,7,0.7}};                          // separada -> se queda
        auto k = nms(bs, 0.5);
        sort(k.begin(), k.end());
        check(k.size()==2 && k[0]==0 && k[1]==2, "EJ5 NMS conserva {0,2}");
    }

    cout << "\nResultado: " << g_pass << " passed, " << g_fail << " failed\n";
    return g_fail ? 1 : 0;
}
