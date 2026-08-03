// EJ 20 — Cola de frames thread-safe con capacidad limitada (productor/consumidor)
//
// CÓMO USARLO
//   1. Rellena los métodos marcados con  // TODO.
//   2. Compila y ejecuta:   make ej20
//   3. Cronométrate: apunta a ~30 min.
//
// CONTEXTO TIPO ENTREVISTA (el más "de sistemas" del lote)
//   "En la Jetson tenemos un hilo de captura a 60 fps y un hilo de inferencia
//    que tarda 25 ms por frame. Escribe la cola que los conecta. ¿Qué pasa
//    cuando el consumidor no da abasto?"
//
//   Y la respuesta correcta NO es "que crezca la cola": eso dispara la latencia
//   y acaba en OOM. En tiempo real se limita la capacidad y se elige política:
//     - push()            bloquea al productor (contrapresión: bueno si leer de
//                         disco/fichero, malo con una cámara en vivo).
//     - pushDropOldest()  tira el frame más viejo (bueno en vivo: prefieres el
//                         frame actual a uno de hace 300 ms).
//   Saber explicar ese trade-off vale más que la implementación.
//
// GOTCHAS
//   - condition_variable SIEMPRE con el predicado en el wait: hay despertares
//     espurios. `cv.wait(lock, [&]{ return ...; })` te lo resuelve.
//   - Hace falta un estado "cerrada" para que los consumidores bloqueados puedan
//     salir; si no, al terminar el programa se quedan colgados y nunca hace join.
//   - notify_all al cerrar; notify_one basta para el flujo normal.
//   - La cola debe aceptar tipos MOVE-ONLY (un frame es un buffer grande: nunca
//     se copia). Usa std::move al meter y al sacar.
//   - size() también necesita el mutex, y por eso el mutex es `mutable`.

#include <atomic>
#include <chrono>
#include <condition_variable>
#include <deque>
#include <iostream>
#include <memory>
#include <mutex>
#include <string>
#include <thread>
#include <vector>
using namespace std;

// ===========================================================================
// 20 — FrameQueue<T>
// ---------------------------------------------------------------------------
template <class T>
class FrameQueue {
public:
    explicit FrameQueue(size_t capacity) : cap_(capacity ? capacity : 1) {}

    // No copiable ni movible: contiene un mutex.
    FrameQueue(const FrameQueue&) = delete;
    FrameQueue& operator=(const FrameQueue&) = delete;

    // Bloquea mientras esté llena. Devuelve false si la cola está cerrada.
    bool push(T item) {
        // TODO
        return false;
    }

    // Nunca bloquea: si está llena descarta el elemento MÁS VIEJO.
    // Devuelve true si ha tenido que descartar algo (útil para contar frames perdidos).
    bool pushDropOldest(T item) {
        // TODO
        return false;
    }

    // Bloquea mientras esté vacía. Devuelve false si está cerrada Y vacía.
    bool pop(T& out) {
        // TODO
        return false;
    }

    // Despierta a todos los bloqueados; después de esto push() falla y pop()
    // sigue devolviendo lo que quede pendiente hasta vaciarla.
    void close() {
        // TODO
    }

    size_t size() const {
        // TODO
        return 0;
    }

private:
    mutable mutex mtx_;
    condition_variable notEmpty_, notFull_;
    deque<T> q_;
    size_t cap_;
    bool closed_ = false;
};

// ===========================================================================
//                        TEST HARNESS (no tocar)
// ===========================================================================
static int g_pass = 0, g_fail = 0;
void check(bool ok, const string& name) {
    (ok ? g_pass : g_fail)++;
    cout << (ok ? "  [PASS] " : "  [FAIL] ") << name << "\n";
}

int main() {
    // --- FIFO básico --------------------------------------------------------
    {
        FrameQueue<int> q(4);
        check(q.push(1) && q.push(2) && q.push(3), "20 push devuelve true en cola abierta");
        check(q.size() == 3, "20 size() refleja los elementos pendientes");
        int v = 0;
        bool ok = q.pop(v) && v == 1;
        ok = ok && q.pop(v) && v == 2;
        ok = ok && q.pop(v) && v == 3;
        check(ok, "20 orden FIFO");
        check(q.size() == 0, "20 queda vacía");
    }

    // --- cerrada ------------------------------------------------------------
    {
        FrameQueue<int> q(4);
        q.push(1);
        q.close();
        check(!q.push(2), "20 push falla en cola cerrada");
        int v = 0;
        check(q.pop(v) && v == 1, "20 pop sigue drenando lo pendiente tras close()");
        check(!q.pop(v), "20 pop falla cuando está cerrada y vacía");
    }

    // --- move-only ----------------------------------------------------------
    {
        FrameQueue<unique_ptr<int>> q(2);
        q.push(make_unique<int>(42));
        unique_ptr<int> p;
        bool ok = q.pop(p) && p && *p == 42;
        check(ok, "20 soporta tipos move-only (unique_ptr)");
    }

    // --- drop-oldest --------------------------------------------------------
    {
        FrameQueue<int> q(2);
        q.push(1); q.push(2);
        check(q.pushDropOldest(3), "20 pushDropOldest avisa de que ha descartado");
        int a = 0, b = 0;
        q.pop(a); q.pop(b);
        check(a == 2 && b == 3, "20 descarta el más viejo y conserva el más nuevo");
        check(q.size() == 0 && !q.pushDropOldest(4) && q.size() == 1,
              "20 con hueco libre no descarta nada");
    }

    // --- close() despierta a un consumidor bloqueado -------------------------
    {
        FrameQueue<int> q(2);
        bool result = true;
        thread consumer([&]{ int v; result = q.pop(v); });
        this_thread::sleep_for(chrono::milliseconds(50));
        q.close();
        consumer.join();
        check(!result, "20 close() desbloquea a un consumidor en espera");
    }

    // --- push bloquea cuando está llena --------------------------------------
    {
        FrameQueue<int> q(1);
        q.push(1);
        atomic<bool> finished{false};
        thread producer([&]{ q.push(2); finished = true; });
        this_thread::sleep_for(chrono::milliseconds(50));
        bool blocked = !finished && q.size() == 1;
        int v; q.pop(v);                       // hace hueco -> el productor continúa
        producer.join();
        check(blocked, "20 push bloquea mientras la cola está llena");
        check(finished && q.size() == 1, "20 el productor continúa al liberarse hueco");
    }

    // --- estrés: 2 productores, 3 consumidores -------------------------------
    {
        const int PROD = 2, CONS = 3, N = 500;
        FrameQueue<int> q(8);
        vector<thread> ts;
        atomic<long long> total{0};
        atomic<int> received{0};

        for (int c = 0; c < CONS; ++c)
            ts.emplace_back([&]{ int v; while (q.pop(v)) { total += v; ++received; } });
        for (int p = 0; p < PROD; ++p)
            ts.emplace_back([&]{ for (int i = 1; i <= N; ++i) q.push(i); });

        for (int i = CONS; i < (int)ts.size(); ++i) ts[i].join();   // esperar productores
        q.close();                                                  // luego cerrar
        for (int i = 0; i < CONS; ++i) ts[i].join();

        long long expected = (long long)PROD * N * (N + 1) / 2;
        check(total == expected, "20 no se pierde ni se duplica ningún elemento");
        check(received == PROD * N, "20 se consumen exactamente los producidos");
    }

    cout << "\nResultado: " << g_pass << " passed, " << g_fail << " failed\n";
    return g_fail ? 1 : 0;
}
