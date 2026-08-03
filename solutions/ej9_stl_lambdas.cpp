// EJ 9 — STL: algoritmos, lambdas y structured bindings — solución de referencia
// Compilar:  g++ -std=c++17 -O2 -Wall solutions/ej9_stl_lambdas.cpp -o sol9 && ./sol9
// Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

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

// ---------------------------------------------------------------------------
// EJ 9a — topKByScore. Complejidad: O(n log n) por el sort.
vector<Detection> topKByScore(vector<Detection> dets, int k) {
    sort(dets.begin(), dets.end(),
         [](const Detection& a, const Detection& b) { return a.score > b.score; });
    size_t n = min(static_cast<size_t>(k), dets.size());
    dets.resize(n);
    return dets;
}

// ---------------------------------------------------------------------------
// EJ 9b — labelHistogram. Complejidad: O(n).
unordered_map<string, int> labelHistogram(const vector<Detection>& dets) {
    unordered_map<string, int> hist;
    for (const auto& d : dets) ++hist[d.label];
    return hist;
}

// ---------------------------------------------------------------------------
// EJ 9c — meanScoreAbove. Complejidad: O(n).
double meanScoreAbove(const vector<Detection>& dets, float threshold) {
    double sum = 0.0;
    int count = 0;
    for (const auto& d : dets) {
        if (d.score > threshold) {
            sum += d.score;
            ++count;
        }
    }
    return count == 0 ? 0.0 : sum / count;
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
