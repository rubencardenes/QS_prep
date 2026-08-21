# Resultado del test — C++ moderno (C++11/14/17/20)

- Fecha: 2026-08-04 11:04
- Nivel: media
- Puntuación: **25%** (2.50/10 puntos)
- Preguntas perfectas: 1/10

## Revisión pregunta a pregunta

### ❌ Pregunta 1 — Concurrencia: data race, lock_guard RAII y atomics

Dado el siguiente código, donde varios hilos incrementan `contador` protegido manualmente con `lock()`/`unlock()`:

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

¿Cuál de las siguientes afirmaciones es correcta?

- [ ] **Particionar el trabajo dando a cada hilo un contador local y sumando los resultados tras el `join()` evitaría la contención del mutex durante el bucle, aunque seguiría siendo necesario usar atomics para sumar los resultados parciales al final.** — _incorrecta_: Incorrecto en la última parte: la técnica de particionamiento con contadores locales es válida y reduce contención, pero la suma final tras `join()` se ejecuta secuencialmente en un solo hilo, por lo que no requiere atomics ni mutex.
- [ ] **Si `trabajo()` lanzase una excepción entre `lock()` y `unlock()`, el mutex quedaría bloqueado permanentemente; por eso sería más seguro usar `std::lock_guard<std::mutex>` para garantizar el desbloqueo mediante RAII.** — _correcta_: Correcto: `lock_guard` libera el mutex automáticamente en su destructor incluso si se propaga una excepción, evitando interbloqueos por rutas de salida no controladas. Es el patrón RAII estándar para mutexes en C++11.
- [ ] **Cambiar `lock()`/`unlock()` por `lock_guard` no altera el comportamiento observable, ya que ambos ofrecen exactamente las mismas garantías; RAII es solo una cuestión de estilo sin beneficio funcional.** — _incorrecta_: Incorrecto: hay una diferencia funcional real, no solo de estilo: `lock_guard` garantiza el desbloqueo ante excepciones o retornos anticipados, algo que el manejo manual no ofrece salvo que se añada `try/catch` explícito.
- [x] **El código es seguro tal como está porque `contador++` es una operación atómica en la mayoría de arquitecturas modernas, así que el mutex resulta redundante.** — _incorrecta_: Incorrecto: `contador++` sobre un `long` normal no es atómico en C++ (implica lectura-modificación-escritura sin garantías); sin `std::atomic` o sincronización explícita hay data race, independientemente de la arquitectura subyacente.
- [ ] **Sustituir `long contador` por `std::atomic<long>` y eliminar el mutex requeriría mantener igualmente el mutex para evitar el 'problema ABA' en incrementos simples.** — _incorrecta_: Incorrecto: el problema ABA afecta a algoritmos lock-free basados en compare-and-swap sobre estructuras compuestas (p. ej. pilas), no a un simple incremento atómico; `std::atomic<long>::operator++` ya es seguro por sí solo.

> El ejemplo ilustra un data race potencial si se elimina la sincronización, y compara mecanismos de protección: `lock_guard` aporta seguridad ante excepciones vía RAII, `std::atomic` evita el mutex para operaciones simples sin necesitar protección adicional tipo ABA, y el particionamiento con acumulación local es una técnica clásica para reducir contención sin sincronización extra en la fase de combinación final.
>
> Repasar: `std::lock_guard (RAII), std::atomic, particionamiento para reducir contención`

### ⚠️ Pregunta 2 — Templates: polimorfismo en tiempo de compilación vs. despacho virtual

Dado el siguiente código:

```cpp
template <typename T>
void imprimir(const T& valor) {
    std::cout << "generico: " << valor << "\n";
}

template <>
void imprimir<bool>(const bool& valor) {
    std::cout << "booleano: " << (valor ? "si" : "no") << "\n";
}

struct Base {
    virtual void saludar() const { std::cout << "Base\n"; }
};

struct Derivada : Base {
    void saludar() const override { std::cout << "Derivada\n"; }
};
```

¿Cuáles de las siguientes afirmaciones sobre la especialización de `imprimir` y el despacho virtual de `saludar()` son correctas? (selecciona todas las que apliquen)

- [ ] **La especialización de plantillas incurre en el mismo coste de indirección en tiempo de ejecución que una llamada virtual, porque el compilador genera una tabla de despacho para las especializaciones.** — _incorrecta_: Incorrecto: no existe tabla de despacho para especializaciones de plantillas; el compilador genera código directo para el tipo concreto, sin indirección ni coste de vtable.
- [ ] **Añadir una nueva especialización de `imprimir` para, por ejemplo, `std::string` requiere modificar el código de la plantilla genérica, igual que añadir una nueva clase derivada de `Base` requiere modificar `Base`.** — _incorrecta_: Incorrecto: ambos mecanismos son abiertos a extensión sin modificar el código existente (principio abierto/cerrado): se puede añadir una especialización o una clase derivada nueva sin tocar la plantilla genérica ni `Base`.
- [ ] **La decisión de qué versión de `imprimir` se ejecuta ocurre en tiempo de ejecución, igual que ocurre con `saludar()` al llamarse a través de un puntero `Base*`.** — _incorrecta_: Incorrecto: la resolución de plantillas es estática (compile-time); solo el despacho virtual mediante vtable se resuelve en tiempo de ejecución. Confundir ambos mecanismos es un error habitual.
- [ ] **La llamada `imprimir(true)` invoca la especialización explícita para `bool`, y esa resolución se decide en tiempo de compilación.** — _correcta_: Correcto: la especialización de plantillas es un mecanismo de polimorfismo estático; el compilador elige la versión adecuada según el tipo deducido antes de generar el binario.
- [x] **Si se llama a `saludar()` a través de un `Base*` que apunta a una `Derivada`, se ejecuta `Derivada::saludar()` gracias a la tabla de punteros virtuales (vtable), resuelta en tiempo de ejecución.** — _correcta_: Correcto: las funciones `virtual` usan despacho dinámico a través de la vtable, determinado por el tipo real del objeto en tiempo de ejecución, no por el tipo estático del puntero.

> Las plantillas implementan polimorfismo en tiempo de compilación (resolución estática, sin coste de indirección), mientras que las funciones virtuales implementan polimorfismo en tiempo de ejecución mediante vtable. Ambos permiten extensibilidad sin modificar el código base, pero difieren fundamentalmente en cuándo y cómo se resuelve la llamada.
>
> Repasar: `Especialización de plantillas vs. funciones virtuales (static vs. dynamic polymorphism)`

### ❌ Pregunta 3 — Move semantics: lvalue, rvalue y std::move

Dado el siguiente código:

```cpp
std::vector<int> v1 = {1, 2, 3};
std::vector<int> v2 = std::move(v1);
```

¿Cuáles de las siguientes afirmaciones son correctas? (selecciona todas las que correspondan)

- [ ] **Una función `void f(std::vector<int>&& v)` no puede invocarse pasando v1 directamente, porque v1 es un lvalue y una referencia rvalue no se enlaza a un lvalue.** — _correcta_: Correcto: v1 es un lvalue con nombre; para llamar a f hace falta un rvalue explícito, por ejemplo f(std::move(v1)) o f(std::vector<int>{...}).
- [ ] **std::move(v1) no mueve nada por sí mismo; solo convierte v1 en una referencia rvalue (es esencialmente un static_cast<T&&>), habilitando que se seleccione la sobrecarga de movimiento si existe.** — _correcta_: Correcto: std::move es solo una anotación de tipo. El movimiento real ocurre en el constructor/asignación de movimiento invocado, no en la llamada a std::move.
- [x] **Tras la línea, se garantiza por el estándar que v1 queda vacío (v1.size() == 0), ya que así lo exige la especificación de std::vector.** — _incorrecta_: Incorrecto: el estándar solo garantiza que v1 queda en un estado 'válido pero no especificado' tras ser movido; que quede vacío es un detalle habitual de implementación (libstdc++/libc++), no una garantía normativa.
- [ ] **Si la clase contenedora de v1 declara explícitamente un destructor personalizado, el compilador no generará automáticamente el constructor ni el operador de asignación de movimiento, y las 'operaciones de movimiento' caerán silenciosamente en copias.** — _correcta_: Correcto: declarar un destructor (u otros miembros especiales) suprime la generación implícita de move constructor/move assignment; el compilador recurre entonces a la copia si está disponible, sin error de compilación pero con pérdida de rendimiento.
- [ ] **Devolver v2 por valor desde una función (`return v2;`) impide el movimiento automático, por lo que siempre hay que escribir `return std::move(v2);` para evitar una copia.** — _incorrecta_: Incorrecto: para variables locales automáticas, el compilador aplica NRVO o, si no elide la copia, selecciona automáticamente el constructor de movimiento. Añadir std::move explícito en un return puede incluso impedir la elisión de copia (RVO).

> La semántica de movimiento (C++11) permite transferir recursos internos de un objeto temporal o marcado con std::move a otro, evitando copias costosas. Es clave distinguir que std::move solo habilita el movimiento (cast a rvalue reference) y que el estado post-movimiento es 'válido pero no especificado', no una fuga ni un UB.
>
> Repasar: `std::move, rvalue references, move constructor, regla de los cinco`

### ❌ Pregunta 4 — Invalidación de iteradores: reasignación, insert, erase

Analiza el siguiente fragmento:

```cpp
std::vector<int> v = {1, 2, 3, 4, 5};
auto it = v.begin() + 2; // apunta al valor 3
v.insert(v.begin(), 0);  // inserta al principio
*it = 100;               // ¿qué ocurre aquí?
```

¿Cuál de las siguientes afirmaciones describe correctamente el comportamiento del código?

- [x] **Es equivalente a usar std::list, donde insertar al principio nunca invalida iteradores existentes porque los nodos no se mueven en memoria.** — _incorrecta_: Incorrecto: esa propiedad es cierta para std::list (los iteradores solo se invalidan si se borra el nodo apuntado), pero no aplica a std::vector, que es el contenedor del ejemplo.
- [ ] **El código es válido: insert solo invalida iteradores anteriores al punto de inserción, y como it apunta después de ese punto, sigue siendo válido y ahora referencia al valor 2.** — _incorrecta_: Incorrecto: es justo al revés. Los iteradores anteriores al punto de inserción se mantienen válidos; los que están en el punto de inserción o después quedan invalidados.
- [x] **El código es válido siempre que la capacidad del vector sea suficiente para evitar una reubicación de memoria; en ese caso it seguiría apuntando al tercer elemento original (valor 3).** — _incorrecta_: Incorrecto: aunque no haya reallocation, insert desplaza físicamente los elementos posteriores al punto de inserción, por lo que el estándar igualmente invalida esos iteradores, no solo por posible reubicación.
- [ ] **El comportamiento es indefinido: insert() al principio de un vector invalida todos los iteradores existentes en o después del punto de inserción, haya o no reubicación de memoria, porque los elementos se desplazan.** — _correcta_: Correcto: el estándar especifica que vector::insert invalida todos los iteradores/referencias en el punto de inserción y posteriores (y todos si hay reallocation); aquí la inserción es en begin(), por lo que it queda invalidado sin importar la capacidad.

> En std::vector, cualquier insert/erase invalida los iteradores en el punto de la operación y posteriores (y todos ante reallocation), a diferencia de contenedores basados en nodos como std::list o std::map, donde la invalidación es mucho más limitada. Confundir estas reglas es una fuente común de UB en producción.
>
> Repasar: `Invalidación de iteradores en std::vector, vector::insert`

### ⚠️ Pregunta 5 — RAII: gestión de recursos con constructor/destructor

Considera la siguiente clase que envuelve un descriptor de fichero siguiendo el patrón RAII:

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

¿Cuáles de las siguientes afirmaciones sobre este código son correctas? (selecciona todas las que correspondan)

- [x] **Si el constructor lanza la excepción, el destructor de ese objeto no llegará a ejecutarse, pero no hay fuga porque fopen falló y no hay recurso que liberar.** — _correcta_: Correcto: en C++ un objeto cuyo constructor lanza una excepción se considera no completamente construido, así que su destructor nunca se invoca; aquí eso es seguro porque fp_ es null.
- [ ] **Este patrón garantiza que fclose se invocará automáticamente al salir del ámbito, incluso si se lanza una excepción en código posterior a la creación del objeto.** — _correcta_: Correcto: esa es la esencia de RAII — el desenrollado de pila (stack unwinding) llama a los destructores de los objetos ya construidos, liberando el recurso sin código adicional.
- [ ] **Copiar un FileHandle por valor es seguro por defecto porque el compilador genera un constructor de copia que duplica el FILE* de forma segura.** — _incorrecta_: Incorrecto: el constructor de copia implícito haría una copia superficial del puntero, provocando doble cierre (double-close) y comportamiento indefinido; habría que eliminar la copia o implementarla explícitamente.
- [ ] **Si se necesitara compartir el mismo FILE* entre varias instancias sin duplicar el recurso, sería más apropiado sustituir el puntero crudo por un std::shared_ptr<FILE> con un deleter personalizado que llame a fclose.** — _correcta_: Correcto: shared_ptr con deleter personalizado permite compartir la propiedad de un recurso no gestionado por new/delete, cerrando el fichero solo cuando el último propietario lo libera.
- [ ] **Usar RAII aquí es funcionalmente idéntico a un bloque try/finally, por lo que no aporta ninguna ventaja real frente a ese estilo.** — _incorrecta_: Incorrecto: aunque el objetivo (liberar siempre el recurso) es similar, RAII no requiere repetir bloques try/finally en cada punto de salida ni cada llamada; el compilador se encarga automáticamente en todas las rutas de salida, incluidos returns múltiples.

> RAII vincula la vida de un recurso (memoria, ficheros, locks, sockets) al ciclo de vida de un objeto: se adquiere en el constructor y se libera en el destructor, garantizando liberación determinista incluso ante excepciones. El error clásico es olvidar la regla de los tres/cinco cuando el recurso es un puntero crudo.
>
> Repasar: `RAII, regla de los tres/cinco, exception safety`

### ❌ Pregunta 6 — Smart pointers: unique_ptr exclusivo vs shared_ptr compartido

El siguiente código no compila:

```cpp
std::unique_ptr<int> a = std::make_unique<int>(42);
std::unique_ptr<int> b = a; // error de compilación
```

¿Cuál es el motivo principal del error?

- [ ] **std::make_unique<int>(42) devuelve un puntero crudo (int*), no un unique_ptr, por lo que la asignación mezcla tipos incompatibles.** — _incorrecta_: Incorrecto: make_unique devuelve exactamente un std::unique_ptr<int> por valor; no hay incompatibilidad de tipos, el problema es la semántica de copia prohibida.
- [ ] **unique_ptr exige que el tipo apuntado (int, en este caso) tenga un constructor de copia definido explícitamente para poder inicializarse.** — _incorrecta_: Incorrecto: el problema no depende del tipo apuntado (int es trivialmente copiable); el error surge porque es unique_ptr, no el int, el que prohíbe la copia a nivel de su propia interfaz.
- [x] **unique_ptr solo puede inicializarse mediante make_unique y no admite ninguna asignación posterior a su creación.** — _incorrecta_: Incorrecto: unique_ptr sí admite asignación de movimiento después de su creación (por ejemplo, b = std::move(a)); lo que no admite es la asignación por copia.
- [x] **unique_ptr tiene eliminado (= delete) su constructor de copia; solo permite transferir la propiedad mediante movimiento, por lo que debería escribirse std::unique_ptr<int> b = std::move(a);** — _correcta_: Correcto: unique_ptr modela propiedad exclusiva, así que copiarlo violaría esa invariante; el estándar lo impide eliminando explícitamente el constructor y el operador de copia, dejando solo las versiones de movimiento.
- [x] **El compilador intenta convertir implícitamente unique_ptr en shared_ptr para realizar la copia, y esa conversión falla en este contexto.** — _incorrecta_: Incorrecto: no existe tal conversión implícita a shared_ptr en una asignación directa entre dos unique_ptr; el error de compilación proviene simplemente de que el constructor de copia de unique_ptr está eliminado.

> unique_ptr (C++11) implementa propiedad exclusiva y no copiable, solo movible, mientras que shared_ptr implementa propiedad compartida mediante conteo de referencias (use_count) con un bloque de control. Confundir ambos modelos es un error frecuente al portar código de punteros crudos.
>
> Repasar: `unique_ptr, shared_ptr, propiedad exclusiva vs compartida`

### ❌ Pregunta 7 — Contenedores STL: vector contiguo, queue FIFO, map ordenado

¿Cuáles de las siguientes afirmaciones sobre los contenedores de la biblioteca estándar de C++ son correctas?

- [ ] **std::map mantiene sus elementos ordenados según la clave (por defecto con std::less), lo que permite recorridos en orden y búsquedas en O(log n) mediante un árbol balanceado.** — _correcta_: Correcto: std::map se implementa típicamente como un árbol rojo-negro balanceado que mantiene el orden de las claves y garantiza complejidad logarítmica.
- [ ] **std::list ofrece acceso aleatorio en O(1) igual que std::vector, ya que ambos son contenedores secuenciales.** — _incorrecta_: Incorrecto: std::list es una lista doblemente enlazada; el acceso a un elemento por posición requiere recorrer los nodos en O(n), no ofrece operator[] ni acceso aleatorio.
- [ ] **std::vector garantiza almacenamiento contiguo en memoria, por lo que &v[0] puede usarse como puntero a un array al estilo C compatible con funciones que esperan T*.** — _correcta_: Correcto: el estándar exige que std::vector almacene sus elementos de forma contigua, propiedad explotada habitualmente para interoperar con APIs en C.
- [x] **std::unordered_map también garantiza orden ascendente de las claves igual que std::map, solo que internamente usa una tabla hash para acelerar las búsquedas.** — _incorrecta_: Incorrecto: std::unordered_map no garantiza ningún orden de iteración; el orden depende de la función hash y la distribución en buckets, y puede cambiar tras un rehash.
- [x] **std::queue es un contenedor adaptador que por defecto usa std::deque como contenedor subyacente y proporciona semántica FIFO (el primer elemento insertado es el primero en salir).** — _correcta_: Correcto: std::queue adapta std::deque por defecto (configurable), exponiendo solo push/pop/front/back con orden FIFO.

> Conocer las garantías de complejidad y layout de memoria de cada contenedor STL es clave para elegir el adecuado: vector para contigüidad y caché, queue para FIFO sobre deque, map para orden y búsqueda logarítmica, frente a unordered_map (sin orden) y list (sin acceso aleatorio).
>
> Repasar: `std::vector, std::queue, std::map, complejidad de contenedores STL`

### ⚠️ Pregunta 8 — Regla de cero/cinco: destructor suprime moves, marcar noexcept

Dada la siguiente clase que gestiona memoria dinámica manualmente:

```cpp
class Buffer {
public:
    Buffer(size_t n) : data_(new int[n]), size_(n) {}
    ~Buffer() { delete[] data_; }
private:
    int* data_;
    size_t size_;
};
```

¿Cuáles de las siguientes afirmaciones son correctas respecto a esta clase y a la regla de cero/tres/cinco en C++ moderno?

- [x] **Marcar el constructor de movimiento como noexcept permite que contenedores como std::vector lo usen durante una reubicación (realloc) en lugar de copiar, ya que si no puede lanzar excepciones el contenedor recurre a copiar para mantener la garantía fuerte de excepciones.** — _correcta_: Correcto: std::vector usa std::move_if_noexcept internamente; si el move no está garantizado noexcept, prefiere copiar para no dejar el vector en estado inconsistente ante una excepción a mitad de la reubicación.
- [ ] **La clase ya cumple la regla de cero tal como está escrita, porque delega toda la gestión de memoria en su propio destructor y no necesita declarar más miembros especiales.** — _incorrecta_: Incorrecto: la regla de cero consiste en NO gestionar recursos crudos manualmente, delegando en wrappers RAII como std::unique_ptr o std::vector; aquí se gestiona memoria a mano, lo que obliga a seguir la regla de cinco (o tres), no la de cero.
- [ ] **El compilador sigue generando implícitamente el constructor de copia y el operador de asignación por copia (aunque su generación esté marcada como obsoleta en este caso), realizando una copia superficial de data_ que puede causar doble delete.** — _correcta_: Correcto: la copia implícita sigue existiendo por compatibilidad (deprecated), pero copia el puntero, no el buffer, provocando un double free o use-after-free al destruirse ambos objetos.
- [ ] **Al declarar un destructor propio, el compilador suprime la generación implícita del constructor de movimiento y del operador de asignación por movimiento; por tanto, un std::vector<Buffer> recurrirá a copias en lugar de moverse.** — _correcta_: Correcto: desde C++11, declarar cualquiera de destructor, constructor de copia o asignación de copia inhibe la generación implícita de los miembros de movimiento.

> Cuando una clase gestiona un recurso manualmente y declara un destructor, pierde los movimientos implícitos y solo conserva copias potencialmente peligrosas. La solución idiomática es aplicar la regla de cero delegando en tipos RAII (unique_ptr, vector), o si se necesita gestión manual, declarar explícitamente los cinco miembros especiales, marcando move como noexcept para habilitar optimizaciones en contenedores STL.
>
> Repasar: `Regla de cero/cinco, std::move_if_noexcept, RAII`

### ✅ Pregunta 9 — Lambdas: captura por referencia y ciclo de vida

Analiza este código:
```cpp
std::function<int()> hacer_contador() {
    int contador = 0;
    auto incrementar = [&contador]() {
        return ++contador;
    };
    return incrementar;
}

int main() {
    auto f = hacer_contador();
    std::cout << f() << std::endl;
}
```
¿Qué ocurre al ejecutar este programa?

- [x] **Comportamiento indefinido: contador es una variable local de hacer_contador() que deja de existir al retornar la función, y la lambda capturó una referencia a ella, no una copia.** — _correcta_: Correcto: al capturar por referencia ([&contador]), la lambda solo guarda un alias a la variable original. Cuando la función termina, contador sale de ámbito y su almacenamiento se libera, dejando una referencia colgante que se usa en f().
- [ ] **El código no compila, porque el estándar prohíbe devolver una lambda que capture variables locales por referencia.** — _incorrecta_: Incorrecto: el código compila perfectamente. El compilador no impide capturar por referencia variables locales ni devolver la lambda envuelta en std::function; el problema es un fallo en tiempo de ejecución (UB), no de compilación.
- [ ] **Imprime 0, porque contador se reinicia a su valor por defecto justo antes de que la lambda sea invocada desde main().** — _incorrecta_: Incorrecto: no hay ningún mecanismo que 'reinicie' contador; simplemente su almacenamiento ya no es válido, por lo que el resultado no está garantizado (podría imprimir cualquier valor, incluido 0, pero no por esta razón).
- [ ] **El programa funciona correctamente porque std::function extiende automáticamente la vida útil de las variables capturadas por referencia, igual que hace una captura por valor.** — _incorrecta_: Incorrecto: std::function solo gestiona el ciclo de vida del objeto invocable (la lambda en sí), no el de las variables externas referenciadas dentro de ella; no existe extensión automática de vida útil para capturas por referencia.
- [ ] **Imprime 1, porque la lambda mantiene su propia copia interna de contador gracias a la captura por referencia.** — _incorrecta_: Incorrecto: es justo lo contrario. La captura por referencia ([&contador]) no copia la variable, sino que almacena un puntero/alias a ella; si se quisiera una copia independiente habría que capturar por valor ([contador]).

> Este es un error clásico con lambdas: capturar por referencia ([&]) variables locales que no sobrevivirán al ámbito de la función crea referencias colgantes, un problema distinto de la captura por valor ([=] o [var]), que copia el estado en el momento de creación de la lambda y por tanto es segura frente a este escenario.
>
> Repasar: `captura de lambdas por referencia vs. por valor, dangling reference, ciclo de vida de closures`

### ⚠️ Pregunta 10 — Algoritmos STL: complejidad, overflow acumulativo y erase-remove idiom

Dado el siguiente código:
```cpp
std::vector<int> v = {1,2,3,4,5,6,7,8,9,10};
auto it = std::remove(v.begin(), v.end(), 5);
v.erase(it, v.end());
```
¿Cuáles de las siguientes afirmaciones sobre este código y los algoritmos de la STL son correctas? (selecciona todas las que apliquen)

- [x] **std::remove no elimina realmente los elementos del contenedor; solo reordena el rango moviendo los elementos que no coinciden hacia el principio y devuelve un iterador al nuevo 'final lógico'. Por eso es necesario llamar a erase() para reducir el tamaño real del vector.** — _correcta_: Correcto: std::remove opera sobre un rango [first, last) y no conoce el contenedor, así que no puede cambiar su tamaño; el idiom erase-remove combina ambos pasos para eliminar de verdad los elementos.
- [ ] **std::sort tiene complejidad media O(n log n), mientras que std::stable_sort puede degradarse a O(n log² n) si no dispone de memoria auxiliar suficiente para hacer la mezcla.** — _correcta_: Correcto: el estándar garantiza O(n log n) para std::sort en el caso medio, y para std::stable_sort garantiza O(n log n) si hay memoria extra disponible, o O(n log² n) en el peor caso sin memoria auxiliar.
- [ ] **std::accumulate(v.begin(), v.end(), 0) sobre un vector<int> nunca puede desbordar, porque el tipo del acumulador se ajusta automáticamente al tipo de mayor precisión necesario según los valores sumados.** — _incorrecta_: Incorrecto: el tipo del acumulador se deduce del valor inicial (0 es int), no de los elementos sumados. Si la suma supera el rango de int, se produce overflow (comportamiento indefinido en tipos con signo); hay que pasar un valor inicial de tipo más ancho, p. ej. 0LL.
- [ ] **El idiom erase-remove es igual de eficiente en un std::list que en un std::vector, porque ambos contenedores ofrecen iteradores de acceso aleatorio compatibles con std::remove.** — _incorrecta_: Incorrecto: std::list solo ofrece iteradores bidireccionales, no de acceso aleatorio, y además list::erase de un solo elemento es O(1) frente al O(n) de vector; por eso se recomienda usar list::remove, más eficiente que el idiom genérico.
- [ ] **std::find tiene complejidad O(n) porque realiza una búsqueda lineal sin asumir que el rango esté ordenado.** — _correcta_: Correcto: std::find recorre secuencialmente el rango comparando cada elemento, por lo que su coste es lineal en el peor caso, a diferencia de std::binary_search que exige un rango ordenado.

> La pregunta combina tres subtemas clásicos de algoritmos STL: el funcionamiento real de std::remove (no borra, reordena), las garantías de complejidad de las funciones de ordenación, y el riesgo de overflow silencioso en std::accumulate cuando el valor inicial fija un tipo demasiado estrecho.
>
> Repasar: `erase-remove idiom, complejidad de algoritmos STL, std::accumulate`
