# Curso de refuerzo — C++ moderno (C++11/14/17/20)

Basado en tus tests de C++ (revision_test_01, 02, 06 y 09). Puntuaciones: 25%, 53%, 40% (parte C++) y 43%. El patrón de fallos es claro: **move semantics** aparece roto en los cuatro tests, y hay huecos recurrentes en smart pointers, invalidación de iteradores, concurrencia/atomics y forwarding references. Este curso va de menos a más, porque varios temas se apoyan unos en otros (RAII → move semantics → smart pointers → concurrencia).

Cada módulo tiene: explicación desde cero, desarrollo con matices que te hicieron fallar, ejemplos comentados y un ejercicio. Las soluciones a los ejercicios están todas al final, para que intentes resolverlos antes de mirar.

## Índice

1. RAII y la regla de tres/cinco/cero
2. Move semantics a fondo (tu punto más débil)
3. Smart pointers: unique_ptr, shared_ptr, weak_ptr
4. Lambdas: capturas y ciclo de vida
5. Templates vs. funciones virtuales
6. Invalidación de iteradores en STL
7. Contenedores STL: garantías y complejidad
8. Algoritmos STL: erase-remove, accumulate, complejidad
9. Concurrencia básica: data races, mutex, atomics
10. Atomics avanzado: memory_order y happens-before
11. Perfect forwarding y referencias universales
12. std::optional
13. Localidad de caché y contigüidad de memoria
14. Bonus: C++ y Python (pybind11)

---

## 1. RAII y la regla de tres/cinco/cero

### ¿Qué es?

RAII (*Resource Acquisition Is Initialization*) es la idea central de C++: la vida de un recurso (memoria, un fichero, un mutex, un socket) se ata a la vida de un objeto. El recurso se adquiere en el constructor y se libera en el destructor. Como C++ garantiza que los destructores de los objetos en la pila se ejecutan siempre al salir de su ámbito —incluso si hay una excepción de por medio (stack unwinding)—, esto te da liberación determinista de recursos sin necesidad de `try/finally`.

```cpp
class FileHandle {
public:
    FileHandle(const char* path) : fp_(std::fopen(path, "r")) {
        if (!fp_) throw std::runtime_error("no se pudo abrir");
    }
    ~FileHandle() { if (fp_) std::fclose(fp_); }
private:
    FILE* fp_;
};
```

Si el constructor lanza una excepción, el objeto se considera "no construido" y su destructor **no** se ejecuta. Eso es correcto aquí porque, si `fopen` falla, `fp_` es `nullptr` y no hay nada que liberar. Pero si el constructor hubiera adquirido dos recursos y el segundo fallara, tendrías que asegurarte de que el primero se libera igualmente (normalmente delegando cada recurso en su propio objeto RAII).

### Profundizando: la regla de tres/cinco/cero

Cuando una clase gestiona un recurso manualmente con un puntero crudo, C++ te obliga a pensar en **cinco miembros especiales**:

- Destructor
- Constructor de copia
- Operador de asignación por copia
- Constructor de movimiento
- Operador de asignación por movimiento

Regla clave que se te escapó en el test: **si declaras cualquiera de destructor, constructor de copia o asignación de copia, el compilador dejará de generarte automáticamente el constructor y la asignación de movimiento.** Consecuencia práctica: una clase con destructor propio y sin move constructor declarado explícitamente hará *copias* donde tú esperabas *movimientos* (por ejemplo, dentro de un `std::vector`), sin ningún error de compilación, solo pérdida silenciosa de rendimiento.

```cpp
class Buffer {
public:
    Buffer(size_t n) : data_(new int[n]), size_(n) {}
    ~Buffer() { delete[] data_; }   // declarar el destructor...
private:
    int* data_;
    size_t size_;
};
// ...suprime la generación implícita de move ctor / move assignment.
// El compilador SÍ sigue generando copy ctor / copy assignment (deprecated
// pero presente), que copian el puntero superficialmente -> doble delete.
```

La solución idiomática moderna es la **regla de cero**: no gestiones recursos crudos tú mismo. Delega en `std::unique_ptr`, `std::vector`, `std::string`, etc., que ya implementan la regla de cinco correctamente. Si de verdad necesitas gestionar un recurso a mano, declara los cinco miembros explícitamente.

### Ejercicio 1

Tienes esta clase:

```cpp
class Matriz {
public:
    Matriz(int filas, int cols)
        : filas_(filas), cols_(cols), datos_(new double[filas * cols]) {}
    ~Matriz() { delete[] datos_; }
private:
    int filas_, cols_;
    double* datos_;
};

std::vector<Matriz> matrices;
matrices.push_back(Matriz(100, 100));
matrices.push_back(Matriz(200, 200)); // fuerza una reallocation
```

a) ¿Qué ocurre exactamente cuando `matrices` reubica su almacenamiento interno en el segundo `push_back`? ¿Copia o mueve los objetos `Matriz`?
b) Reescribe `Matriz` aplicando la regla de cero (sin destructor propio).

---

## 2. Move semantics a fondo (tu punto más débil)

Esto ha aparecido en los cuatro tests de C++ y sigue fallando incluso en la repetición (test 09), así que vamos despacio.

### ¿Qué es un rvalue y qué hace std::move?

En C++, todo valor tiene una **categoría de valor**. Simplificando a lo esencial:

- **lvalue**: tiene nombre, ocupa una dirección de memoria identificable, puedes tomarle la dirección (`&x`). Ejemplo: una variable local `v1`.
- **rvalue** (más concretamente *xvalue* o *prvalue*): un valor temporal, sin nombre persistente, del que "nadie más" va a necesitar el contenido después de esta expresión. Ejemplo: el resultado de `Buffer(100)`, o el resultado de `std::move(v1)`.

`std::move` **no mueve nada**. Es literalmente un `static_cast<T&&>(x)`: solo cambia la categoría de valor de `x` de lvalue a rvalue, como una etiqueta que dice "puedes canibalizar este objeto, no lo necesito más tal cual". El movimiento real ocurre cuando, gracias a ese cast, la resolución de sobrecarga elige el **constructor o el operador de asignación de movimiento** (los que tienen parámetro `T&&`) en vez de la versión de copia (`const T&`).

```cpp
std::vector<int> v1 = {1, 2, 3};
std::vector<int> v2 = std::move(v1); // v1 pasa a ser un rvalue -> se elige
                                       // el move constructor de vector
```

Este es el error #1 que cometiste: pensar que `std::move` "hace" el movimiento. Si el tipo destino **no tiene** constructor/asignación de movimiento aplicable, `std::move(x)` simplemente hace que se copie igual, sin ningún error ni aviso.

### Trampa 1: el estado de v1 tras moverlo

El estándar garantiza que, tras ser movido-desde, un objeto de la biblioteca estándar (como `std::vector`) queda en un **estado válido pero no especificado**. Válido significa que puedes destruirlo o reasignarle un valor nuevo con seguridad; no especificado significa que el estándar **no** te garantiza que quede vacío, aunque en la práctica libstdc++/libc++ suelen dejarlo vacío. No lo des por hecho salvo que la documentación del tipo concreto lo prometa explícitamente.

### Trampa 2: un parámetro con nombre siempre es un lvalue, aunque su tipo sea `T&&`

```cpp
class Buffer {
public:
    explicit Buffer(std::vector<int> data) : data_(std::move(data)) {}
    //                                                   ^^^^^^^^^^^^
    // "data" es un PARÁMETRO con nombre -> dentro del cuerpo de la función
    // es un lvalue, aunque haya sido inicializado desde un rvalue en la
    // llamada. Por eso hace falta std::move(data) aquí explícitamente:
    // sin él, se COPIARÍA el vector en vez de moverlo.
    std::vector<int> data_;
};
```

Regla general que conviene memorizar: **cualquier cosa con nombre es un lvalue dentro de su propio ámbito**, sin importar si su tipo declarado es una referencia rvalue.

### Trampa 3: `noexcept` decide si `std::vector` mueve o copia

Cuando `std::vector` necesita reubicar sus elementos (por ejemplo, al crecer más allá de su capacidad), tiene que decidir si mover o copiar cada elemento existente al nuevo bloque de memoria. Para no dejar el vector en un estado corrupto si algo falla a mitad del proceso (la *garantía fuerte de excepciones*), `std::vector` usa internamente `std::move_if_noexcept`:

- Si el constructor de movimiento del tipo está marcado `noexcept`, lo usa (rápido, y si falla algo raro no hay forma de que ocurra a mitad, porque el move no lanza).
- Si **no** está marcado `noexcept` (aunque exista y funcione perfectamente), y hay constructor de copia disponible, `std::vector` prefiere **copiar**, porque una copia se puede abortar a medias sin dejar el vector corrupto, y un move a medias sí podría hacerlo.

```cpp
class Buffer {
public:
    Buffer(Buffer&& other) { /* mueve recursos */ }        // sin noexcept
    Buffer(const Buffer& other) { /* copia recursos */ }
};
std::vector<Buffer> v;
v.push_back(Buffer());
v.push_back(Buffer()); // reallocation -> como el move ctor NO es noexcept,
                        // vector usará el COPY ctor, no el move ctor.
```

La lección práctica: **marca siempre `noexcept` tus constructores y asignaciones de movimiento** si realmente no pueden lanzar (lo normal, ya que solo intercambian punteros). Si no lo haces, pierdes silenciosamente la optimización que perseguías con move semantics.

### Trampa 4: `return` de una variable local y copia elidida (RVO/NRVO)

```cpp
std::vector<int> hacer() {
    std::vector<int> v2 = {1,2,3};
    return v2;                 // NO escribas "return std::move(v2);"
}
```

Para variables locales automáticas, el compilador aplica NRVO (*Named Return Value Optimization*) o, si no puede elidir la copia, selecciona automáticamente el constructor de movimiento sobre `v2` porque es una variable local a punto de destruirse. Añadir `std::move` explícito en un `return` no ayuda y en algunos casos **impide** que el compilador aplique la elisión de copia (porque ya no ve un objeto "con nombre simple", sino una expresión `std::move(v2)`), obligándolo a caer al move constructor cuando podría haber elidido la construcción por completo.

Ojo con un matiz de C++17: la **copia elidida garantizada** (*guaranteed copy elision*) para `return Tipo(args);` (un *prvalue* construido directamente en el return) elimina de verdad toda copia/movimiento del objeto devuelto. Pero eso **no** elimina los movimientos que ocurren *dentro* del constructor de ese objeto:

```cpp
Buffer make() {
    std::vector<int> v = {1, 2, 3};
    return Buffer(std::move(v));
    // La construcción de "Buffer(...)" como prvalue de retorno se elide
    // (no hay copia/move del Buffer completo). Pero DENTRO del constructor
    // de Buffer, std::move(v) sigue provocando un movimiento real del
    // vector interno hacia data_. Son dos cosas distintas.
}
```

### Ejemplo resuelto completo

```cpp
struct Widget {
    std::string nombre;
    Widget(std::string n) : nombre(std::move(n)) {}   // mueve el parámetro
    Widget(Widget&& w) noexcept = default;              // noexcept explícito
    Widget(const Widget&) = default;
};

std::vector<Widget> fabrica() {
    std::vector<Widget> ws;
    ws.emplace_back("a");   // construye in-place, sin copia extra
    ws.push_back(Widget("b")); // Widget("b") es un prvalue -> se mueve, no copia
    return ws;               // NRVO o move automático, sin std::move explícito
}
```

### Ejercicio 2

```cpp
void procesar(std::string s) {          // por valor
    std::cout << s << "\n";
}

std::string origen = "hola";
procesar(origen);              // (A)
procesar(std::move(origen));   // (B)
procesar(std::string("hola")); // (C)
```

a) ¿En cuál de las tres llamadas (A, B, C) se produce una copia de la cadena y en cuáles un movimiento (o construcción directa sin copia)? Justifica cada una.
b) Después de (B), ¿qué puedes asumir sobre el contenido de `origen`? ¿Qué es seguro seguir haciendo con `origen` y qué no?

---

## 3. Smart pointers: unique_ptr, shared_ptr, weak_ptr

### ¿Qué son?

Son wrappers RAII sobre punteros crudos que automatizan la liberación de memoria dinámica:

- `std::unique_ptr<T>`: propiedad **exclusiva**. Solo un `unique_ptr` puede poseer el recurso en cada momento.
- `std::shared_ptr<T>`: propiedad **compartida** mediante conteo de referencias (`use_count()`). El recurso se libera cuando el último `shared_ptr` que lo posee se destruye.
- `std::weak_ptr<T>`: **observa** un objeto gestionado por `shared_ptr` sin poseerlo ni incrementar el contador de referencias.

### Por qué unique_ptr no se puede copiar

```cpp
std::unique_ptr<int> a = std::make_unique<int>(42);
std::unique_ptr<int> b = a;              // ERROR de compilación
std::unique_ptr<int> b = std::move(a);   // OK: transfiere la propiedad
```

`unique_ptr` tiene su constructor y operador de copia **eliminados** (`= delete`) a propósito: copiar destruiría la invariante de propiedad exclusiva (¿quién liberaría el recurso, `a` o `b`?). Solo permite **mover**, lo que transfiere la propiedad: tras `std::move(a)`, `a` queda a `nullptr` y `b` es el nuevo dueño.

### El problema de los ciclos con shared_ptr, y cómo weak_ptr lo resuelve

```cpp
struct Node {
    std::shared_ptr<Node> next;
    std::weak_ptr<Node> prev;   // <- clave: weak_ptr, no shared_ptr
};

auto a = std::make_shared<Node>();
auto b = std::make_shared<Node>();
a->next = b;
b->prev = a;
```

Si `prev` fuera también `shared_ptr<Node>`, tendrías un ciclo: `a` mantiene vivo a `b` (vía `next`) y `b` mantiene vivo a `a` (vía `prev`). Aunque las variables locales `a` y `b` salgan de ámbito, cada objeto seguiría teniendo `use_count() >= 1` gracias al otro, así que **ninguno de los dos se destruiría nunca**: una fuga de memoria clásica en estructuras enlazadas o padre-hijo.

Al declarar `prev` como `weak_ptr`, esa referencia **no cuenta** para el `use_count()`. El ciclo fuerte se rompe: cuando las variables externas `a` y `b` desaparecen, el conteo de cada uno llega a cero y se destruyen con normalidad. Para usar el objeto observado por un `weak_ptr` de forma segura, se llama a `.lock()`, que devuelve un `shared_ptr` válido si el objeto sigue vivo, o un `shared_ptr` vacío (nunca acceso a memoria liberada) si ya fue destruido.

### make_shared vs. new + shared_ptr

`std::make_shared<T>(args...)` hace **una sola** asignación de memoria que aloja juntos el objeto `T` y el bloque de control (contador de referencias fuertes/débiles). `std::shared_ptr<T>(new T(args...))` hace **dos** asignaciones separadas. Además de ser más rápido, `make_shared` es más seguro frente a excepciones en construcciones complejas. Úsalo siempre que no necesites un deleter personalizado.

### Ejercicio 3

```cpp
struct Sensor {
    std::string id;
    ~Sensor() { std::cout << "destruyendo " << id << "\n"; }
};

std::weak_ptr<Sensor> observador;
{
    auto s = std::make_shared<Sensor>(Sensor{"cam0"});
    observador = s;
    std::cout << "dentro: " << (observador.expired() ? "expirado" : "vivo") << "\n";
}
std::cout << "fuera: " << (observador.expired() ? "expirado" : "vivo") << "\n";

if (auto sp = observador.lock()) {
    std::cout << "id: " << sp->id << "\n";
} else {
    std::cout << "ya no existe\n";
}
```

Traza mentalmente la salida completa del programa, línea a línea, y explica por qué `observador.lock()` en la última parte no puede causar un use-after-free.

---

## 4. Lambdas: capturas y ciclo de vida

Has visto esta pregunta en tres tests distintos (01, 02, 09) y la última vez la acertaste — pero merece un repaso firme porque es un error muy fácil de cometer en código real.

### ¿Qué es?

Una lambda `[captura](parámetros) { cuerpo }` es azúcar sintáctico para un objeto función anónimo. Lo importante es qué significa cada tipo de captura:

- `[x]`: **captura por valor**. La lambda guarda una *copia* de `x` en el momento de crearse. Su vida es independiente de la variable original.
- `[&x]`: **captura por referencia**. La lambda guarda un alias/puntero a la variable original `x`. No copia nada.
- `[=]` / `[&]`: capturan todo lo usado por valor / por referencia, respectivamente (evita esto en código de producción; sé explícito).

### El bug clásico: referencia colgante al devolver una lambda

```cpp
std::function<int()> hacer_contador() {
    int contador = 0;
    auto incrementar = [&contador]() {   // captura por REFERENCIA
        return ++contador;
    };
    return incrementar;
}

int main() {
    auto f = hacer_contador();
    std::cout << f() << std::endl;   // comportamiento indefinido
}
```

`contador` es una variable local de `hacer_contador()`. Cuando la función retorna, `contador` se destruye (su almacenamiento en pila deja de ser válido). La lambda, al capturar por referencia, solo guardó un alias hacia esa posición de memoria — no una copia. Al llamar a `f()` desde `main`, accedes a memoria que ya no pertenece a nadie: comportamiento indefinido, no un error de compilación ni un resultado "0" garantizado.

**`std::function` no alarga la vida de nada capturado por referencia.** Solo gestiona el ciclo de vida del propio objeto invocable (la lambda), no el de las variables externas que esa lambda referencia.

La solución es capturar por valor: `[contador]`. Como el `operator()` generado por una lambda es `const` por defecto, si quieres *modificar* tu copia interna necesitas además la palabra clave `mutable`:

```cpp
auto hacer_contador() {
    int contador = 0;
    return [contador]() mutable {   // copia propia, modificable
        return ++contador;
    };
}
```

### Regla práctica

Si una lambda **va a sobrevivir** al ámbito en el que se creó (se devuelve, se guarda en un `std::function` miembro, se pasa a un hilo, se registra como callback), captura por **valor** las variables locales que necesite, o gestiona su vida con algo más robusto (`shared_ptr`, variable `static`, miembro de clase).

### Ejercicio 4

```cpp
std::vector<std::function<void()>> callbacks;

void registrar(int id) {
    callbacks.push_back([&id]() {
        std::cout << "callback " << id << "\n";
    });
}

int main() {
    for (int i = 0; i < 3; ++i) registrar(i);
    for (auto& cb : callbacks) cb();
}
```

a) ¿Qué tiene de problemático este código? (Pista: fíjate en qué es exactamente `id` dentro de `registrar`.)
b) Corrígelo para que imprima `callback 0`, `callback 1`, `callback 2`.

---

## 5. Templates vs. funciones virtuales

### ¿Qué es?

C++ ofrece dos mecanismos de polimorfismo con propósitos y costes muy distintos:

- **Polimorfismo estático (tiempo de compilación)**: templates y sus especializaciones. El compilador decide qué código generar/usar en base al tipo, *antes* de ejecutar el programa. No hay indirección en tiempo de ejecución.
- **Polimorfismo dinámico (tiempo de ejecución)**: funciones `virtual` despachadas a través de una *vtable* (tabla de punteros a función). La decisión de qué implementación ejecutar depende del tipo real del objeto, resuelto en tiempo de ejecución.

```cpp
template <typename T>
void imprimir(const T& valor) { std::cout << "generico: " << valor << "\n"; }

template <>
void imprimir<bool>(const bool& valor) {
    std::cout << "booleano: " << (valor ? "si" : "no") << "\n";
}
// imprimir(true) -> el compilador YA SABE en compilación que hay que usar
// la especialización para bool. Cero coste de indirección.

struct Base { virtual void saludar() const { std::cout << "Base\n"; } };
struct Derivada : Base { void saludar() const override { std::cout << "Derivada\n"; } };

Base* p = new Derivada();
p->saludar(); // "Derivada" -> decidido en RUNTIME vía vtable, porque el
              // tipo estático de p es Base*, pero el tipo dinámico es Derivada
```

### Los dos matices que fallaste

1. **Coste**: la especialización de plantillas **no** genera ninguna tabla de despacho ni indirección; el compilador simplemente emite código directo para el tipo concreto. El coste de indirección (seguir un puntero en la vtable) es exclusivo del despacho virtual.
2. **Extensibilidad**: ambos mecanismos son abiertos a extensión sin tocar el código existente (principio abierto/cerrado). Añadir `imprimir<std::string>` no requiere modificar la plantilla genérica, igual que añadir una nueva clase derivada de `Base` no requiere modificar `Base`. No confundas "polimorfismo estático" con "cerrado a extensión": son ejes distintos.

### Ejercicio 5

Escribe una función `mayor(const T& a, const T& b)` genérica que devuelva el mayor de los dos usando `operator>`, y luego una especialización explícita para `const char*` que compare con `strcmp` en vez de comparar punteros. Explica en una frase por qué, sin la especialización, `mayor("abc", "abd")` daría un resultado incorrecto/no significativo.

---

## 6. Invalidación de iteradores en STL

### ¿Qué es?

Un iterador es, conceptualmente, un puntero generalizado a un elemento dentro de un contenedor. Cuando el contenedor reorganiza su memoria interna (inserta, borra, reubica), los iteradores que apuntaban a ciertas posiciones pueden dejar de ser válidos. Las reglas de invalidación **dependen del contenedor** y es la fuente de UB en producción más subestimada de la STL.

### El caso que fallaste: std::vector

```cpp
std::vector<int> v = {1, 2, 3, 4, 5};
auto it = v.begin() + 2;   // apunta al valor 3
v.insert(v.begin(), 0);    // inserta al principio
*it = 100;                 // comportamiento indefinido
```

Regla exacta para `std::vector::insert`: se invalidan **todos los iteradores/referencias en el punto de inserción y posteriores**, haya o no reallocation de memoria — porque incluso sin reallocation, `insert` tiene que desplazar físicamente todos los elementos posteriores al punto de inserción para hacer hueco. Como aquí insertamos en `v.begin()` (el principio), *todo* queda invalidado, incluido `it`. Si hay reallocation (porque se supera la capacidad), se invalida absolutamente todo, sin excepción.

Lo que mucha gente cree erróneamente (y es donde fallaste): que basta con que "no haya reallocation" para que los iteradores sigan siendo válidos. Falso para inserciones/borrados en medio del vector: el desplazamiento de elementos por sí solo ya invalida.

### Comparativa rápida (memorízala)

| Contenedor | insert/push_back | erase |
|---|---|---|
| `std::vector` | invalida iteradores en el punto y posteriores (todo si hay reallocation) | invalida iteradores en el punto y posteriores |
| `std::deque` | invalida casi todo (salvo excepciones en los extremos) | invalida casi todo |
| `std::list` / `std::map` / `std::set` | **no** invalida iteradores existentes (basados en nodos) | solo invalida el iterador al elemento borrado |

Los contenedores basados en nodos (lista enlazada, árbol) no mueven los elementos existentes en memoria al insertar/borrar otro, así que sus iteradores son mucho más estables.

### Ejercicio 6

```cpp
std::vector<int> v = {10, 20, 30, 40, 50};
auto it_ultimo = v.end() - 1;      // apunta a 50
v.push_back(60);
```

a) ¿Es seguro usar `it_ultimo` después del `push_back`? Razónalo considerando ambos casos: que haya reallocation o que no la haya.
b) Reescribe el fragmento para obtener de forma segura una referencia al último elemento tras el `push_back`.

---

## 7. Contenedores STL: garantías y complejidad

### Lo que hay que saber de memoria, sin dudar

- **`std::vector`**: almacenamiento **contiguo** garantizado por el estándar. `&v[0]` es válido como `T*` compatible con APIs en C. Acceso aleatorio O(1). Inserción/borrado al final amortizado O(1); en medio, O(n).
- **`std::list`**: lista doblemente enlazada. **No** tiene acceso aleatorio ni `operator[]`; acceder al elemento *i* cuesta O(n). Inserción/borrado en cualquier punto conocido, O(1).
- **`std::map`**: árbol balanceado (típicamente rojo-negro), mantiene las claves **ordenadas** (por defecto con `std::less`). Búsqueda, inserción y borrado en O(log n).
- **`std::unordered_map`**: tabla hash. **No garantiza ningún orden** de iteración (puede cambiar tras un rehash). Búsqueda amortizada O(1), peor caso O(n).
- **`std::queue`**: no es un contenedor en sí, es un **adaptador** que por defecto envuelve un `std::deque` y expone solo `push`/`pop`/`front`/`back` con semántica FIFO.

### El error típico

Confundir `std::map` con `std::unordered_map` en cuanto a orden de iteración, o asumir que `std::list` tiene acceso aleatorio "porque es secuencial como `vector`". Ninguno de los dos es cierto: la palabra "secuencial" en el estándar se refiere al orden lógico de los elementos, no a cómo se accede a ellos en memoria.

### Ejercicio 7

Para cada escenario, elige el contenedor STL más adecuado y justifica en una frase:

a) Necesitas insertar y borrar frecuentemente elementos por el medio de una colección de tamaño mediano, y casi nunca accedes por índice.
b) Necesitas buscar si un identificador (string) existe en una colección de 1 millón de elementos, lo más rápido posible, sin que te importe el orden.
c) Necesitas recorrer los empleados de una empresa ordenados alfabéticamente por apellido, insertando nuevos empleados de vez en cuando.
d) Implementas una cola de tareas pendientes en orden de llegada (FIFO).

---

## 8. Algoritmos STL: erase-remove, accumulate, complejidad

### El idiom erase-remove

```cpp
std::vector<int> v = {1,2,3,4,5,6,7,8,9,10};
auto it = std::remove(v.begin(), v.end(), 5);
v.erase(it, v.end());
```

`std::remove` **no elimina nada del contenedor** (ni siquiera conoce qué contenedor es: solo opera sobre un rango `[first, last)` vía iteradores). Lo que hace es reordenar el rango, moviendo hacia el principio los elementos que *no* coinciden con el valor buscado, y devuelve un iterador al nuevo "final lógico". Los elementos después de ese iterador quedan en un estado indeterminado (sobras del reordenamiento). Por eso hace falta el segundo paso, `v.erase(it, v.end())`, que sí reduce físicamente el tamaño del vector.

Nota de complejidad: aplicar este idiom sobre `std::list` es un desperdicio: `list::erase` de un elemento es O(1) y el propio `std::list` ofrece `list::remove()`, más eficiente que el idiom genérico porque trabaja directamente sobre los nodos.

### El overflow silencioso de accumulate

```cpp
std::vector<int> v = /* muchos millones de elementos */;
auto suma = std::accumulate(v.begin(), v.end(), 0);  // 0 es int
```

`std::accumulate` deduce el tipo del **acumulador** a partir del **valor inicial**, no de los elementos que suma. Si pasas `0` (un `int`), el acumulador es `int`, sin importar que sumando muchos elementos el resultado real supere el rango de `int`: hay overflow (UB en enteros con signo). La solución es pasar un valor inicial de un tipo con más rango: `std::accumulate(v.begin(), v.end(), 0LL)`.

### Complejidades que hay que tener memorizadas

- `std::find`: O(n), búsqueda lineal, no asume orden.
- `std::binary_search`: O(log n), pero **exige** que el rango esté ordenado.
- `std::sort`: O(n log n) en el caso medio (no garantiza estabilidad).
- `std::stable_sort`: O(n log n) si hay memoria auxiliar disponible; O(n log² n) en el peor caso sin ella.

### Ejercicio 8

```cpp
std::vector<uint8_t> bytes = {200, 100, 50};
uint8_t total = std::accumulate(bytes.begin(), bytes.end(), 0);
```

a) ¿Qué tipo tiene el acumulador aquí, y qué valor obtienes en `total`? (pista: no es directamente 350)
b) Corrige la llamada para que el resultado sea correcto incluso si la suma real supera 255, devolviendo el resultado ya truncado a `uint8_t` solo al final si así lo necesitas.

---

## 9. Concurrencia básica: data races, mutex, atomics

### ¿Qué es una data race?

Ocurre cuando dos o más hilos acceden concurrentemente a la misma variable, al menos uno de ellos escribiendo, sin ninguna sincronización que establezca un orden entre esos accesos. Es comportamiento indefinido en C++, no "un resultado raro pero seguro".

```cpp
long contador = 0;
std::mutex m;

void trabajo(int n) {
    for (int i = 0; i < n; ++i) {
        m.lock();
        contador++;
        m.unlock();
    }
}
```

Dos errores conceptuales que cometiste sobre este código:

1. **`contador++` no es atómico** solo por ser un `long`. Es lectura + incremento + escritura, tres pasos separados a nivel de máquina; sin el mutex (o un `std::atomic<long>`), dos hilos pueden pisarse la operación. El mutex aquí es necesario, no redundante.
2. Si `trabajo()` lanzara una excepción entre `lock()` y `unlock()` manuales, el mutex quedaría **bloqueado para siempre** (nadie llama a `unlock()`). La solución es RAII aplicado a locks: `std::lock_guard<std::mutex>`, cuyo destructor llama a `unlock()` automáticamente sea cual sea la ruta de salida (return, excepción, break...).

```cpp
void trabajo(int n) {
    for (int i = 0; i < n; ++i) {
        std::lock_guard<std::mutex> lg(m);  // se libera solo al salir del scope
        contador++;
    }
}
```

Nota: esto **no es solo estilo**. `lock_guard` cambia el comportamiento observable frente a excepciones respecto al `lock()`/`unlock()` manual sin `try/catch`.

### Alternativa sin mutex: std::atomic

```cpp
std::atomic<long> contador{0};
void trabajo(int n) {
    for (int i = 0; i < n; ++i) contador++;   // atómico, sin mutex
}
```

`std::atomic<long>::operator++` ya es seguro por sí solo para esta operación simple. No confundas esto con el "problema ABA": ese problema afecta a algoritmos lock-free basados en *compare-and-swap* sobre estructuras compuestas (como pilas lock-free), no a un incremento atómico simple, que no lo necesita.

### Reducir contención: particionamiento

Otra técnica válida es dar a cada hilo un contador **local** (sin sincronización durante el bucle) y sumar los resultados parciales después de `join()`. Esa suma final se ejecuta **secuencialmente en un solo hilo**, así que no necesita ni mutex ni atomics — el error típico es pensar que hace falta protegerla también.

### Ejercicio 9

Tienes 4 hilos que cada uno debe sumar los cuadrados de un rango distinto de un array grande de `int`, y quieres el total combinado. Escribe una versión que use particionamiento con acumuladores locales (sin mutex ni atomics durante el bucle de cada hilo), y explica por qué la suma final es segura sin sincronización adicional.

---

## 10. Atomics avanzado: memory_order y happens-before

Esto es un nivel más profundo que el módulo anterior, y es donde fallaste en el test 09.

### El problema: atomicidad no es lo mismo que orden/visibilidad

```cpp
int datos = 0;                       // variable NO atómica
std::atomic<bool> listo{false};

void productor() {
    datos = 42;
    listo.store(true, std::memory_order_relaxed);
}

void consumidor() {
    while (!listo.load(std::memory_order_relaxed)) {}
    std::cout << datos << std::endl;  // ¿ve 42, o comportamiento indefinido?
}
```

`std::memory_order_relaxed` garantiza que las operaciones sobre `listo` en sí son atómicas (nadie ve un valor "a medio escribir"), pero **no establece ninguna relación de orden (happens-before) con otras variables**. El consumidor puede observar `listo == true` sin que eso garantice que también observará `datos == 42`: el compilador o la CPU pueden reordenar esas operaciones si nada se lo impide. Como `datos` es una variable no atómica accedida concurrentemente sin happens-before, hay una data race real, aunque el patrón "parezca funcionar" en la práctica.

### La solución: release-acquire

```cpp
void productor() {
    datos = 42;
    listo.store(true, std::memory_order_release);   // "publica" datos
}

void consumidor() {
    while (!listo.load(std::memory_order_acquire)) {} // "sincroniza" con el release
    std::cout << datos << std::endl;  // ahora SÍ garantizado: ve 42
}
```

Un `store` con `memory_order_release` garantiza que **todas las escrituras anteriores a él** (en este caso, `datos = 42`) sean visibles para cualquier hilo que haga un `load` con `memory_order_acquire` sobre la **misma variable atómica** y observe el valor almacenado. Esta pareja release/acquire crea la relación happens-before que faltaba.

### Dos ideas erróneas típicas

1. **`volatile` no sirve para esto en C++.** A diferencia de Java/C#, en C++ `volatile` solo impide ciertas optimizaciones del compilador sobre el acceso a memoria; no garantiza atomicidad ni visibilidad entre hilos, ni establece ningún orden.
2. **`seq_cst` (el valor por defecto) no es "igual" que `relaxed`.** `seq_cst` es estrictamente más fuerte: además de atomicidad, aporta semántica de acquire/release y un orden total consistente observado igual por todos los hilos. `relaxed` no ofrece ninguna garantía de orden entre variables distintas. Si dudas de qué `memory_order` usar, `seq_cst` es la opción segura por defecto (más lenta, pero correcta); optimiza a `relaxed`/`release`/`acquire` solo si perfilas y lo necesitas.

### Ejercicio 10

Explica con tus palabras por qué cambiar *solo* el `store` del productor a `memory_order_release`, dejando el `load` del consumidor en `memory_order_relaxed`, **no** arregla la data race sobre `datos`. ¿Qué falta?

---

## 11. Perfect forwarding y referencias universales

### ¿Qué es una forwarding reference?

```cpp
template <typename T>
void wrapper(T&& arg) {
    inner(std::forward<T>(arg));
}
```

Cuando `T` es un parámetro de plantilla deducido, `T&&` **no** es una rvalue reference fija: es una **referencia universal** (forwarding reference). Su comportamiento depende de qué le pases:

- Si llamas `wrapper(x)` con `x` un lvalue, `T` se deduce como `U&`. Por la regla de **colapso de referencias** (`& + && = &`), el parámetro resultante es `U&`.
- Si llamas `wrapper(Widget{})` con un rvalue, `T` se deduce como `U` (sin referencia), y el parámetro resultante es `U&&`.

Esto es lo contrario de lo que asumiste en el test: `T&&` en este contexto **puede** recibir tanto lvalues como rvalues; no está limitado a temporales.

### std::forward vs. std::move

`std::forward<T>(arg)` reconstruye la categoría de valor **original** con la que se llamó a `wrapper`: si vino un lvalue, reenvía un lvalue; si vino un rvalue, reenvía un rvalue. `std::move(arg)` en cambio **siempre** convierte a rvalue, sin importar el origen. Usar `std::move` aquí en vez de `std::forward` sería un bug: podría mover accidentalmente un objeto que el llamador pasó como lvalue (y que quizás seguía necesitando después).

```cpp
Widget w;
wrapper(w);              // T = Widget&  -> arg es Widget& -> forward reenvía un lvalue
wrapper(Widget{});        // T = Widget   -> arg es Widget&& -> forward reenvía un rvalue
```

### Por qué recibir por valor (`T arg`) no es equivalente

```cpp
template <typename T> void wrapper(T arg) { inner(arg); }
```

Aquí **siempre** hay una copia (o un movimiento, pero nunca un reenvío real de la categoría de valor original) al construir `arg` a partir del argumento. Se pierde la posibilidad de reenviar la categoría de valor a `inner`, que es justo el objetivo del perfect forwarding: evitar copias innecesarias cuando no hacen falta, preservando semántica cuando sí las necesitas.

### Ejercicio 11

```cpp
template <typename T>
void log_y_reenvia(T&& valor) {
    std::cout << "procesando...\n";
    destino(std::forward<T>(valor));
}
```

Para cada una de estas llamadas, indica a qué se deduce `T` y si `destino` recibirá un lvalue o un rvalue:

a) `int x = 5; log_y_reenvia(x);`
b) `log_y_reenvia(42);`
c) `std::string s = "hola"; log_y_reenvia(std::move(s));`

---

## 12. std::optional

### ¿Qué es y qué problema resuelve?

`std::optional<T>` (C++17) representa "puede haber un valor de tipo `T`, o puede no haberlo", sin recurrir a valores sentinela ad hoc como `-1`, `0` o punteros nulos.

```cpp
std::optional<size_t> buscarIndice(const std::vector<int>& v, int valor) {
    for (size_t i = 0; i < v.size(); ++i) {
        if (v[i] == valor) return i;
    }
    return std::nullopt;
}
```

### Por qué es mejor que un sentinela como -1

`size_t` es un tipo **sin signo**. Si usaras `-1` como sentinela de "no encontrado" con un tipo sin signo, `-1` se convierte silenciosamente en un valor enorme (por wraparound), no en un negativo: una fuente clásica de bugs si alguien compara `indice >= 0` (siempre verdadero para `size_t`) esperando detectar el caso "no encontrado". `std::optional` separa completamente el "no hay valor" del valor en sí, sin ambigüedad y sin coste de asignación dinámica (se almacena "en línea", normalmente en la pila, junto a un flag de presencia).

### Acceso: las tres formas y sus diferencias

```cpp
std::optional<size_t> r = buscarIndice(v, 99);

*r;              // UB si r está vacío -- NO devuelve nada "por defecto"
r.value();       // lanza std::bad_optional_access si está vacío
r.value_or(0);   // devuelve 0 si está vacío, sin lanzar nada
if (r.has_value()) { /* uso seguro */ }
```

El error típico es asumir que acceder a un `optional` vacío "no pasa nada" y devuelve algo por defecto silenciosamente. Solo `value_or` hace eso; `operator*` y `value()` no.

### Ejercicio 12

Reescribe esta función que usa `-1` como sentinela para que use `std::optional<int>`, y escribe el código que la llama comprobando el resultado de forma segura:

```cpp
int buscarPrimerNegativo(const std::vector<int>& v) {
    for (size_t i = 0; i < v.size(); ++i)
        if (v[i] < 0) return static_cast<int>(i);
    return -1;
}
```

---

## 13. Localidad de caché y contigüidad de memoria

### El problema: vector<vector<int>> vs. buffer plano

```cpp
std::vector<std::vector<int>> matrizA;               // "matriz de matrices"
std::vector<int> matrizB;                             // buffer plano, fila-mayor
// acceso: matrizB[fila * numColumnas + columna]
```

`std::vector<std::vector<int>>` **no** garantiza contigüidad entre filas: el vector externo solo almacena punteros a vectores internos, cada uno con su propio bloque de memoria reservado de forma independiente, potencialmente disperso por el heap. Acceder a `matrizA[i]` implica primero leer ese puntero (una indirección) y luego saltar a un bloque de memoria que puede estar lejos de los demás: más fallos de caché, peor aprovechamiento del *prefetcher* de la CPU.

Un buffer plano (`matrizB`) mantiene **todos** los elementos en un único bloque contiguo. Recorrerlo secuencialmente favorece la localidad espacial: cuando la CPU carga una línea de caché, trae de forma "gratuita" varios elementos adyacentes que vas a necesitar a continuación.

Detalle importante que fallaste: el número de columnas **no** necesita conocerse en tiempo de compilación para usar un buffer plano; el índice `fila * numColumnas + columna` se calcula perfectamente en tiempo de ejecución con `numColumnas` como variable normal.

Y recorrer `vector<vector<int>>` **por columnas** en vez de por filas es aún peor: en cada iteración saltas entre vectores internos distintos y dispersos, combinando mala localidad con saltos de puntero constantes.

### Ejercicio 13

Tienes una matriz de 1000×1000 `int` representada como buffer plano fila-mayor. Escribe la expresión de índice para acceder al elemento `(fila=37, columna=812)`, y explica en una frase por qué recorrer la matriz con el bucle exterior sobre filas y el interior sobre columnas es más rápido que al revés.

---

## 14. Bonus: C++ y Python (pybind11)

Este tema apareció mezclado con Python en el test 06 y probablemente lo necesitas si conectas C++ con Python en tu trabajo (extensiones, bindings de visión/robótica).

### Idea central

`pybind11` expone clases C++ a Python mediante `py::class_<T>`. Por defecto, el objeto Python creado **posee** la instancia C++ a través de un *holder* — `std::unique_ptr` por defecto (no `shared_ptr`, aunque es configurable) —, y cuando el `refcount` del wrapper Python llega a cero, se destruye también el objeto C++.

```cpp
py::class_<Sensor>(m, "Sensor")
    .def(py::init<std::string>());
```

### Los dos matices peligrosos

1. **CPython no rastrea punteros crudos en la pila de C++.** Si tu código C++ guarda un `PyObject*` crudo sin `Py_INCREF` (o sin usar `py::object`, que lo hace automáticamente en su constructor/destructor), el objeto Python puede liberarse mientras tu puntero crudo sigue "vivo" desde el punto de vista de C++: use-after-free.
2. **`py::gil_scoped_release` no se reactiva solo.** Si liberas el GIL para hacer trabajo pesado en C++ puro, cualquier llamada posterior a la API de Python (incluido `Py_INCREF`/`Py_DECREF`) sin volver a adquirir el GIL explícitamente con `py::gil_scoped_acquire` es comportamiento indefinido. pybind11 no lo hace automáticamente por ti.

### Ejercicio 14

En una función C++ expuesta con pybind11 que recibe una lista grande de Python, haces trabajo intensivo en C++ liberando el GIL con `py::gil_scoped_release` para no bloquear otros hilos de Python. A mitad de ese trabajo necesitas llamar a un callback de Python que te pasaron como argumento. ¿Qué tienes que hacer antes de invocar ese callback, y por qué?

---

## Soluciones

### Solución 1

a) Como `Matriz` declara un destructor propio y no declara move constructor ni move assignment, el compilador **no genera** los miembros de movimiento implícitamente (la declaración del destructor los suprime). Sí sigue generando copy constructor y copy assignment (aunque deprecados), que copian el puntero `datos_` de forma superficial. Por tanto, `std::vector<Matriz>` usará el **constructor de copia** durante la reallocation, no el de movimiento: cada `Matriz` copiada comparte temporalmente el mismo `datos_` que el original hasta que ambos destructores hagan `delete[]` sobre el mismo puntero → doble `delete`, comportamiento indefinido.

b)
```cpp
class Matriz {
public:
    Matriz(int filas, int cols)
        : filas_(filas), cols_(cols), datos_(filas * cols) {}
private:
    int filas_, cols_;
    std::vector<double> datos_;   // regla de cero: delega en vector
};
```

### Solución 2

a) (A) copia: `origen` es un lvalue, y como `procesar` recibe `std::string` por valor, se invoca el constructor de copia. (B) movimiento: `std::move(origen)` convierte `origen` en un rvalue, seleccionando el constructor de movimiento de `std::string` al inicializar el parámetro por valor de `procesar`. (C) construcción directa/movimiento sin copia real: `std::string("hola")` ya es un prvalue temporal; se usa para inicializar el parámetro por valor sin copia (elisión o move trivial).

b) Tras (B), `origen` queda en un estado válido pero no especificado (probablemente vacío en la práctica, pero no garantizado por el estándar). Es seguro destruirlo o asignarle un nuevo valor (`origen = "otra cosa";`); no es seguro asumir ningún contenido concreto ni su longitud antes de reasignarlo.

### Solución 3

Salida:
```
dentro: vivo
destruyendo cam0
fuera: expirado
ya no existe
```
`observador.lock()` nunca puede causar use-after-free porque, si el objeto ya fue destruido, `lock()` comprueba internamente el bloque de control compartido y devuelve un `shared_ptr` **vacío** (nulo), no un puntero colgante hacia memoria liberada. El `if (auto sp = observador.lock())` es falso y entra en el `else`.

### Solución 4

a) `id` es un **parámetro** de `registrar`, con vida ligada a cada llamada a `registrar`. Cada lambda captura `[&id]` por referencia a *ese* parámetro concreto, que deja de existir en cuanto `registrar` retorna. Al llamar a los callbacks después, todas acceden a memoria ya liberada: comportamiento indefinido (probablemente verás basura o el mismo valor repetido, pero no está garantizado).

b)
```cpp
void registrar(int id) {
    callbacks.push_back([id]() {           // captura por VALOR
        std::cout << "callback " << id << "\n";
    });
}
```

### Solución 5

```cpp
template <typename T>
T mayor(const T& a, const T& b) { return (a > b) ? a : b; }

template <>
const char* mayor<const char*>(const char* const& a, const char* const& b) {
    return (std::strcmp(a, b) > 0) ? a : b;
}
```
Sin la especialización, `operator>` sobre dos `const char*` compara **direcciones de memoria**, no el contenido de las cadenas: el resultado depende de dónde el compilador/enlazador decidió colocar cada literal, no de cuál cadena es "mayor" alfabéticamente. Es una comparación sin significado semántico útil.

### Solución 6

a) No es seguro en ningún caso. Si hay reallocation, todo el bloque de memoria se mueve y `it_ultimo` queda apuntando a memoria liberada. Si no hay reallocation, `push_back` sigue siendo seguro para los iteradores **anteriores** al nuevo elemento, así que en este caso concreto (añadir al final) `it_ultimo` técnicamente seguiría apuntando al elemento en la posición 4 (el 50) — pero como no puedes saber de antemano si habrá o no reallocation sin consultar `capacity()`, la práctica correcta es no asumir nada y volver a pedir el iterador después.

b)
```cpp
v.push_back(60);
auto it_ultimo = std::prev(v.end());   // o: v.end() - 1, pedido DESPUÉS del push_back
```

### Solución 7

a) `std::list` (o `std::deque` si también necesitas algo de acceso por índice ocasional): inserciones/borrados O(1) en cualquier punto conocido, sin desplazar el resto de elementos.
b) `std::unordered_map<std::string, ...>`: búsqueda amortizada O(1), y no te importa el orden.
c) `std::map<std::string, Empleado>` con la clave siendo el apellido (o un struct comparador si necesitas clave compuesta): mantiene orden automáticamente, O(log n) por inserción.
d) `std::queue<Tarea>`: adaptador FIFO diseñado exactamente para esto.

### Solución 8

a) El acumulador es `uint8_t` (deducido del valor inicial `0`, que aquí se interpreta como `uint8_t` por el contexto del tipo de retorno... en realidad en la llamada real `std::accumulate(bytes.begin(), bytes.end(), 0)` el acumulador sería `int` porque `0` es `int` — pero como el ejercicio lo asigna a un `uint8_t total`, hay una conversión truncante final igualmente. Suma real: 200+100+50 = 350. Si el acumulador fuese `uint8_t` desde el principio (por ejemplo pasando `uint8_t(0)` como valor inicial), el resultado se truncaría en **cada suma parcial** vía aritmética módulo 256: 350 mod 256 = 94.

b)
```cpp
int total_int = std::accumulate(bytes.begin(), bytes.end(), 0); // acumula en int
uint8_t total = static_cast<uint8_t>(total_int); // trunca solo una vez, al final
```

### Solución 9

```cpp
std::vector<long long> parciales(4, 0);
std::vector<std::thread> hilos;
for (int t = 0; t < 4; ++t) {
    hilos.emplace_back([&, t]() {
        long long local = 0;
        for (int i = rango_inicio(t); i < rango_fin(t); ++i)
            local += static_cast<long long>(datos[i]) * datos[i];
        parciales[t] = local;   // cada hilo escribe SOLO en su propia posición
    });
}
for (auto& h : hilos) h.join();
long long total = 0;
for (auto p : parciales) total += p;  // secuencial, un solo hilo -> sin sincronización
```
Es seguro porque, durante el bucle paralelo, cada hilo lee/escribe únicamente su propia variable local y su propia posición de `parciales` (no hay solapamiento de escrituras entre hilos). La suma final ocurre después de `join()`, cuando ya no hay concurrencia: se ejecuta en un único hilo, así que no puede haber data race.

### Solución 10

Falta el `acquire` en el lado del consumidor. La relación happens-before release-acquire requiere **ambos** lados sincronizados sobre la misma variable atómica: un `store` `release` sin un `load` `acquire` correspondiente no publica nada de forma garantizada — el hilo que hace `load` con `relaxed` puede seguir sin ver `datos = 42` incluso si observa `listo == true`, porque su propio `load` relajado no impone ninguna barrera de sincronización en su extremo. Hacen falta los dos: `release` en el productor **y** `acquire` en el consumidor.

### Solución 11

a) `x` es un lvalue → `T` se deduce como `int&` → colapso de referencias da `int&` → `destino` recibe un **lvalue**.
b) `42` es un rvalue (prvalue) → `T` se deduce como `int` → el parámetro es `int&&` → `destino` recibe un **rvalue**.
c) `std::move(s)` es un rvalue → `T` se deduce como `std::string` → el parámetro es `std::string&&` → `destino` recibe un **rvalue** (y probablemente termina moviendo `s`, así que `s` queda en estado válido pero no especificado después de esta llamada).

### Solución 12

```cpp
std::optional<int> buscarPrimerNegativo(const std::vector<int>& v) {
    for (size_t i = 0; i < v.size(); ++i)
        if (v[i] < 0) return static_cast<int>(i);
    return std::nullopt;
}

auto r = buscarPrimerNegativo(datos);
if (r.has_value()) {
    std::cout << "primer negativo en índice " << *r << "\n";
} else {
    std::cout << "no hay negativos\n";
}
```

### Solución 13

Índice: `indice = 37 * 1000 + 812;` (en general, `fila * numColumnas + columna`).

Recorrer filas por fuera y columnas por dentro accede a posiciones de memoria **consecutivas** en cada paso del bucle interno (porque el layout es fila-mayor), lo que maximiza la reutilización de líneas de caché ya cargadas y favorece el prefetching. Recorrerlo al revés (columnas por fuera) saltaría `numColumnas` posiciones en cada paso, generando muchos más fallos de caché.

### Solución 14

Antes de invocar el callback de Python tienes que volver a adquirir el GIL explícitamente con `py::gil_scoped_acquire` (normalmente en un bloque de ámbito reducido alrededor de la llamada al callback). Cualquier interacción con la API de Python — y llamar a un objeto invocable de Python es justo eso — requiere tener el GIL adquirido; pybind11 no lo reactiva automáticamente solo porque lo hayas liberado antes, así que hacerlo sin `gil_scoped_acquire` es comportamiento indefinido.
