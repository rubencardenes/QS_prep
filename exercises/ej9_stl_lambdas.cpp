// EJ 9 — STL: algoritmos, lambdas y structured bindings
//
// CÓMO USARLO
//   1. Rellena las funciones marcadas con  // TODO.
//   2. Compila y ejecuta:
//        g++ -std=c++17 -O2 -Wall exercises/ej9_stl_lambdas.cpp -o ej9 && ./ej9
//   3. Cronométrate: apunta a ~15-20 min.
//   4. Solo si te atascas, mira solutions/ej9_stl_lambdas.cpp.

#include <algorithm>
#include <cmath>
#include <iostream>
#include <numeric>
#include <string>
#include <unordered_map>
#include <vector>
using namespace std;

struct Detection {
    string label;
    float score;
};

// ===========================================================================
// EJ 9a — topKByScore
//   Devuelve las k detecciones con mayor score, ordenadas de mayor a menor.
//   Usa std::sort con una lambda como comparador. Si k > dets.size(),
//   devuelve todas. Complejidad esperada: O(n log n).
// ---------------------------------------------------------------------------
vector<Detection> topKByScore(vector<Detection> dets, int k) {
    if (k > dets.size()) {
        return dets;
    }
    sort(dets.begin(), dets.end(), [&](Detection a, Detection b){
        return a.score > b.score; });
    vector<Detection> dets_out(k);
    dets.resize(k);
    return dets;
}

// ===========================================================================
// EJ 9b — labelHistogram
//   Cuenta cuántas detecciones hay de cada label.
// ---------------------------------------------------------------------------
unordered_map<string, int> labelHistogram(const vector<Detection>& dets) {
    unordered_map<string, int> hist;
    for (int i=0;i<dets.size();++i) {
        hist[dets[i].label] += 1;
    }
    return hist;
}

// ===========================================================================
// EJ 9c — meanScoreAbove
//   Media del score de las detecciones con score > threshold.
//   Usa std::count_if / std::accumulate o un simple bucle. Devuelve 0.0
//   si no hay ninguna que cumpla el umbral.
// ---------------------------------------------------------------------------
double meanScoreAbove(const vector<Detection>& dets, float threshold) {
    int N = 0;
    float accum = 0;
    for (int i=0;i<dets.size();++i) {
        if (dets[i].score > threshold) {
            accum += dets[i].score;
            N++;
        }
    }
    if (N > 0) {
       return accum / N;
    }
    return 0.0;
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
    vector<Detection> dets = {
        {"person", 0.9f}, {"car", 0.4f}, {"person", 0.7f},
        {"dog", 0.6f}, {"car", 0.95f}
    };

    { auto top = topKByScore(dets, 3);
      check(top.size() == 3, "EJ9a topK tamano correcto");
      check(top[0].score == 0.95f && top[1].score == 0.9f && top[2].score == 0.7f,
            "EJ9a topK orden descendente"); }

    { auto top = topKByScore(dets, 100);
      check(top.size() == dets.size(), "EJ9a topK con k mayor que el tamano devuelve todo"); }

    { auto hist = labelHistogram(dets);
      check(hist["person"] == 2 && hist["car"] == 2 && hist["dog"] == 1,
            "EJ9b histograma cuenta por label"); }

    { double m = meanScoreAbove(dets, 0.5f);
      check(fabs(m - 0.7875) < 1e-4, "EJ9c media de scores > 0.5"); }

    { double m = meanScoreAbove(dets, 0.99f);
      check(m == 0.0, "EJ9c sin elementos devuelve 0.0"); }

    cout << "\nResultado: " << g_pass << " passed, " << g_fail << " failed\n";
    return g_fail ? 1 : 0;
}
