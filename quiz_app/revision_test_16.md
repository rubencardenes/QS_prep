# Resultado del test — C++ moderno (C++11/14/17/20)

- Fecha: 2026-09-14 11:17
- Nivel: junior
- Puntuación: **62%** (6.17/10 puntos)
- Preguntas perfectas: 4/10

## Revisión pregunta a pregunta

### ⚠️ Pregunta 1 — Complejidad de algoritmos estándar

Para un `std::vector<int>` con `n` elementos, ¿qué afirmaciones sobre los algoritmos estándar son correctas?

- [ ] **`std::binary_search` puede usarse correctamente sobre cualquier vector, aunque sus elementos no estén ordenados.** — _incorrecta_: El rango debe estar ordenado conforme al mismo criterio de comparación; de lo contrario, no se cumplen las precondiciones del algoritmo.
- [ ] **`std::sort` tiene complejidad O(n) porque el vector ofrece acceso aleatorio.** — _incorrecta_: El acceso aleatorio permite aplicar algoritmos eficientes, pero no reduce la ordenación general a tiempo lineal. `std::sort` realiza O(n log n) comparaciones.
- [x] **`std::binary_search` tiene complejidad O(log n) sobre un vector ordenado.** — _correcta_: Con iteradores de acceso aleatorio, como los de `std::vector`, la búsqueda reduce el intervalo aproximadamente a la mitad en cada paso.
- [x] **`std::find` tiene complejidad lineal O(n) en el peor caso.** — _correcta_: Puede ser necesario examinar los `n` elementos antes de encontrar el valor o determinar que no existe.
- [ ] **`std::count` tiene complejidad lineal O(n).** — _correcta_: Debe recorrer todo el rango para contar todas las apariciones, incluso si encuentra coincidencias al principio.

> La complejidad depende tanto del algoritmo como de la categoría de sus iteradores y de sus precondiciones. En un vector, `std::find` y `std::count` recorren linealmente el rango, `std::binary_search` requiere orden y opera en O(log n), y `std::sort` usa O(n log n) comparaciones.
>
> Repasar: `Complejidad de std::find, std::count, std::binary_search y std::sort`

### ⚠️ Pregunta 2 — Deducción de tipos en plantillas de función

Dado el siguiente código C++17, ¿qué afirmaciones son correctas?

```cpp
template <typename T>
void procesar(T valor) {}

const int numero = 42;
procesar(numero);
procesar(3.5);
```

- [x] **En `procesar(3.5)`, `T` se deduce como `double`.** — _correcta_: El literal `3.5` tiene tipo `double`, por lo que ese es el tipo deducido para `T`.
- [ ] **Es obligatorio escribir `procesar<int>(numero)` porque las plantillas no deducen tipos a partir de argumentos.** — _incorrecta_: Las plantillas de función normalmente pueden deducir sus parámetros de tipo a partir de los argumentos de la llamada.
- [x] **Las dos llamadas generan instanciaciones de la plantilla con tipos distintos.** — _correcta_: El compilador necesita una especialización con `T = int` y otra con `T = double`.
- [x] **En `procesar(numero)`, `T` se deduce como `const int`.** — _incorrecta_: El `const` de nivel superior no se conserva cuando el parámetro de la plantilla se recibe por valor.
- [ ] **En `procesar(numero)`, `T` se deduce como `int`.** — _correcta_: Al pasar el argumento por valor, se eliminan los calificadores `const` de nivel superior durante la deducción. Por tanto, `T` es `int`.

> En una plantilla de función, el compilador deduce `T` a partir del tipo del argumento. Para un parámetro recibido por valor se eliminan referencias y calificadores de nivel superior como `const`; cada tipo deducido distinto puede producir una instanciación diferente.
>
> Repasar: `Deducción de argumentos de plantilla`

### ❌ Pregunta 3 — std::atomic y modelo de memoria

Considera un contador compartido declarado como `std::atomic<int> contador{0};`. ¿Qué afirmaciones son correctas?

- [ ] **Acceder al contador únicamente mediante sus operaciones atómicas evita una carrera de datos sobre ese objeto.** — _correcta_: Las operaciones atómicas concurrentes sobre el mismo objeto están definidas y no producen una carrera de datos.
- [ ] **Si no se especifica un orden de memoria, las operaciones atómicas utilizan `std::memory_order_seq_cst` por defecto.** — _correcta_: `std::memory_order_seq_cst` es el orden predeterminado y proporciona el modelo más sencillo y restrictivo de ordenación entre operaciones atómicas.
- [x] **El uso de `std::atomic` convierte automáticamente una secuencia de varias operaciones atómicas en una transacción indivisible.** — _incorrecta_: Cada operación puede ser atómica individualmente, pero una secuencia de varias operaciones puede intercalarse con operaciones de otros hilos.
- [ ] **Declarar el contador como `volatile int` ofrecería las mismas garantías de sincronización entre hilos.** — _incorrecta_: `volatile` no proporciona atomicidad ni sincronización entre hilos; se usa para otros tipos de accesos observables, como ciertos dispositivos de memoria mapeada.
- [x] **`contador.fetch_add(1)` incrementa el contador mediante una operación atómica.** — _correcta_: `fetch_add` realiza la lectura, modificación y escritura como una única operación atómica sobre el contador.

> `std::atomic`, disponible desde C++11, permite realizar accesos indivisibles y evita carreras de datos cuando el objeto se utiliza correctamente. El orden predeterminado es `std::memory_order_seq_cst`, pero la atomicidad de cada operación no convierte varias operaciones en una transacción conjunta.
>
> Repasar: `std::atomic, fetch_add y std::memory_order_seq_cst`

### ✅ Pregunta 4 — Localidad de caché y coste de asignaciones de memoria

Se recorren secuencialmente un `std::vector<int>` y un `std::list<int>` con el mismo número de elementos para calcular una suma. En condiciones habituales, ¿cuál es la razón principal por la que el recorrido del `std::vector` suele ser más rápido?

- [ ] **Cada acceso a un elemento de `std::list` requiere una nueva asignación dinámica durante el recorrido.** — _incorrecta_: Los nodos ya fueron asignados al construir la lista. El recorrido sigue punteros, pero no necesita asignar memoria de nuevo en cada acceso.
- [x] **Los elementos del `std::vector` se almacenan de forma contigua, lo que favorece la localidad de caché y la precarga de memoria.** — _correcta_: La disposición contigua permite aprovechar mejor cada línea de caché y facilita que el procesador anticipe los siguientes accesos.
- [ ] **La suma de enteros está implementada en tiempo constante para `std::vector`, pero en tiempo lineal para `std::list`.** — _incorrecta_: Recorrer y sumar todos los elementos tiene complejidad lineal en ambos contenedores. La diferencia habitual procede de factores de rendimiento constantes.
- [ ] **`std::vector` almacena siempre sus elementos en la pila, mientras que `std::list` los almacena en el heap.** — _incorrecta_: El almacenamiento dinámico de un `std::vector` normalmente también reside en memoria dinámica; la ventaja relevante es su contigüidad, no que use la pila.

> `std::vector` mantiene sus elementos contiguos, mientras que `std::list` usa nodos separados enlazados mediante punteros. Aunque ambos recorridos son O(n), el vector suele aprovechar mejor la caché y evita la indirección y el coste de almacenamiento asociado a cada nodo.
>
> Repasar: `localidad espacial, líneas de caché, std::vector y std::list`

### ✅ Pregunta 5 — Invalidación de iteradores en std::vector

¿Cuál es la afirmación correcta sobre los iteradores de `std::vector` después de ejecutar `push_back`?

- [x] **Si `push_back` provoca una reasignación de memoria, se invalidan todos los iteradores, punteros y referencias a elementos del vector.** — _correcta_: La reasignación mueve los elementos a un nuevo bloque contiguo de memoria, por lo que los accesos que apuntaban al almacenamiento anterior dejan de ser válidos.
- [ ] **Una reasignación invalida únicamente el iterador `end()`, pero conserva los iteradores a elementos existentes.** — _incorrecta_: Cuando hay reasignación, todos los elementos cambian potencialmente de dirección, así que se invalidan todos los iteradores y referencias.
- [ ] **Llamar previamente a `reserve` garantiza que ningún `push_back` futuro invalidará iteradores, sin importar cuántos elementos se añadan.** — _incorrecta_: `reserve` evita reasignaciones solo mientras el tamaño resultante no supere la capacidad reservada. Al excederla puede producirse una nueva reasignación.
- [ ] **Los iteradores nunca se invalidan porque `std::vector` mantiene sus elementos en memoria contigua.** — _incorrecta_: Precisamente por usar un bloque contiguo, el vector puede tener que trasladar todos sus elementos cuando aumenta su capacidad.

> `std::vector` almacena sus elementos de forma contigua. Si una inserción supera su capacidad, debe reasignar el almacenamiento e invalida todos los iteradores, punteros y referencias; si no hay reasignación, `push_back` invalida `end()` pero conserva los accesos a los elementos anteriores.
>
> Repasar: `std::vector::push_back e invalidación de iteradores`

### ⚠️ Pregunta 6 — RAII y liberación automática de recursos

Observa el siguiente código:

```cpp
class Archivo {
public:
    Archivo(const char* ruta) : f(std::fopen(ruta, "r")) {}
    ~Archivo() {
        if (f) std::fclose(f);
    }
private:
    std::FILE* f;
};
```

¿Qué afirmaciones describen correctamente el uso de RAII? Selecciona todas las correctas.

- [x] **El archivo se cierra automáticamente cuando un objeto `Archivo` sale de su ámbito.** — _correcta_: El destructor se ejecuta al finalizar la vida del objeto y libera el recurso mediante `std::fclose`.
- [ ] **El archivo también se cierra durante el desenrollado de la pila si se lanza una excepción después de construir el objeto.** — _correcta_: Los destructores de los objetos automáticos ya construidos se ejecutan durante el desenrollado de la pila.
- [ ] **RAII exige llamar explícitamente al destructor antes de abandonar cada función.** — _incorrecta_: La destrucción de los objetos automáticos ocurre de forma automática; llamar explícitamente al destructor normalmente sería incorrecto.
- [ ] **El constructor garantiza que `f` siempre contiene un archivo abierto válido.** — _incorrecta_: `std::fopen` puede fallar y devolver un puntero nulo. La clase tendría que comprobarlo y decidir cómo comunicar el error.

> RAII vincula la vida de un recurso con la de un objeto: el constructor adquiere o inicializa el recurso y el destructor lo libera. Esto permite una liberación determinista incluso cuando el flujo termina mediante una excepción.
>
> Repasar: `RAII, destructores y desenrollado de pila`

### ❌ Pregunta 7 — Evaluación constexpr en tiempo de compilación

Suponiendo que n solo se conoce durante la ejecución, ¿cuál de las siguientes declaraciones válidas exige que la llamada a cuadrado se evalúe como una expresión constante en tiempo de compilación?

```cpp
constexpr int cuadrado(int x) {
    return x * x;
}

int n;
std::cin >> n;
```

- [ ] **const int resultado = cuadrado(5);** — _incorrecta_: const impide modificar resultado después de inicializarlo, pero no exige por sí solo una evaluación en tiempo de compilación.
- [x] **constexpr int resultado = cuadrado(5);** — _correcta_: Un objeto constexpr debe inicializarse con una expresión constante. Como 5 es constante y cuadrado puede evaluarse en compilación, esta declaración lo exige.
- [ ] **static const int resultado = cuadrado(n);** — _incorrecta_: static controla la duración de almacenamiento y const impide modificaciones posteriores, pero ninguna de las dos exige que n sea conocido en compilación.
- [x] **int resultado = cuadrado(5);** — _incorrecta_: El compilador puede optimizar esta llamada y calcularla anticipadamente, pero el lenguaje no obliga a que se evalúe en tiempo de compilación.
- [ ] **constexpr int resultado = cuadrado(n);** — _incorrecta_: Esta declaración no es válida porque n solo se conoce en ejecución y, por tanto, cuadrado(n) no es una expresión constante.

> Desde C++11, una función constexpr puede participar en expresiones constantes cuando recibe argumentos adecuados. La función también puede ejecutarse en tiempo de ejecución; es el contexto constexpr del resultado el que exige la evaluación constante.
>
> Repasar: `constexpr y expresiones constantes`

### ✅ Pregunta 8 — Propiedad con unique_ptr, shared_ptr y weak_ptr

¿Qué afirmaciones sobre `std::unique_ptr`, `std::shared_ptr` y `std::weak_ptr` son correctas? Selecciona todas las correctas.

- [ ] **Dos objetos que se poseen mutuamente mediante `std::shared_ptr` siempre se liberan automáticamente.** — _incorrecta_: La propiedad circular puede impedir que los recuentos lleguen a cero. Uno de los enlaces suele modelarse con `std::weak_ptr` para romper el ciclo.
- [ ] **`std::weak_ptr` permite desreferenciar directamente el objeto con el operador `*`.** — _incorrecta_: `std::weak_ptr` no ofrece desreferenciación directa porque el objeto podría haber sido destruido. Primero debe obtenerse temporalmente un `std::shared_ptr` mediante `lock()`.
- [x] **`std::weak_ptr` observa un objeto administrado por `std::shared_ptr` sin incrementar el recuento de propietarios.** — _correcta_: `std::weak_ptr` no posee el objeto. Para intentar acceder a él se usa normalmente `lock()`, que devuelve un `std::shared_ptr`.
- [x] **`std::shared_ptr` mantiene un recuento de propietarios y destruye el objeto cuando desaparece el último propietario compartido.** — _correcta_: Cada copia propietaria participa en el recuento de referencias; el objeto gestionado se destruye cuando ese recuento llega a cero.
- [x] **`std::unique_ptr` representa propiedad exclusiva y puede transferirse mediante movimiento.** — _correcta_: `std::unique_ptr` no se puede copiar, pero sí mover para transferir la propiedad del objeto gestionado.

> Los punteros inteligentes de C++11 expresan distintas formas de propiedad: `std::unique_ptr` para propiedad exclusiva, `std::shared_ptr` para propiedad compartida y `std::weak_ptr` para observación no propietaria. Elegir el tipo adecuado evita fugas, dobles liberaciones y ciclos de referencias.
>
> Repasar: `unique_ptr, shared_ptr, weak_ptr y ciclos de propiedad`

### ✅ Pregunta 9 — Semántica de movimiento y referencias rvalue

Dado el código siguiente, ¿qué afirmación es correcta?

```cpp
std::string origen = "datos";
std::string destino = std::move(origen);
```

- [x] **`std::move` convierte `origen` en una expresión rvalue y permite que `destino` use el constructor de movimiento.** — _correcta_: `std::move` realiza una conversión a una referencia rvalue; esto habilita la selección del constructor de movimiento cuando está disponible.
- [ ] **Después del movimiento, acceder a `origen` produce siempre comportamiento indefinido.** — _incorrecta_: El objeto movido permanece válido, aunque su estado concreto normalmente no está especificado. Puede destruirse o recibir un nuevo valor de forma segura.
- [ ] **Después de la asignación, el estándar garantiza que `origen.empty()` sea verdadero.** — _incorrecta_: Un objeto movido queda en un estado válido pero no especificado; no se garantiza que la cadena quede vacía.
- [ ] **`std::move` mueve por sí misma los caracteres de `origen` a `destino`.** — _incorrecta_: `std::move` no transfiere recursos directamente. La transferencia, si ocurre, la implementa el constructor de movimiento de `std::string`.

> Desde C++11, las referencias rvalue y las operaciones de movimiento permiten transferir recursos evitando copias innecesarias. `std::move` es esencialmente una conversión de categoría de valor y no garantiza por sí sola que se realice un movimiento.
>
> Repasar: `std::move, referencias rvalue y estado válido no especificado`

### ⚠️ Pregunta 10 — Capturas por valor y referencia en lambdas

Tras ejecutar este código, ¿qué afirmaciones son correctas? Selecciona todas las aplicables.

```cpp
int x = 2;
int y = 3;

auto f = [x, &y]() mutable {
    ++x;
    ++y;
    return x + y;
};

int r = f();
```

- [ ] **La palabra clave mutable permite modificar directamente la variable x original.** — _incorrecta_: mutable permite modificar la copia de x almacenada en el cierre. No cambia una captura por valor en una captura por referencia.
- [ ] **El valor de r es 7.** — _correcta_: La copia capturada de x pasa de 2 a 3 y el objeto y referenciado pasa de 3 a 4. Por tanto, la lambda devuelve 3 + 4.
- [x] **El valor de x fuera de la lambda sigue siendo 2.** — _correcta_: x se captura por valor, así que el cierre almacena y modifica una copia. La variable original no cambia.
- [ ] **Sin mutable, la lambda podría incrementar su copia capturada de x de la misma manera.** — _incorrecta_: De forma predeterminada, el operador de llamada del cierre es const y las capturas por valor no pueden modificarse. mutable elimina esa restricción.
- [x] **El valor de y fuera de la lambda pasa a ser 4.** — _correcta_: y se captura por referencia mediante &y. Incrementarla dentro de la lambda modifica la variable original.

> Una lambda crea un objeto de cierre que almacena sus capturas. Las capturas por valor son copias independientes, mientras que las capturas por referencia permiten modificar el objeto original; mutable habilita la modificación de las copias capturadas.
>
> Repasar: `capturas de lambda, objeto de cierre y mutable`
