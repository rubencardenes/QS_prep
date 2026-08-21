# Resultado del test — C++ moderno (C++11/14/17/20)

- Fecha: 2026-08-05 12:15
- Nivel: media
- Puntuación: **43%** (2.17/5 puntos)
- Preguntas perfectas: 1/5

## Revisión pregunta a pregunta

### ❌ Pregunta 1 — Semántica de movimiento y constructores de copia

Analiza la siguiente clase, que gestiona un array dinámico y define tanto constructor de copia como constructor de movimiento:

```cpp
class Buffer {
public:
    Buffer(size_t n) : size_(n), data_(new int[n]) {}

    Buffer(Buffer&& other) noexcept
        : size_(other.size_), data_(other.data_) {
        other.data_ = nullptr;
        other.size_ = 0;
    }

    Buffer(const Buffer& other)
        : size_(other.size_), data_(new int[other.size_]) {
        std::copy(other.data_, other.data_ + size_, data_);
    }

    ~Buffer() { delete[] data_; }
private:
    size_t size_;
    int* data_;
};
```

¿Cuáles de las siguientes afirmaciones son correctas?

- [ ] **El constructor de movimiento marcado `noexcept` permite que `std::vector<Buffer>` use movimiento en lugar de copia durante las realocaciones al crecer, mejorando el rendimiento.** — _correcta_: Correcto. `std::vector` solo usa el constructor de movimiento en reallocaciones si este es `noexcept` (o no hay constructor de copia); de lo contrario recurre a copiar para garantizar la garantía fuerte de excepciones.
- [ ] **Si se omitiera la línea `other.data_ = nullptr;` dentro del constructor de movimiento, se produciría un doble `delete` al destruirse ambos objetos.** — _correcta_: Correcto. Sin poner a `nullptr` el puntero de `other`, ambos objetos (`other` y el nuevo) apuntarían al mismo bloque de memoria, y sus destructores lo liberarían dos veces, causando comportamiento indefinido.
- [ ] **El compilador generará implícitamente un operador de asignación por movimiento, ya que existe un constructor de movimiento definido por el usuario.** — _incorrecta_: Falso. Declarar explícitamente el constructor de movimiento (o de copia, o el destructor) suprime la generación implícita del operador de asignación por movimiento; habría que declararlo manualmente.
- [x] **`std::move(other)` garantiza que se invoque la sobrecarga de movimiento, independientemente de si existe una sobrecarga de movimiento aplicable.** — _incorrecta_: Falso. `std::move` solo realiza un `static_cast` a referencia rvalue; si no existe constructor/asignación de movimiento aplicable, la resolución de sobrecarga recurre silenciosamente a la versión de copia.

> La pregunta evalúa la comprensión de move semantics del Rule of Three/Five: cómo `noexcept` afecta a la elección de move vs copy en contenedores STL, la suspensión de generación implícita de miembros especiales, y el riesgo de doble liberación si no se deja el objeto origen en un estado válido tras el movimiento.
>
> Repasar: `Rule of Five, std::move, noexcept en constructores de movimiento`

### ✅ Pregunta 2 — Lambdas: captura de variables y ciclos de vida

Analiza el siguiente código:

```cpp
#include <functional>
#include <iostream>

std::function<int()> hacer_contador() {
    int valor = 0;
    auto incrementar = [&valor]() {
        return ++valor;
    };
    return incrementar;
}

int main() {
    auto contador = hacer_contador();
    std::cout << contador() << std::endl;
}
```

¿Cuál de las siguientes afirmaciones es correcta?

- [x] **El código tiene comportamiento indefinido porque `valor` es una variable local que deja de existir cuando `hacer_contador` retorna, y la lambda captura `valor` por referencia colgante.** — _correcta_: Correcto. `[&valor]` captura la variable local por referencia; al terminar `hacer_contador`, `valor` se destruye y la referencia interna de la lambda queda colgante (dangling), produciendo UB al invocar `contador()`.
- [ ] **El resultado de la llamada `contador()` es determinista y siempre imprime 1.** — _incorrecta_: Falso. Al tratarse de comportamiento indefinido (referencia colgante), no hay garantía de ningún valor concreto; el programa podría imprimir cualquier cosa o incluso fallar.
- [ ] **El código es válido y seguro porque `std::function` prolonga automáticamente la vida de todas las variables capturadas por referencia, similar a lo que hace `shared_ptr`.** — _incorrecta_: Falso. `std::function` solo gestiona la vida del objeto invocable (la lambda en sí, tipo-borrado), no la de las variables externas capturadas por referencia. No hay extensión de vida ninguna sobre `valor`.
- [ ] **El problema se solucionaría capturando `valor` por valor con `[valor]`, ya que las lambdas que capturan por valor siempre permiten modificar su copia interna sin necesidad de ninguna palabra clave adicional.** — _incorrecta_: Falso. El `operator()` generado por una lambda es `const` por defecto, así que modificar una variable capturada por valor (`++valor`) no compilaría; haría falta marcar la lambda como `mutable`.
- [ ] **El código no compila porque no se puede capturar por referencia una variable local dentro de una lambda que se retorna desde una función.** — _incorrecta_: Falso. Capturar por referencia es sintácticamente válido y compila sin errores ni advertencias obligatorias; el problema es puramente de tiempo de ejecución (UB), no de compilación.

> Capturar variables locales por referencia en una lambda que se devuelve o se almacena para uso posterior (p. ej. en un `std::function` retornado) es un error clásico: si la variable capturada tiene duración automática, su vida termina al salir del ámbito, dejando referencias colgantes. La solución habitual es capturar por valor (añadiendo `mutable` si se necesita modificar la copia) o usar variables con vida más larga (p. ej. `static`, miembros de clase o gestionadas con `shared_ptr`).
>
> Repasar: `Captura por referencia en lambdas y dangling reference`

### ⚠️ Pregunta 3 — Atomics: memory order y carreras de datos

Dado el siguiente patrón productor-consumidor:

```cpp
#include <atomic>
#include <thread>
#include <iostream>

int datos = 0;
std::atomic<bool> listo{false};

void productor() {
    datos = 42;
    listo.store(true, std::memory_order_relaxed);
}

void consumidor() {
    while (!listo.load(std::memory_order_relaxed)) {}
    std::cout << datos << std::endl;
}
```

¿Cuáles de las siguientes afirmaciones son correctas?

- [x] **Usar `memory_order_relaxed` en ambos accesos a `listo` no garantiza que el consumidor vea `datos = 42` una vez que observa `listo == true`; existe una carrera de datos porque no se establece una relación happens-before entre las operaciones sobre `datos`.** — _correcta_: Correcto. `memory_order_relaxed` solo garantiza atomicidad sobre la propia variable atómica, sin orden de sincronización con otras variables. `datos` es un `int` no atómico, así que el acceso concurrente sin happens-before es una carrera de datos y comportamiento indefinido.
- [x] **Cambiar el store a `memory_order_release` y el load a `memory_order_acquire` establece una relación happens-before que garantiza que el consumidor vea `datos = 42` tras observar `listo == true`.** — _correcta_: Correcto. El par release-acquire crea una relación de sincronización: todas las escrituras anteriores al `store` release (incluyendo `datos = 42`) son visibles para el hilo que hace el `load` acquire correspondiente y observa el valor almacenado.
- [ ] **El problema desaparecería si se declarara `datos` como `volatile int` en lugar de usar sincronización, ya que `volatile` garantiza atomicidad y visibilidad entre hilos en C++.** — _incorrecta_: Falso, es un error común (confusión con Java/C#). En C++, `volatile` solo impide ciertas optimizaciones del compilador sobre accesos a memoria; no garantiza atomicidad ni visibilidad entre hilos ni establece happens-before.
- [ ] **Da igual qué `memory_order` se use en `listo`: siempre habrá comportamiento indefinido sobre `datos` porque es una variable no atómica, sin excepción posible.** — _incorrecta_: Falso. Aunque `datos` no sea atómico, usar `memory_order_release`/`acquire` (o `seq_cst`) sobre `listo` establece happens-before y elimina la carrera de datos sobre `datos`; el UB depende precisamente del memory order elegido.
- [x] **Usar `std::memory_order_seq_cst` (el valor por defecto) sería equivalente en términos de sincronización a usar `memory_order_relaxed`, ya que ambos son válidos para tipos `std::atomic<bool>`.** — _incorrecta_: Falso. `seq_cst` es estrictamente más fuerte: además de atomicidad, aporta semántica de adquisición/liberación y un orden total consistente entre todos los hilos, mientras que `relaxed` no ofrece ninguna garantía de orden entre variables distintas.

> El modelo de memoria de C++ distingue entre atomicidad (garantizada por `std::atomic` con cualquier memory order) y orden/sincronización entre hilos (que depende del memory order elegido). `memory_order_relaxed` no crea relaciones happens-before con otras variables, por lo que un patrón de publicación como este necesita como mínimo `release`/`acquire` (o `seq_cst`) para ser correcto y evitar carreras de datos sobre variables no atómicas.
>
> Repasar: `std::memory_order, release-acquire y happens-before`

### ⚠️ Pregunta 4 — shared_ptr, weak_ptr y ciclos de referencia

Dado el siguiente código:

```cpp
struct Node {
    std::shared_ptr<Node> next;
    std::weak_ptr<Node> prev;
};

auto a = std::make_shared<Node>();
auto b = std::make_shared<Node>();
a->next = b;
b->prev = a;
```

¿Cuáles de las siguientes afirmaciones son correctas?

- [x] **Tras ejecutar el código, `a.use_count()` es 1, ya que `b->prev` es un `weak_ptr` y no contribuye al conteo de referencias fuertes.** — _correcta_: Correcto. La única referencia fuerte a los datos de `a` es la variable local `a`; `b->prev` es débil y no cuenta, por lo que `use_count()` permanece en 1.
- [x] **Si `prev` fuera `std::shared_ptr<Node>` en lugar de `weak_ptr`, ni `a` ni `b` se destruirían automáticamente al salir del scope, provocando una fuga de memoria.** — _correcta_: Correcto. Con dos `shared_ptr` fuertes apuntándose mutuamente, cada objeto mantiene al otro con `use_count` >= 1 incluso tras salir de scope, impidiendo su destrucción (ciclo de referencias clásico).
- [x] **Como `prev` es `std::weak_ptr`, no incrementa el contador de referencias de `a`, por lo que no se produce fuga de memoria por ciclo de referencia entre `a` y `b`.** — _correcta_: Correcto. `weak_ptr` observa el objeto sin poseerlo (no incrementa el `use_count`), rompiendo el ciclo fuerte que impediría que el contador llegara a cero.
- [x] **`std::make_shared<Node>()` realiza dos asignaciones de memoria independientes (una para el objeto de control y otra para el `Node`), lo cual es menos eficiente que usar `new Node()` junto con `shared_ptr`.** — _incorrecta_: Falso, es justo al revés: `make_shared` combina el bloque de control y el objeto en una única asignación, siendo más eficiente que `shared_ptr<Node>(new Node())`, que sí requiere dos asignaciones separadas.
- [ ] **`b->prev.lock()` devuelve un `std::shared_ptr<Node>` válido incluso después de que `a` haya sido destruido y su memoria liberada.** — _incorrecta_: Falso. Si el objeto apuntado ya fue destruido, `weak_ptr::lock()` devuelve un `shared_ptr` vacío (nulo); nunca da acceso a memoria liberada.

> La pregunta explora la diferencia entre propiedad fuerte (`shared_ptr`) y observación débil (`weak_ptr`), el problema clásico de ciclos de referencia en estructuras enlazadas o de padre-hijo, el comportamiento de `lock()` sobre punteros expirados, y la eficiencia de `make_shared` frente a construir un `shared_ptr` a partir de `new`.
>
> Repasar: `std::weak_ptr, ciclos de referencia, std::make_shared`

### ❌ Pregunta 5 — Perfect forwarding con referencias universales

Considera la siguiente plantilla de función:

```cpp
template <typename T>
void wrapper(T&& arg) {
    inner(std::forward<T>(arg));
}
```

¿Cuál de las siguientes afirmaciones es correcta?

- [ ] **Gracias a la deducción de tipos y al colapso de referencias, `wrapper` puede aceptar tanto lvalues como rvalues, y `std::forward<T>(arg)` preserva la categoría de valor original al invocar `inner`.** — _correcta_: Correcto. Cuando se pasa un lvalue, `T` se deduce como `U&` (colapsando a `U&`); cuando se pasa un rvalue, `T` se deduce como `U`, dando `U&&`. `std::forward<T>` reconstruye la categoría de valor original, evitando copias o movidas incorrectas.
- [ ] **La función sería igual de genérica y eficiente si se declarara como `void wrapper(T arg)` en lugar de `T&& arg`, ya que ambas formas evitan copias innecesarias.** — _incorrecta_: Falso. `void wrapper(T arg)` recibe el argumento por valor, provocando una copia (o movimiento, pero nunca forwarding real) en cada llamada, perdiendo la capacidad de reenviar la categoría de valor original a `inner`.
- [x] **Usar `std::move(arg)` en lugar de `std::forward<T>(arg)` sería equivalente en este contexto, ya que ambos convierten `arg` a rvalue de la misma manera.** — _incorrecta_: Falso. `std::move` siempre castea a rvalue sin importar la categoría original, lo que podría mover incorrectamente de un argumento que el llamador pasó como lvalue; `std::forward` solo castea a rvalue si `T` corresponde a un rvalue original.
- [ ] **Si se llama `wrapper(x)` con `x` una variable lvalue de tipo `int`, la plantilla se instanciará como `void wrapper(int&& arg)`.** — _incorrecta_: Falso. Con un argumento lvalue de tipo `int`, `T` se deduce como `int&`, y por colapso de referencias el parámetro resultante es `int&`, no `int&&`.
- [ ] **`T&&` es siempre una referencia rvalue, por lo que `wrapper` solo puede recibir argumentos temporales (rvalues).** — _incorrecta_: Falso. Como `T` se deduce en la propia llamada, `T&&` es una referencia universal (forwarding reference), no una rvalue reference fija, y puede vincularse tanto a lvalues como a rvalues.

> La pregunta evalúa el entendimiento de forwarding references (referencias universales), la deducción de tipos con colapso de referencias, y la diferencia semántica entre `std::forward` y `std::move`, un tema central del perfect forwarding introducido en C++11.
>
> Repasar: `Forwarding references, std::forward, reference collapsing`
