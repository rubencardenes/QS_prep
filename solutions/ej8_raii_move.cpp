// EJ 8 — Buffer con RAII y move semantics — solución de referencia
// Compilar:  g++ -std=c++17 -O2 -Wall solutions/ej8_raii_move.cpp -o sol8 && ./sol8
// Úsalo SOLO para comprobar tu respuesta después de intentarlo tú.

#include <cstdint>
#include <iostream>
#include <string>
#include <utility>
#include <vector>
using namespace std;

// ---------------------------------------------------------------------------
// EJ 8 — Buffer con RAII y move semantics (rule-of-5 explícito).
// Complejidad: O(rows*cols) en construcción/copia, O(1) en move.
class Buffer {
public:
    static int s_copyCount;

    Buffer(int rows, int cols)
        : rows_(rows), cols_(cols), data_(static_cast<size_t>(rows) * cols, 0) {}

    // Copy: profunda
    Buffer(const Buffer& other)
        : rows_(other.rows_), cols_(other.cols_), data_(other.data_) {
        ++s_copyCount;
    }
    Buffer& operator=(const Buffer& other) {
        if (this != &other) {
            rows_ = other.rows_;
            cols_ = other.cols_;
            data_ = other.data_;
            ++s_copyCount;
        }
        return *this;
    }

    // Move: roba el buffer, deja el origen vacío
    Buffer(Buffer&& other) noexcept
        : rows_(other.rows_), cols_(other.cols_), data_(std::move(other.data_)) {
        other.rows_ = 0;
        other.cols_ = 0;
    }
    Buffer& operator=(Buffer&& other) noexcept {
        if (this != &other) {
            rows_ = other.rows_;
            cols_ = other.cols_;
            data_ = std::move(other.data_);
            other.rows_ = 0;
            other.cols_ = 0;
        }
        return *this;
    }

    uint8_t& at(int r, int c) {
        return data_.at(static_cast<size_t>(r) * cols_ + c);
    }
    const uint8_t& at(int r, int c) const {
        return data_.at(static_cast<size_t>(r) * cols_ + c);
    }

    int rows() const { return rows_; }
    int cols() const { return cols_; }

private:
    int rows_ = 0, cols_ = 0;
    vector<uint8_t> data_;
};

int Buffer::s_copyCount = 0;

// ===========================================================================
//                               TEST HARNESS
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
