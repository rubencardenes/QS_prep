// EJ 20 — Cola de frames thread-safe con capacidad limitada — solución de referencia
// Compilar:  make sol20
// Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

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

// ---------------------------------------------------------------------------
// Dos condition_variable (notEmpty_/notFull_) en vez de una: así al liberarse
// un hueco solo se despierta a los productores y al llegar un dato solo a los
// consumidores. Con una sola cv funciona igual pero despiertas al doble de
// hilos para nada (thundering herd).
//
// Todos los wait llevan predicado: protege de despertares espurios Y hace el
// código legible ("espera hasta que haya sitio o esté cerrada").
// ---------------------------------------------------------------------------
template <class T>
class FrameQueue {
public:
    explicit FrameQueue(size_t capacity) : cap_(capacity ? capacity : 1) {}

    FrameQueue(const FrameQueue&) = delete;
    FrameQueue& operator=(const FrameQueue&) = delete;

    bool push(T item) {
        unique_lock<mutex> lock(mtx_);
        notFull_.wait(lock, [this] { return q_.size() < cap_ || closed_; });
        if (closed_) return false;
        q_.push_back(std::move(item));          // move: un frame no se copia
        lock.unlock();                          // desbloquear ANTES de notificar
        notEmpty_.notify_one();                 // evita que el despertado choque con el mutex
        return true;
    }

    bool pushDropOldest(T item) {
        unique_lock<mutex> lock(mtx_);
        if (closed_) return false;
        bool dropped = false;
        if (q_.size() >= cap_) { q_.pop_front(); dropped = true; }
        q_.push_back(std::move(item));
        lock.unlock();
        notEmpty_.notify_one();
        return dropped;
    }

    bool pop(T& out) {
        unique_lock<mutex> lock(mtx_);
        notEmpty_.wait(lock, [this] { return !q_.empty() || closed_; });
        if (q_.empty()) return false;           // cerrada y vacía (no antes: hay que drenar)
        out = std::move(q_.front());
        q_.pop_front();
        lock.unlock();
        notFull_.notify_one();
        return true;
    }

    void close() {
        {
            lock_guard<mutex> lock(mtx_);
            closed_ = true;
        }
        notEmpty_.notify_all();                 // all: puede haber varios esperando
        notFull_.notify_all();
    }

    size_t size() const {
        lock_guard<mutex> lock(mtx_);           // por eso mtx_ es mutable
        return q_.size();
    }

private:
    mutable mutex mtx_;
    condition_variable notEmpty_, notFull_;
    deque<T> q_;
    size_t cap_;
    bool closed_ = false;
};

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
    {
        FrameQueue<int> q(4);
        q.push(1);
        q.close();
        check(!q.push(2), "20 push falla en cola cerrada");
        int v = 0;
        check(q.pop(v) && v == 1, "20 pop sigue drenando lo pendiente tras close()");
        check(!q.pop(v), "20 pop falla cuando está cerrada y vacía");
    }
    {
        FrameQueue<unique_ptr<int>> q(2);
        q.push(make_unique<int>(42));
        unique_ptr<int> p;
        check(q.pop(p) && p && *p == 42, "20 soporta tipos move-only (unique_ptr)");
    }
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
    {
        FrameQueue<int> q(2);
        bool result = true;
        thread consumer([&]{ int v; result = q.pop(v); });
        this_thread::sleep_for(chrono::milliseconds(50));
        q.close();
        consumer.join();
        check(!result, "20 close() desbloquea a un consumidor en espera");
    }
    {
        FrameQueue<int> q(1);
        q.push(1);
        atomic<bool> finished{false};
        thread producer([&]{ q.push(2); finished = true; });
        this_thread::sleep_for(chrono::milliseconds(50));
        bool blocked = !finished && q.size() == 1;
        int v; q.pop(v);
        producer.join();
        check(blocked, "20 push bloquea mientras la cola está llena");
        check(finished && q.size() == 1, "20 el productor continúa al liberarse hueco");
    }
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

        for (int i = CONS; i < (int)ts.size(); ++i) ts[i].join();
        q.close();
        for (int i = 0; i < CONS; ++i) ts[i].join();

        long long expected = (long long)PROD * N * (N + 1) / 2;
        check(total == expected, "20 no se pierde ni se duplica ningún elemento");
        check(received == PROD * N, "20 se consumen exactamente los producidos");
    }

    cout << "\nResultado: " << g_pass << " passed, " << g_fail << " failed\n";
    return g_fail ? 1 : 0;
}
