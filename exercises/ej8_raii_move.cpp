// EJ 8 — Buffer con RAII y move semantics
//
// CÓMO USARLO
//   1. Rellena los métodos marcados con  // TODO.
//   2. Compila y ejecuta:
//        g++ -std=c++17 -O2 -Wall exercises/ej8_raii_move.cpp -o ej8 && ./ej8
//   3. Cronométrate: apunta a ~15-20 min.
//   4. Solo si te atascas, mira solutions/ej8_raii_move.cpp.

#include <cstdint>
#include <iostream>
#include <string>
#include <utility>
#include <vector>
using namespace std;

// ===========================================================================
// EJ 8 — Buffer con RAII y move semantics
//   Clase que posee un buffer contiguo (vector<uint8_t>) de rows*cols bytes.
//   Implementa el rule-of-5 a mano:
//     - constructor(rows, cols): reserva y pone a 0
//     - copy ctor / copy assignment: copia profunda, incrementa s_copyCount
//     - move ctor / move assignment: roba el buffer (noexcept), sin copiar
//     - at(r,c) y at(r,c) const: acceso al elemento (r,c) en row-major
//   Pistas de senior: move debe dejar el origen en un estado válido y vacío;
//   nada de new/delete crudos; marca los moves noexcept.
// ---------------------------------------------------------------------------
class Buffer {
public:
    static int s_copyCount;

    Buffer(int rows, int cols) {
        // TODO
    }

    // Copy
    Buffer(const Buffer& other) {
        // TODO
    }
    Buffer& operator=(const Buffer& other) {
        // TODO
        return *this;
    }

    // Move
    Buffer(Buffer&& other) noexcept {
        // TODO
    }
    Buffer& operator=(Buffer&& other) noexcept {
        // TODO
        return *this;
    }

    uint8_t& at(int r, int c) {
        // TODO
        static uint8_t dummy = 0;
        return dummy;
    }
    const uint8_t& at(int r, int c) const {
        // TODO
        static uint8_t dummy = 0;
        return dummy;
    }

    int rows() const { return rows_; }
    int cols() const { return cols_; }

private:
    int rows_ = 0, cols_ = 0;
    vector<uint8_t> data_;
};

int Buffer::s_copyCount = 0;

// ===========================================================================
//                        TEST HARNESS (no tocar)
// ===========================================================================
static int g_pass = 0, g_fail = 0;
void check(bool ok, const string& name) {
    (ok ? g_pass : g_fail)++;
    cout << (ok ? "  [PASS] " : "  [FAIL] ") << name << "\n";
}

int main() {
    { Buffer a(2, 2);
      a.at(0,0) = 10; a.at(1,1) = 20;
      check(a.rows() == 2 && a.cols() == 2, "EJ8 dimensiones tras construir");
      check(a.at(0,0) == 10 && a.at(1,1) == 20, "EJ8 escritura/lectura at()"); }

    { Buffer a(2, 2);
      a.at(0,0) = 5;
      Buffer::s_copyCount = 0;
      Buffer b(std::move(a));
      check(b.at(0,0) == 5, "EJ8 move ctor transfiere datos");
      check(Buffer::s_copyCount == 0, "EJ8 move ctor no copia");
      check(a.rows() == 0 && a.cols() == 0, "EJ8 origen queda vacio tras move"); }

    { Buffer a(2, 2);
      a.at(0,0) = 7;
      Buffer b(1, 1);
      Buffer::s_copyCount = 0;
      b = a;
      check(b.at(0,0) == 7, "EJ8 copy assignment copia datos");
      check(Buffer::s_copyCount == 1, "EJ8 copy assignment incrementa contador");
      b.at(0,0) = 99;
      check(a.at(0,0) == 7, "EJ8 copia es profunda (independiente del original)"); }

    cout << "\nResultado: " << g_pass << " passed, " << g_fail << " failed\n";
    return g_fail ? 1 : 0;
}
