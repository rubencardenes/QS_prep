// EJ 12 — Concurrencia: std::thread, std::mutex, std::atomic — solución de referencia
// Compilar:  g++ -std=c++17 -O2 -Wall -pthread solutions/ej12_concurrency.cpp -o sol12 && ./sol12
// Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

#include <algorithm>
#include <atomic>
#include <iostream>
#include <mutex>
#include <string>
#include <thread>
#include <vector>
using namespace std;

// ---------------------------------------------------------------------------
// EJ 12a — parallelSum. Cada hilo escribe en su propio slot -> sin datos
// compartidos mutables, sin necesidad de sincronizacion.
long long parallelSum(const vector<int>& data, int numThreads) {
    numThreads = max(1, numThreads);
    vector<long long> partials(numThreads, 0);
    vector<thread> threads;
    size_t n = data.size();
    size_t chunk = (n + numThreads - 1) / numThreads;

    for (int t = 0; t < numThreads; ++t) {
        size_t begin = t * chunk;
        size_t end = min(n, begin + chunk);
        threads.emplace_back([&data, &partials, t, begin, end] {
            long long s = 0;
            for (size_t i = begin; i < end; ++i) s += data[i];
            partials[t] = s;
        });
    }
    for (auto& th : threads) th.join();

    long long total = 0;
    for (long long p : partials) total += p;
    return total;
}

// ---------------------------------------------------------------------------
// EJ 12b — atomicCountAbove. Contador compartido sin locks via fetch_add.
long long atomicCountAbove(const vector<int>& data, int threshold, int numThreads) {
    numThreads = max(1, numThreads);
    atomic<long long> count{0};
    vector<thread> threads;
    size_t n = data.size();
    size_t chunk = (n + numThreads - 1) / numThreads;

    for (int t = 0; t < numThreads; ++t) {
        size_t begin = t * chunk;
        size_t end = min(n, begin + chunk);
        threads.emplace_back([&data, &count, threshold, begin, end] {
            long long local = 0;
            for (size_t i = begin; i < end; ++i)
                if (data[i] > threshold) ++local;
            count.fetch_add(local, memory_order_relaxed);
        });
    }
    for (auto& th : threads) th.join();
    return count.load();
}

// ---------------------------------------------------------------------------
// EJ 12c — mutexCollectAbove. Vector compartido protegido con mutex.
vector<int> mutexCollectAbove(const vector<int>& data, int threshold, int numThreads) {
    numThreads = max(1, numThreads);
    vector<int> result;
    mutex mtx;
    vector<thread> threads;
    size_t n = data.size();
    size_t chunk = (n + numThreads - 1) / numThreads;

    for (int t = 0; t < numThreads; ++t) {
        size_t begin = t * chunk;
        size_t end = min(n, begin + chunk);
        threads.emplace_back([&data, &result, &mtx, threshold, begin, end] {
            vector<int> local;
            for (size_t i = begin; i < end; ++i)
                if (data[i] > threshold) local.push_back(data[i]);
            lock_guard<mutex> lock(mtx);
            result.insert(result.end(), local.begin(), local.end());
        });
    }
    for (auto& th : threads) th.join();
    return result;
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
    vector<int> data;
    for (int i = 1; i <= 1000; ++i) data.push_back(i);

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
