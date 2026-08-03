// EJ 12 — Concurrencia: std::thread, std::mutex, std::atomic
//
// CÓMO USARLO
//   1. Rellena las funciones marcadas con  // TODO.
//   2. Compila y ejecuta (enlaza pthread):
//        g++ -std=c++17 -O2 -Wall -pthread exercises/ej12_concurrency.cpp -o ej12 && ./ej12
//   3. Cronométrate: apunta a ~20 min.
//   4. Solo si te atascas, mira solutions/ej12_concurrency.cpp.

#include <algorithm>
#include <atomic>
#include <iostream>
#include <mutex>
#include <string>
#include <thread>
#include <vector>
using namespace std;

// ===========================================================================
// EJ 12a — parallelSum
//   Suma un vector<int> repartiendo el trabajo entre numThreads hilos.
//   Cada hilo debe calcular su suma parcial en su propio slot (sin estado
//   compartido mutable). El hilo principal suma los parciales tras hacer
//   join a todos los hilos.
// ---------------------------------------------------------------------------
long long parallelSum(const vector<int>& data, int numThreads) {
    // TODO
    return 0;
}

// ===========================================================================
// EJ 12b — atomicCountAbove
//   Cuenta cuántos elementos de data son > threshold, repartiendo el trabajo
//   entre numThreads hilos que incrementan un contador COMPARTIDO usando
//   std::atomic<long long> (fetch_add), sin locks.
// ---------------------------------------------------------------------------
long long atomicCountAbove(const vector<int>& data, int threshold, int numThreads) {
    // TODO
    return 0;
}

// ===========================================================================
// EJ 12c — mutexCollectAbove
//   Recolecta en un vector<int> COMPARTIDO los elementos > threshold,
//   repartiendo el trabajo entre numThreads hilos que protegen el acceso
//   al vector compartido con std::mutex. El orden del resultado no importa
//   (el test lo ordena antes de comparar).
// ---------------------------------------------------------------------------
vector<int> mutexCollectAbove(const vector<int>& data, int threshold, int numThreads) {
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

int main() {
    vector<int> data;
    for (int i = 1; i <= 1000; ++i) data.push_back(i);   // 1..1000

    { long long s = parallelSum(data, 4);
      check(s == 500500, "EJ12a suma paralela de 1..1000"); }

    { long long s = parallelSum(data, 1);
      check(s == 500500, "EJ12a funciona con 1 hilo"); }

    { long long c = atomicCountAbove(data, 990, 4);
      check(c == 10, "EJ12b cuenta atomica de elementos > 990 (991..1000)"); }

    { auto v = mutexCollectAbove(data, 995, 4);
      sort(v.begin(), v.end());
      vector<int> expected = {996,997,998,999,1000};
      check(v == expected, "EJ12c recoleccion con mutex de elementos > 995"); }

    cout << "\nResultado: " << g_pass << " passed, " << g_fail << " failed\n";
    return g_fail ? 1 : 0;
}
