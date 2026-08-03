// EJ 5 — Non-Maximum Suppression (NMS)
//
// CÓMO USARLO
//   1. Rellena la función marcada con  // TODO.
//   2. Compila y ejecuta:
//        g++ -std=c++17 -O2 -Wall exercises/ej5_nms.cpp -o ej5 && ./ej5
//   3. Cronométrate: apunta a ~10-15 min.
//   4. Solo si te atascas, mira solutions/ej5_nms.cpp.
//
// NOTA: iou() viene ya resuelto aquí (es el EJ4) para que este fichero sea
// autónomo. Si quieres practicar los dos juntos, bórralo y reescríbelo.

#include <algorithm>
#include <iostream>
#include <numeric>
#include <string>
#include <vector>
using namespace std;

struct Box { double x1, y1, x2, y2, score; };

// --- Dado (EJ 4) ------------------------------------------------------------
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

// ===========================================================================
// EJ 5 — Non-Maximum Suppression (NMS)  [usa iou()]
//   Ordena las cajas por score desc. Recorre: conserva la de mayor score y
//   descarta las que tengan IoU > iou_thr con ella. Repite con las restantes.
//   Devuelve los ÍNDICES conservados (referidos al vector original).
//   Es EL algoritmo de post-proceso en detección de objetos: espera que caiga.
// ---------------------------------------------------------------------------
vector<int> nms(const vector<Box>& boxes, double iou_thr) {
    // Sort boxes
    int n = boxes.size();
    vector<int> idx(n);
    iota(idx.begin(), idx.end(), 0);
    sort(idx.begin(), idx.end(), [&](int i, int j){
        return boxes[i].score > boxes[j].score; });
    for (int i=0;i < boxes_sorted.size(); ++i) {
        
        
    }
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

int main() {
    { vector<Box> bs = {{0,0,2,2,0.9},          // muy solapadas -> se queda la 0
                        {0.1,0.1,2.1,2.1,0.8},
                        {5,5,7,7,0.7}};          // separada -> se queda
      auto k = nms(bs, 0.5);
      sort(k.begin(), k.end());
      check(k.size()==2 && k[0]==0 && k[1]==2, "EJ5 NMS conserva {0,2}"); }

    cout << "\nResultado: " << g_pass << " passed, " << g_fail << " failed\n";
    return g_fail ? 1 : 0;
}
