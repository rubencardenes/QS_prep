# C++ moderno — Cheatsheet (Bloque 1)

Todo el código asume C++17 y `using namespace std;` (aceptable en entrevista para ir rápido, nunca en producción).
Los términos técnicos van en inglés porque así te los van a preguntar.

```bash
g++ -std=c++17 -O2 -Wall -Wextra main.cpp -o app
```

---

## 0. Plantilla mental para coderpad

Lo primero que tecleas, sin pensar:

```cpp
#include <iostream>
#include <vector>
#include <string>
#include <algorithm>      // sort, find, min/max, clamp, transform...
#include <numeric>        // accumulate, iota
#include <unordered_map>
#include <queue>
using namespace std;

void print(const vector<int>& v) {
    for (int x : v) cout << x << ' ';
    cout << '\n';
}

int main() {
    vector<int> v{5, 3, 9, 1};
    sort(v.begin(), v.end());
    print(v);                       // 1 3 5 9
    return 0;
}
```

`cout` es tu debugger. No hay más. Imprime pronto y a menudo.

---

# PARTE 1 — Contenedores STL

## 1.1 Tabla de decisión (esto es lo que te preguntan)

| Contenedor | Estructura interna | Acceso | Insertar/borrar | Cuándo lo eliges |
|---|---|---|---|---|
| `vector<T>` | array contiguo | `O(1)` por índice | `O(1)` amortizado al final, `O(n)` en medio | **Por defecto, siempre.** Cache-friendly |
| `array<T,N>` | array fijo en el stack | `O(1)` | — | Tamaño conocido en compilación |
| `deque<T>` | bloques enlazados | `O(1)` por índice | `O(1)` en ambos extremos | Necesitas `push_front` barato |
| `list<T>` | doblemente enlazada | `O(n)` | `O(1)` con iterador | Casi nunca. Mata la caché |
| `map<K,V>` | red-black tree | `O(log n)` | `O(log n)` | Necesitas las **claves ordenadas** |
| `unordered_map<K,V>` | hash table | `O(1)` medio, `O(n)` peor | `O(1)` medio | Lookup rápido, orden irrelevante |
| `set` / `unordered_set` | igual que los maps | igual | igual | Solo te importa la pertenencia |
| `queue<T>` | adaptador sobre `deque` | solo `front`/`back` | `O(1)` | FIFO: **BFS, flood fill** |
| `stack<T>` | adaptador sobre `deque` | solo `top` | `O(1)` | LIFO: DFS iterativo |
| `priority_queue<T>` | heap sobre `vector` | solo `top` | `O(log n)` | Sacar siempre el máximo/mínimo |

**La frase que dices en la entrevista:** *"Por defecto `vector`. Es contiguo, así que el prefetcher de la CPU lo adora; un `list` con la misma complejidad teórica va 10× más lento en la práctica por los cache misses. Solo me muevo de `vector` si el patrón de acceso lo exige."*

---

## 1.2 `std::vector` — el 80 % de tu código

```cpp
vector<int> a;                    // vacío
vector<int> b(10);                // 10 elementos, valor 0 (¡inicializados!)
vector<int> c(10, -1);            // 10 elementos a -1
vector<int> d{1, 2, 3};           // lista de inicialización
vector<int> e(d.begin(), d.end());// copia por rango
vector<vector<int>> grid(H, vector<int>(W, 0));   // matriz H×W a ceros
```

Ojo con la trampa clásica: `vector<int> v(10)` son 10 ceros, pero `vector<int> v{10}` es **un** elemento de valor 10. Las llaves ganan siempre que exista un constructor de `initializer_list`.

### Operaciones

```cpp
v.size()        v.empty()       v.capacity()
v.push_back(x);                 // copia/mueve x
v.emplace_back(args...);        // Se usa para anadir elementos al vector usando el constructor de la classe. 
                                // No aporta nada con respecto a tipos simples como int o float  
                                // CONSTRUYE in-place, sin temporal. Devuelve T& (C++17)
v.pop_back();                   // quita el último. NO devuelve nada (void)
v.front()  v.back()             // referencias al primero/último. UB si está vacío
v[i]                            // sin comprobación de rango → rápido
v.at(i)                         // lanza std::out_of_range → seguro
v.clear();                      // size = 0, capacity intacta
v.resize(n);                    // cambia el tamaño lógico (rellena con 0)
v.reserve(n);                   // reserva capacidad, NO cambia size
v.assign(n, val);               // Asigna el valor val, un total de n veces.
                                // reemplaza el contenido entero, aunque el vector existente sea mas grande.
v.insert(v.begin() + 2, 99);    // O(n): mueve todo lo que viene detrás
v.erase(v.begin() + 2);         // O(n)
v.erase(v.begin()+1, v.begin()+4); // borra rango [1,4)
swap(a, b);                     // O(1): intercambia punteros internos
```

### `reserve` — la optimización que demuestra seniority

```cpp
vector<int> v;
v.reserve(1000);          // una sola asignación de memoria
for (int i = 0; i < 1000; ++i) v.push_back(i);
```

Sin `reserve`, el vector crece duplicando capacidad: reasigna y **copia/mueve todo** unas 10 veces. Con `reserve`, una vez. En un bucle de procesado de imagen esto se nota.

### Borrar por condición: erase-remove idiom

`std::remove` **no borra nada**: reordena el vector dejando los supervivientes al principio y devuelve un iterador al nuevo final. Hay que encadenar `erase`.

```cpp
// Quitar todos los pares
v.erase(remove_if(v.begin(), v.end(), [](int x){ return x % 2 == 0; }), v.end());

// C++20 lo simplifica:  erase_if(v, [](int x){ return x % 2 == 0; });
```

### Invalidación de iteradores (pregunta trampa frecuente)

```cpp
vector<int> v{1,2,3};
int& ref = v[0];
v.push_back(4);      // si reasigna → ref, punteros e iteradores quedan COLGANDO
cout << ref;         // UB
```

Regla: cualquier operación que pueda cambiar la capacidad invalida **todo**. Un `erase` invalida desde el punto borrado hacia el final.

---

## 1.3 `std::queue` — para BFS / flood fill

Es un **adaptador**: no tiene iteradores, no puedes recorrerlo. Solo empujas por detrás y sacas por delante.

```cpp
#include <queue>
queue<int> q;
q.push(1);          q.emplace(2);
q.front()           // el más antiguo (el próximo en salir)
q.back()            // el más reciente
q.pop();            // ELIMINA el front y devuelve void → hay que leer antes de sacar
q.size()  q.empty()
```

El patrón que memorizas, porque flood fill / contar islas cae mucho en roles de CV:

```cpp
// Cuenta componentes conexas de 1s en una grid binaria (4-conectividad)
int countIslands(vector<vector<int>>& g) {
    if (g.empty()) return 0;
    const int H = g.size(), W = g[0].size();
    const int dy[] = {-1, 1, 0, 0};
    const int dx[] = { 0, 0,-1, 1};
    int count = 0;

    for (int sy = 0; sy < H; ++sy) {
        for (int sx = 0; sx < W; ++sx) {
            if (g[sy][sx] != 1) continue;
            ++count;
            queue<pair<int,int>> q;
            q.push({sy, sx});
            g[sy][sx] = 0;                     // marca al ENCOLAR, no al desencolar
            while (!q.empty()) {
                auto [y, x] = q.front();       // structured binding
                q.pop();
                for (int k = 0; k < 4; ++k) {
                    int ny = y + dy[k], nx = x + dx[k];
                    if (ny < 0 || ny >= H || nx < 0 || nx >= W) continue;
                    if (g[ny][nx] != 1) continue;
                    g[ny][nx] = 0;
                    q.push({ny, nx});
                }
            }
        }
    }
    return count;
}
```

**El detalle que te preguntarán:** marcar como visitado al *encolar* y no al *desencolar*. Si marcas al desencolar, el mismo píxel entra en la cola varias veces y en el peor caso explota la memoria.

---

## 1.4 `std::stack` y `std::priority_queue`

```cpp
stack<int> s;
s.push(1);  s.top();  s.pop();  s.empty();
```

`priority_queue` es un **max-heap por defecto** (sale el mayor primero). Esto sorprende a todo el mundo:

```cpp
priority_queue<int> maxHeap;                                  // top() = el mayor
priority_queue<int, vector<int>, greater<int>> minHeap;       // top() = el menor

maxHeap.push(3); maxHeap.push(7); maxHeap.push(5);
cout << maxHeap.top();   // 7
maxHeap.pop();

// Con comparador propio: ordena boxes por score descendente
struct Box { float x, y, w, h, score; };
auto cmp = [](const Box& a, const Box& b){ return a.score < b.score; };  // < → max-heap
priority_queue<Box, vector<Box>, decltype(cmp)> pq(cmp);
```

Mnemotécnica: el comparador de `priority_queue` está **invertido** respecto a `sort`. `less` te da el mayor en el `top`.

---

## 1.5 `map` vs `unordered_map`

```cpp
unordered_map<string, int> m;
m["a"] = 1;                 // ¡INSERTA "a" si no existe!
m.emplace("b", 2);
m.insert({"c", 3});
m.at("a");                  // lanza si no existe
m.count("z");               // 0 o 1
m.contains("z");            // C++20
m.erase("a");
m.size();  m.empty();

// Buscar SIN insertar
if (auto it = m.find("x"); it != m.end())      // if con inicializador (C++17)
    cout << it->second;

// Recorrer
for (const auto& [key, val] : m)               // structured binding sobre pair
    cout << key << " -> " << val << '\n';
```

**El gotcha de `operator[]`:** en un `const map` ni siquiera compila, y en uno mutable inserta un valor por defecto silenciosamente. Para contar frecuencias eso es justo lo que quieres (`++freq[x]` funciona porque el int nuevo vale 0), pero para consultar usa `find` o `at`.

```cpp
unordered_map<int,int> freq;
for (int x : v) ++freq[x];      // idioma estándar de conteo
```

`map` te da las claves **ordenadas** al recorrerlo y soporta `lower_bound`/`upper_bound`. `unordered_map` es más rápido de media pero el orden de iteración es arbitrario y puede degradarse a `O(n)` con colisiones.

---

## 1.6 `std::string` y `std::string_view`

```cpp
string s = "hola";
s.size()  s.empty()  s.substr(1,2)  s.find("la")   // find devuelve string::npos si falla
s += " mundo";       s.push_back('!');
s.c_str()            // const char* para APIs de C
to_string(42);  stoi("42");  stof("3.14");
```

`string_view` es una **vista no propietaria**: puntero + longitud, sin copia. Perfecto para parámetros de solo lectura.

```cpp
void log(string_view msg) { cout << msg << '\n'; }   // no copia, acepta string y const char*

// PELIGRO: colgar la vista
string_view bad = string("temporal");   // el string muere al acabar la línea → UB
```

---

# PARTE 2 — Algoritmos STL

Todos operan sobre **rangos de iteradores** `[first, last)`, con `last` excluido. Están en `<algorithm>` salvo `accumulate`/`iota` que viven en `<numeric>`.

```cpp
sort(v.begin(), v.end());                              // O(n log n), introsort, NO estable
sort(v.begin(), v.end(), greater<int>());              // descendente
stable_sort(v.begin(), v.end());                       // mantiene el orden relativo de iguales
partial_sort(v.begin(), v.begin()+k, v.end());         // solo los k primeros ordenados
nth_element(v.begin(), v.begin()+n/2, v.end());        // O(n) medio → MEDIANA (median filter!)

find(v.begin(), v.end(), 42);                          // O(n), devuelve end() si no está
find_if(v.begin(), v.end(), [](int x){ return x > 10; });
count(v.begin(), v.end(), 42);
binary_search(v.begin(), v.end(), 42);                 // O(log n), requiere ORDENADO
lower_bound(v.begin(), v.end(), 42);                   // primer elemento >= 42

accumulate(v.begin(), v.end(), 0);                     // suma
accumulate(v.begin(), v.end(), 0.0);                   // ¡el tipo del init manda!
transform(v.begin(), v.end(), out.begin(), [](int x){ return x*2; });
for_each(v.begin(), v.end(), [](int& x){ x *= 2; });
iota(v.begin(), v.end(), 0);                           // rellena 0,1,2,3...

*max_element(v.begin(), v.end());                      // devuelve ITERADOR → hay que dereferenciar
auto [mn, mx] = minmax_element(v.begin(), v.end());
reverse(v.begin(), v.end());
fill(v.begin(), v.end(), 0);
any_of / all_of / none_of (v.begin(), v.end(), pred);
clamp(value, lo, hi);                                  // C++17 — para saturar píxeles
unique(v.begin(), v.end());                            // colapsa duplicados ADYACENTES → sort antes
```

### El bug de `accumulate` que cae en entrevistas

```cpp
vector<double> v{1.5, 2.5};
accumulate(v.begin(), v.end(), 0);     // → 3  (¡acumula en int!)
accumulate(v.begin(), v.end(), 0.0);   // → 4.0 correcto
```

Lo mismo con overflow: `accumulate(v.begin(), v.end(), 0)` sobre un vector grande de píxeles desborda `int`. Usa `0LL` o `0.0`.

### Deduplicar

```cpp
sort(v.begin(), v.end());
v.erase(unique(v.begin(), v.end()), v.end());
```

---

# PARTE 3 — Lambdas

Una lambda es un objeto función anónimo. La sintaxis completa:

```cpp
[captura](parámetros) -> tipo_retorno { cuerpo }
```

```cpp
auto suma  = [](int a, int b) { return a + b; };
int factor = 3;
auto porFactor = [factor](int x) { return x * factor; };    // captura por VALOR (copia)
auto acumula   = [&factor](int x) { factor += x; };         // captura por REFERENCIA
auto todo      = [=]() { return factor; };                  // todo por valor (evítalo)
auto todoRef   = [&]() { factor = 0; };                     // todo por referencia (evítalo)
auto mut       = [factor]() mutable { factor++; };          // permite modificar la copia
```

### Valor vs referencia — la decisión que te preguntan

```cpp
vector<function<int()>> fs;
for (int i = 0; i < 3; ++i) {
    fs.push_back([i]  { return i; });   // OK: copia i
    fs.push_back([&i] { return i; });   // BUG: i muere al salir del bucle → dangling
}
```

Regla práctica: **por referencia solo si la lambda no sobrevive al scope actual** (es decir, para algoritmos STL que se ejecutan en el momento). Si la guardas o la pasas a otro hilo, captura por valor.

### Uso con algoritmos

```cpp
// Ordenar bounding boxes por score descendente — el primer paso de NMS
struct Box { float x1, y1, x2, y2, score; };
vector<Box> boxes = /* ... */;
sort(boxes.begin(), boxes.end(),
     [](const Box& a, const Box& b) { return a.score > b.score; });

// Filtrar por umbral
boxes.erase(remove_if(boxes.begin(), boxes.end(),
                      [](const Box& b) { return b.score < 0.5f; }),
            boxes.end());
```

### `std::function` vs lambda directa

```cpp
#include <functional>
function<int(int,int)> op = suma;       // borra el tipo: puede guardar cualquier callable
```

`std::function` es cómoda pero **tiene coste**: llamada indirecta y posible asignación en el heap. En un bucle caliente pasa la lambda como parámetro `template` en su lugar:

```cpp
template <typename F>
void apply(vector<int>& v, F f) { for (int& x : v) x = f(x); }   // se inlinea, coste cero
```

---

# PARTE 4 — RAII y gestión de memoria

## 4.1 ¿Qué significa RAII?

**Resource Acquisition Is Initialization.** El nombre es horrible; la idea es simple:

> **Ligas el ciclo de vida de un recurso al ciclo de vida de un objeto.** El constructor lo adquiere, el destructor lo libera. Como C++ garantiza que el destructor de un objeto en el stack se ejecuta al salir del scope — pase lo que pase, incluida una excepción — el recurso no se puede filtrar.

Recurso = memoria, ficheros, sockets, mutex, handles de CUDA, una `cv::VideoCapture`... cualquier cosa que se adquiere y hay que devolver.

**El problema que resuelve:**

```cpp
// SIN RAII — roto
void process() {
    int* buf = new int[1000];
    if (algo_falla()) return;        // FUGA: nunca llega al delete
    mayThrow();                      // FUGA: la excepción salta el delete
    delete[] buf;
}

// CON RAII — imposible filtrar
void process() {
    vector<int> buf(1000);           // el constructor asigna
    if (algo_falla()) return;        // el destructor libera
    mayThrow();                      // el stack unwinding llama al destructor
}                                    // liberado aquí, siempre
```

`vector`, `string`, `unique_ptr`, `lock_guard`, `fstream` — **todos son RAII**. Por eso en C++ moderno no escribes `new`/`delete` nunca.

**Cómo lo explicas en voz alta:** *"RAII es atar un recurso a la vida de un objeto: adquirir en el constructor, liberar en el destructor. Como el destructor se invoca de forma determinista al salir del scope, incluso durante el stack unwinding de una excepción, te da exception safety gratis y elimina toda una clase de bugs: fugas, double free, use-after-free. Es la razón por la que en C++ moderno no hay `new` crudo."*

Tu propia clase RAII:

```cpp
class FileHandle {
    FILE* f_;
public:
    explicit FileHandle(const char* path) : f_(fopen(path, "rb")) {
        if (!f_) throw runtime_error("no se pudo abrir");
    }
    ~FileHandle() { if (f_) fclose(f_); }

    FileHandle(const FileHandle&) = delete;             // no copiable
    FileHandle& operator=(const FileHandle&) = delete;

    FILE* get() const { return f_; }
};
```

## 4.2 Smart pointers

| Puntero | Ownership | Coste | Cuándo |
|---|---|---|---|
| `unique_ptr<T>` | **exclusivo** | cero overhead | **Por defecto** |
| `shared_ptr<T>` | compartido, refcount atómico | +control block, +atomics | Varios dueños de verdad |
| `weak_ptr<T>` | ninguno, observa | — | Romper ciclos de `shared_ptr` |

```cpp
#include <memory>

auto p = make_unique<Image>(640, 480);      // PREFIERE make_unique a new
p->at(0,0) = 255;
Image* raw = p.get();                       // acceso crudo, NO tomas ownership
auto q = move(p);                           // transferencia: p queda a nullptr
p.reset();                                  // libera explícitamente
// unique_ptr<Image> r = p;                 // ERROR de compilación: no es copiable

auto s = make_shared<Image>(640, 480);
auto s2 = s;                                // refcount = 2
cout << s.use_count();                      // 2 — el objeto muere cuando llega a 0

unique_ptr<int[]> arr = make_unique<int[]>(100);   // arrays: usa vector mejor
```

**Por qué `make_unique` y no `new`:** una sola asignación (en `shared_ptr`, junta objeto y control block), no repites el tipo, y es exception-safe en llamadas como `f(unique_ptr<A>(new A), g())` donde el orden de evaluación podría filtrar.

**Cuándo `shared_ptr`:** solo cuando la propiedad es genuinamente compartida y no sabes quién muere último (p. ej. un frame que consumen varios subsistemas asíncronos). Si dudas, `unique_ptr`. Los ciclos `shared_ptr` A→B→A **nunca se liberan**: ahí entra `weak_ptr`.

**Cuándo un puntero crudo está bien:** como *observador* no propietario, pasado por parámetro. `T*` o `T&` en una firma significa "te presto esto, no lo destruyas". Lo prohibido es un puntero crudo que **posee**.

---

# PARTE 5 — Move semantics

## 5.1 El concepto

Copiar un `vector<uint8_t>` de una imagen 4K son 8 MB de `memcpy`. Pero si el original va a morir de todas formas, es un desperdicio: basta con **robarle el puntero interno** y dejarlo vacío. Eso es un *move*: `O(1)` en lugar de `O(n)`.

- **lvalue**: tiene nombre y dirección, persiste (`v`, `obj.campo`).
- **rvalue**: temporal, está a punto de morir (`v + w`, `Image(640,480)`, el resultado de una función).
- `T&&` es una **rvalue reference**: "me vinculo a algo que puedes canibalizar".
- `std::move` **no mueve nada**: es un `static_cast<T&&>`. Solo dice "trátame como rvalue, tienes permiso para robarme".

```cpp
vector<int> a{1,2,3};
vector<int> b = a;              // COPIA: reserva y copia 3 ints
vector<int> c = move(a);        // MOVE: roba el puntero. a queda vacío pero VÁLIDO
cout << a.size();               // 0 — legal leerlo, pero no asumas su contenido
```

Tras un move, el objeto queda en un estado **válido pero no especificado**: solo puedes destruirlo o reasignarlo.

## 5.2 Rule of 0/3/5

**Rule of 0 — la que quieres.** Si tu clase solo tiene miembros que se gestionan solos (`vector`, `string`, `unique_ptr`), **no escribas ningún destructor ni constructor de copia/move**. Los generados por el compilador son correctos.

**Rule of 3 (C++98).** Si necesitas uno de estos tres, necesitas los tres: destructor, copy constructor, copy assignment.

**Rule of 5 (C++11).** Añade move constructor y move assignment.

**La trampa:** declarar un destructor **suprime la generación de los move operations**. Tu clase seguirá compilando pero copiará donde debería mover, en silencio. Por eso Rule of 0 es la meta y solo bajas a Rule of 5 si gestionas un recurso crudo.

```cpp
class Buffer {
    uint8_t* data_;
    size_t   size_;
public:
    explicit Buffer(size_t n) : data_(new uint8_t[n]), size_(n) {}
    ~Buffer() { delete[] data_; }

    Buffer(const Buffer& o) : data_(new uint8_t[o.size_]), size_(o.size_) {   // copy
        copy(o.data_, o.data_ + o.size_, data_);
    }
    Buffer& operator=(const Buffer& o) {
        if (this == &o) return *this;                    // ¡self-assignment!
        uint8_t* tmp = new uint8_t[o.size_];             // asigna ANTES de liberar
        copy(o.data_, o.data_ + o.size_, tmp);
        delete[] data_;
        data_ = tmp; size_ = o.size_;
        return *this;
    }

    Buffer(Buffer&& o) noexcept                          // move: roba
        : data_(o.data_), size_(o.size_) {
        o.data_ = nullptr; o.size_ = 0;                  // deja el origen destruible
    }
    Buffer& operator=(Buffer&& o) noexcept {
        if (this == &o) return *this;
        delete[] data_;
        data_ = o.data_; size_ = o.size_;
        o.data_ = nullptr; o.size_ = 0;
        return *this;
    }
};
```

**Por qué `noexcept` en los moves — la respuesta de senior:** `vector` solo usa el move constructor al reasignar si está marcado `noexcept`. Si puede lanzar, `vector` no tiene forma de dejar el estado consistente a medio camino, así que **copia por seguridad**. Un move constructor sin `noexcept` anula silenciosamente la optimización que acabas de escribir.

## 5.3 Detalles que suman

```cpp
// Devolver por valor NO es lento: hay copy elision / RVO. Nunca devuelvas por move.
Image makeImage() {
    Image img(640, 480);
    return img;              // NRVO. Escribir `return move(img);` lo EMPEORA (inhibe RVO)
}

// Pasar por valor y mover: idioma "sink parameter"
class Widget {
    string name_;
public:
    explicit Widget(string name) : name_(move(name)) {}   // funciona bien con lvalue y rvalue
};

// Forwarding reference (NO es una rvalue reference: T&& con T deducido)
template <typename T>
void wrapper(T&& x) { inner(forward<T>(x)); }   // conserva value category
```

---

# PARTE 6 — Sintaxis moderna esencial

## 6.1 `auto`, range-for, structured bindings

```cpp
auto x = 5;                       // int
auto& r = v[0];                   // referencia — sin & obtienes una COPIA
const auto& cr = v[0];            // lectura sin copia ← tu default en bucles

for (int x : v)          { }      // copia cada elemento
for (auto& x : v)        { x*=2; }// modifica in-place
for (const auto& x : v)  { }      // lectura sin copia ← el que usas casi siempre

// Structured bindings (C++17): desempaqueta pair, tuple, struct, array
map<string,int> m;
for (const auto& [name, count] : m) { }
auto [q, rem] = div(17, 5);

pair<int,int> p{1,2};
auto [a, b] = p;
```

Bug clásico: `for (auto& [k,v] : myMap)` — `k` es `const` porque las claves de un map son inmutables, `v` sí es modificable.

## 6.2 `const` correctness

```cpp
const int  x = 5;
const int* p;        // puntero a const int  → no puedes cambiar el valor al que apunta el puntero *p, el puntero puede cambiar
                     // es lo mismo que int const *p;
int* const q = &y;   // puntero constante    → no puedes cambiar el puntero q, o sea no los puedes apuntar a otra cosa
// Léelo de derecha a izquierda

class Image {
    int w_, h_;
public:
    int width() const { return w_; }            // no modifica el objeto → callable en const Image
    uint8_t& at(int y, int x);                  // versión mutable
    const uint8_t& at(int y, int x) const;      // versión const (overload por const-ness)
};

void process(const Image& img);   // "no la voy a tocar" ← firma por defecto
```

Pasar objetos grandes por `const&` evita la copia y documenta la intención. Marca `const` **todos** los métodos que no mutan: es gratis y en la entrevista es una señal directa de higiene.

## 6.3 Referencias vs punteros

| | Referencia `T&` | Puntero `T*` |
|---|---|---|
| ¿Puede ser nula? | No | Sí |
| ¿Reasignable? | No | Sí |
| Sintaxis | `obj.x` | `p->x` |
| Uso | El caso normal | Puede faltar / aritmética / arrays |

Regla: usa referencia salvo que necesites *nulo* u opcionalidad; entonces `T*` o mejor `optional<T>`.

## 6.4 `constexpr`

```cpp
constexpr int KERNEL = 3;
constexpr int area(int w, int h) { return w * h; }
constexpr int A = area(640, 480);      // calculado EN COMPILACIÓN
static_assert(A == 307200);

int arr[area(3,3)];                    // válido: es una constante de compilación
```

`const` = "no lo modifico". `constexpr` = "se puede evaluar en tiempo de compilación". Útil para tamaños de kernel, tablas de lookup precomputadas (gamma, LUTs de color) y para mover coste del runtime al build.

## 6.5 Templates básicos

```cpp
template <typename T>
T clampValue(T v, T lo, T hi) { return v < lo ? lo : (v > hi ? hi : v); }

template <typename T>
class Grid {
    vector<T> data_; int w_, h_;
public:
    Grid(int w, int h) : data_(w*h), w_(w), h_(h) {}
    T&       operator()(int y, int x)       { return data_[y*w_ + x]; }
    const T& operator()(int y, int x) const { return data_[y*w_ + x]; }
};

Grid<uint8_t> gray(640, 480);
Grid<float>   depth(640, 480);
```

Los templates son *compile-time polymorphism*: cero coste en runtime, todo se resuelve al instanciar. La contrapartida son binarios grandes y errores de compilación ilegibles.

## 6.6 `optional`, `variant`, `string_view`

```cpp
#include <optional>
optional<Box> detect(const Image& img) {
    if (nada) return nullopt;
    return Box{...};
}
if (auto r = detect(img)) {          // conversión a bool
    use(*r);                          // o r.value()  /  r->score
}
int score = r.value_or(0);
```

`optional` sustituye a devolver `-1`, `nullptr` o un flag por referencia. Expresa "puede que no haya resultado" **en el tipo**, así el compilador te obliga a comprobarlo.

```cpp
#include <variant>
variant<int, string> v = 42;
v = "hola";
if (holds_alternative<string>(v)) cout << get<string>(v);
visit([](auto&& x){ cout << x; }, v);      // despacha al tipo activo
```

---

# PARTE 7 — Concurrencia mínima

Suficiente para explicarlo, aunque no lo teclees.

```cpp
#include <thread>
#include <mutex>
#include <atomic>

void worker(int id) { cout << "hilo " << id << '\n'; }

thread t(worker, 1);
t.join();               // espera. O t.detach(). Si no haces ninguno → std::terminate

// Paralelizar por bandas de imagen — el patrón real en CV
vector<thread> threads;
const int N = thread::hardware_concurrency();
for (int i = 0; i < N; ++i)
    threads.emplace_back([&, i] {
        int y0 = i * H / N, y1 = (i+1) * H / N;
        processRows(img, y0, y1);          // bandas disjuntas → sin locks
    });
for (auto& t : threads) t.join();
```

```cpp
mutex mtx;
{
    lock_guard<mutex> lock(mtx);      // RAII: bloquea aquí, desbloquea al salir del scope
    shared_data.push_back(x);
}                                     // nunca escribas mtx.lock()/unlock() a mano

unique_lock<mutex> ul(mtx);           // como lock_guard pero se puede soltar/reservar
scoped_lock sl(m1, m2);               // C++17: varios mutex sin deadlock

atomic<int> counter{0};
counter++;                            // atómico, sin mutex, para tipos simples
counter.fetch_add(1, memory_order_relaxed);
```

**Lo que dices:** *"Un `data race` es dos hilos accediendo al mismo dato sin sincronización con al menos uno escribiendo: es UB, no un valor incorrecto. Se resuelve con mutex, con atómicos si el dato es simple, o eliminándolo — que es lo mejor: en procesado de imagen particiono por bandas de filas disjuntas y no necesito sincronización en absoluto, solo un join al final. Los locks siempre con `lock_guard`, que es RAII, para que una excepción no deje el mutex tomado."*

---

# PARTE 8 — Ejercicio: la clase `Image`

Este es el warm-up exacto que menciona el plan. Escríbelo hasta que salga de memoria.

```cpp
#include <vector>
#include <cstdint>
#include <stdexcept>
#include <algorithm>
using namespace std;

class Image {
    int w_ = 0, h_ = 0, c_ = 1;
    vector<uint8_t> data_;              // buffer contiguo, row-major → RAII gratis

public:
    Image() = default;
    Image(int w, int h, int channels = 1)
        : w_(w), h_(h), c_(channels), data_(static_cast<size_t>(w) * h * channels, 0) {
        if (w <= 0 || h <= 0 || channels <= 0) throw invalid_argument("dims inválidas");
    }

    // Rule of 0: vector gestiona todo → copy/move/destructor generados son correctos.

    int width()    const noexcept { return w_; }
    int height()   const noexcept { return h_; }
    int channels() const noexcept { return c_; }
    bool empty()   const noexcept { return data_.empty(); }

    // Acceso rápido, sin comprobación (el bucle caliente)
    uint8_t&       operator()(int y, int x, int ch = 0)       { return data_[idx(y,x,ch)]; }
    const uint8_t& operator()(int y, int x, int ch = 0) const { return data_[idx(y,x,ch)]; }

    // Acceso seguro
    uint8_t& at(int y, int x, int ch = 0) {
        if (y < 0 || y >= h_ || x < 0 || x >= w_ || ch < 0 || ch >= c_)
            throw out_of_range("píxel fuera de rango");
        return data_[idx(y,x,ch)];
    }

    uint8_t*       ptr(int y)       { return data_.data() + static_cast<size_t>(y)*w_*c_; }
    const uint8_t* ptr(int y) const { return data_.data() + static_cast<size_t>(y)*w_*c_; }

private:
    size_t idx(int y, int x, int ch) const noexcept {
        return (static_cast<size_t>(y) * w_ + x) * c_ + ch;
    }
};
```

Box blur 3×3 usando la clase — nota la acumulación en `int`:

```cpp
Image boxBlur3x3(const Image& src) {
    const int H = src.height(), W = src.width();
    Image dst(W, H, 1);
    for (int y = 0; y < H; ++y) {
        for (int x = 0; x < W; ++x) {
            int sum = 0, n = 0;                 // int, NO uint8_t → 9*255 desborda
            for (int dy = -1; dy <= 1; ++dy) {
                for (int dx = -1; dx <= 1; ++dx) {
                    int ny = y + dy, nx = x + dx;
                    if (ny < 0 || ny >= H || nx < 0 || nx >= W) continue;   // borde: ignora
                    sum += src(ny, nx);
                    ++n;
                }
            }
            dst(y, x) = static_cast<uint8_t>((sum + n/2) / n);   // +n/2 → redondeo
        }
    }
    return dst;                                  // NRVO, sin copia
}
```

Los puntos que **verbalizas** mientras lo escribes:

1. **Buffer contiguo `vector`, no `vector<vector>`** — una sola asignación, memoria contigua, cache-friendly. Un `vector<vector<uint8_t>>` son H asignaciones dispersas por el heap y un puntero extra por acceso.
2. **Row-major, índice `(y*W + x)*C + ch`** — el bucle exterior sobre `y` y el interior sobre `x`, para recorrer memoria secuencialmente. Invertirlos hace el mismo trabajo 5–10× más lento por cache misses.
3. **Rule of 0** — no escribo destructor ni copy/move; `vector` ya lo hace bien y el compilador genera los cinco correctamente.
4. **Overflow de `uint8_t`** — acumulo en `int`. Sumar 9 píxeles de 255 da 2295, que no cabe en un byte.
5. **Política de bordes** — la declaro explícitamente: ignorar vecinos fuera (equivale a normalizar por el número real de muestras). Alternativas: replicar el borde, reflejar, o recortar la salida.
6. **Dos overloads de acceso** — `operator()` sin comprobación para el bucle caliente, `at()` con comprobación para la API pública. Es exactamente lo que hacen `vector` y `cv::Mat`.

---

# PARTE 9 — Errores clásicos (lista de repaso)

| Error | Por qué duele |
|---|---|
| `new`/`delete` crudos | Fuga garantizada en cuanto haya un `return` o un `throw`. Usa `vector`/`make_unique` |
| `vector<vector<T>>` para imágenes | H asignaciones, memoria dispersa, indirección extra |
| Acumular píxeles en `uint8_t` | Overflow silencioso. Acumula en `int`/`float`, y `clamp` al escribir |
| `for (auto x : bigVector)` | Copia cada elemento. Usa `const auto&` |
| Iterador tras `push_back` | Invalidado si reasignó → UB |
| `m[key]` para consultar | Inserta silenciosamente. Usa `find`/`at`/`count` |
| Move constructor sin `noexcept` | `vector` copia en lugar de mover al crecer |
| Destructor declarado sin Rule of 5 | Suprime los moves → copias silenciosas |
| Capturar por `[&]` en lambda que sobrevive | Dangling reference |
| `return move(x)` | Inhibe RVO: lo empeora |
| Bucles `x` fuera, `y` dentro | Recorrido no secuencial, cache misses |
| `q.pop()` esperando el valor | Devuelve `void`: lee `front()` antes |
| `int` para índices de imágenes 4K+ | `y*W+x` puede desbordar; usa `size_t` en el cálculo |
| `unique` sin `sort` previo | Solo colapsa duplicados adyacentes |

---

# PARTE 10 — Preguntas rápidas de autoevaluación

1. ¿Qué es RAII y qué clase de bugs elimina?
2. Diferencia entre `unique_ptr` y `shared_ptr`. ¿Cuál por defecto y por qué?
3. ¿Qué hace realmente `std::move`?
4. ¿En qué estado queda un objeto tras moverlo?
5. ¿Por qué el move constructor debe ser `noexcept`?
6. Rule of 0/3/5 — ¿qué pasa si solo declaras el destructor?
7. `vector` vs `list`: misma complejidad de inserción, ¿por qué gana `vector` en la práctica?
8. ¿Qué invalida los iteradores de un `vector`?
9. `map` vs `unordered_map`: complejidad y cuándo cada uno.
10. ¿Por qué `m[k]` es peligroso para consultar?
11. Captura por valor vs por referencia en una lambda: ¿cuándo es un bug cada una?
12. ¿Por qué `accumulate(v.begin(), v.end(), 0)` puede dar mal resultado?
13. `const int*` vs `int* const`.
14. ¿Qué es una rvalue reference y en qué se diferencia de una forwarding reference?
15. En BFS, ¿marcas visitado al encolar o al desencolar? ¿Por qué?

Si dudas en alguna, esa es la sección a la que vuelves.
