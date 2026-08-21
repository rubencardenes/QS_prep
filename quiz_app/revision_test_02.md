# Resultado del test — C++ moderno (C++11/14/17/20)

- Fecha: 2026-08-04 11:43
- Nivel: junior
- Puntuación: **53%** (2.67/5 puntos)
- Preguntas perfectas: 2/5

## Revisión pregunta a pregunta

### ✅ Pregunta 1 — Move constructor sin noexcept desactiva optimizaciones de vector

Considera la siguiente clase y su uso dentro de un `std::vector`:

```cpp
class Buffer {
public:
    Buffer() = default;
    Buffer(Buffer&& other) { /* mueve recursos */ }
    Buffer(const Buffer& other) { /* copia recursos */ }
};

std::vector<Buffer> v;
v.push_back(Buffer());
v.push_back(Buffer()); // provoca una reasignación (reallocation)
```

El constructor de movimiento de `Buffer` **no** está marcado como `noexcept`. ¿Qué ocurre cuando `std::vector` necesita reubicar sus elementos en un nuevo bloque de memoria?

- [ ] **std::vector usará el move constructor igualmente, ya que noexcept es solo una anotación informativa para el compilador sin efecto en el comportamiento en tiempo de ejecución.** — _incorrecta_: Incorrecto. noexcept sí afecta el comportamiento en tiempo de ejecución en este caso concreto: cambia la decisión entre copiar o mover durante la reubicación de un vector.
- [x] **std::vector usará el constructor de copia en lugar del de movimiento durante la reubicación, porque no puede garantizar la fuerte garantía de excepción si el move constructor pudiera lanzar a mitad de la operación.** — _correcta_: Correcto. Desde C++11, `std::vector` comprueba en tiempo de compilación (vía `std::move_if_noexcept`) si el move constructor es `noexcept`; si no lo es y existe constructor de copia, prefiere copiar para poder revertir la operación si algo falla.
- [ ] **El comportamiento es indefinido, porque el estándar exige que todo tipo almacenado en un contenedor tenga un move constructor noexcept.** — _incorrecta_: Incorrecto. No hay comportamiento indefinido ni ese requisito general; el estándar solo condiciona la elección entre mover y copiar en operaciones como la reubicación de vector.
- [ ] **El programa no compila porque std::vector exige que los move constructors de los elementos que almacena sean noexcept.** — _incorrecta_: Incorrecto. El código compila perfectamente; simplemente el vector opta por copiar en lugar de mover en las reubicaciones, sin que esto sea un error de compilación.

> std::vector ofrece la garantía fuerte de excepción en operaciones como push_back que provocan reasignación: si un move constructor pudiera lanzar una excepción a mitad del proceso, el vector quedaría en un estado corrupto e irreversible. Por eso, si el move constructor no es noexcept, el vector recurre al constructor de copia (que sí puede revertirse) en lugar del de movimiento, perdiendo así la optimización de rendimiento que se buscaba con la semántica de movimiento.
>
> Repasar: `std::move_if_noexcept, garantía fuerte de excepción, noexcept en move constructors`

### ⚠️ Pregunta 2 — Captura por referencia en lambdas y dangling references

Analiza el siguiente código:

```cpp
#include <functional>
#include <iostream>

std::function<int()> crear_contador() {
    int contador = 0;
    auto incrementar = [&contador]() {
        return ++contador;
    };
    return incrementar;
}

int main() {
    auto f = crear_contador();
    std::cout << f() << std::endl;
}
```

¿Cuáles de las siguientes afirmaciones son correctas? (selecciona todas las que apliquen)

- [x] **Llamar a `f()` produce comportamiento indefinido, ya que se accede a memoria de una variable que ya no existe en la pila.** — _correcta_: Correcto. Acceder a `contador` a través de la referencia colgante es un uso de memoria inválida, lo cual es comportamiento indefinido (puede parecer que funciona, pero no está garantizado).
- [ ] **La lambda captura `contador` por referencia, y esa referencia queda colgante al salir de `crear_contador`, porque `contador` es una variable local que se destruye al terminar la función.** — _correcta_: Correcto. `[&contador]` captura la variable por referencia; al retornar la lambda, la variable de pila `contador` ya no existe, dejando una referencia colgante.
- [ ] **El problema se evitaría capturando `contador` por valor, es decir, usando `[contador]` en lugar de `[&contador]`.** — _correcta_: Correcto. Capturar por valor copia `contador` dentro de la lambda, de modo que su ciclo de vida ya no depende de la variable local original (aunque cambia la semántica: cada llamada a `crear_contador` daría una copia independiente).
- [ ] **El compilador detecta el error y produce un fallo de compilación por capturar una variable local por referencia en una lambda que se retorna.** — _incorrecta_: Incorrecto. El compilador no puede detectar este patrón en general; el código compila sin errores y el problema solo se manifiesta en tiempo de ejecución como comportamiento indefinido.
- [ ] **El uso de std::function como tipo de retorno evita este problema, porque extiende automáticamente la vida de las variables capturadas por referencia.** — _incorrecta_: Incorrecto. std::function solo envuelve el objeto invocable (la lambda); no extiende la vida de las variables externas capturadas por referencia.

> Un error muy común en C++ moderno es capturar variables locales por referencia en una lambda que sobrevive al ámbito en el que fue creada, típicamente al devolverla o guardarla para uso posterior. Esto genera una referencia colgante (dangling reference) y comportamiento indefinido al invocar la lambda. La solución habitual es capturar por valor o gestionar la vida útil de la variable con mecanismos como punteros compartidos.
>
> Repasar: `capturas de lambda, dangling reference, ciclo de vida de variables automáticas`

### ❌ Pregunta 3 — Optional: reemplazando punteros nulos y valores sentinela

Analiza esta función, refactorizada para usar `std::optional` en lugar de un valor sentinela como -1:
```cpp
std::optional<size_t> buscarIndice(const std::vector<int>& v, int valor) {
    for (size_t i = 0; i < v.size(); ++i) {
        if (v[i] == valor) return i;
    }
    return std::nullopt;
}
```
¿Cuál de las siguientes afirmaciones es correcta?

- [x] **Acceder a un std::optional vacío mediante operator* o value() sin comprobar has_value() está bien definido y simplemente devuelve un valor por defecto de forma silenciosa.** — _incorrecta_: Incorrecto. operator* sobre un optional vacío es comportamiento indefinido, y value() lanza una excepción std::bad_optional_access; ninguno de los dos devuelve un valor por defecto en silencio.
- [ ] **std::optional<size_t> reserva memoria dinámicamente para almacenar el valor cuando está presente, de forma similar a un std::unique_ptr<size_t>.** — _incorrecta_: Incorrecto. std::optional almacena el valor 'en línea' (junto con un flag de presencia), típicamente en la pila, sin ninguna asignación dinámica de memoria.
- [ ] **std::optional<size_t> permite distinguir de forma segura "no encontrado" de "encontrado en el índice 0", algo problemático si se usara -1 como sentinela con un tipo sin signo como size_t.** — _correcta_: Correcto. Con size_t (sin signo), -1 se convierte en un valor enorme en lugar de negativo, lo que es una fuente clásica de bugs; std::optional evita por completo esa ambigüedad al separar el estado 'vacío' del valor.
- [ ] **El método value_or(valorPorDefecto) de std::optional lanza una excepción si el optional está vacío, en lugar de devolver ese valor por defecto.** — _incorrecta_: Incorrecto. value_or() está pensado precisamente para el caso vacío: devuelve el valor por defecto proporcionado sin lanzar ninguna excepción; es value() el que lanza si está vacío.

> std::optional<T> (desde C++17) sustituye a los valores sentinela (-1, 0, punteros nulos ad hoc) para representar la ausencia de un valor, evitando ambigüedades con tipos sin signo y aportando comprobación explícita (has_value(), value(), value_or()) sin coste de asignación dinámica.
>
> Repasar: `std::optional (C++17) y std::nullopt`

### ⚠️ Pregunta 4 — Buffer contiguo versus vector de vectores: impacto en caché

Se compara el rendimiento de recorrer una matriz 2D representada como `std::vector<std::vector<int>>` frente a un único `std::vector<int>` contiguo que almacena los mismos datos en orden fila-mayor (índice = fila * numColumnas + columna). ¿Cuáles de las siguientes afirmaciones son correctas?

- [ ] **Con std::vector<std::vector<int>>, acceder a una fila implica seguir un puntero adicional a un bloque de memoria potencialmente disperso, lo que puede aumentar los fallos de caché.** — _correcta_: Correcto. Cada `v[i]` requiere primero leer el puntero al vector interno y después acceder a su buffer, añadiendo una indirección que puede degradar la localidad.
- [x] **Recorrer std::vector<std::vector<int>> por columnas en lugar de por filas suele ser aún más lento por la combinación de mala localidad y saltos de puntero entre vectores no contiguos.** — _correcta_: Correcto. Al recorrer por columnas se salta en cada iteración entre distintos vectores internos dispersos en memoria, empeorando una localidad que ya era peor que la del buffer contiguo.
- [ ] **std::vector<std::vector<int>> garantiza que todas las filas quedan almacenadas en un único bloque contiguo de memoria, igual que el buffer plano.** — _incorrecta_: Incorrecto. El vector externo solo almacena punteros a los vectores internos; cada fila reserva su propio bloque de memoria de forma independiente, sin garantía de contigüidad entre filas.
- [x] **Usar un buffer contiguo para representar la matriz obliga a conocer el número de columnas en tiempo de compilación.** — _incorrecta_: Incorrecto. El número de columnas puede ser una variable en tiempo de ejecución; el acceso se calcula dinámicamente como fila * numColumnas + columna.
- [x] **El buffer contiguo permite que la caché de la CPU precargue (prefetch) datos adyacentes de forma eficiente al recorrer filas, mejorando la localidad espacial.** — _correcta_: Correcto. Al estar todos los elementos en un único bloque contiguo, el acceso secuencial favorece la localidad espacial y el prefetching hardware, reduciendo fallos de caché.

> Un std::vector<std::vector<int>> añade una capa de indirección por fila y no ofrece contigüidad entre filas, lo que provoca más fallos de caché y peor aprovechamiento del prefetcher que un buffer plano contiguo, donde toda la matriz vive en un único bloque de memoria y el acceso se indexa manualmente.
>
> Repasar: `localidad de caché y std::vector contiguo`

### ✅ Pregunta 5 — Acumulación en uint8_t versus int: overflow silencioso

Dado el siguiente código, que suma los elementos de un vector de bytes:

```cpp
#include <cstdint>
#include <vector>

uint8_t sumar(const std::vector<uint8_t>& datos) {
    uint8_t total = 0;
    for (uint8_t valor : datos) {
        total += valor;
    }
    return total;
}
```

Se llama con `datos = {200, 100, 50}`. ¿Cuáles de las siguientes afirmaciones son correctas? (selecciona todas las que apliquen)

- [ ] **Este código produce un error de compilación porque el operador `+=` no está definido para el tipo uint8_t.** — _incorrecta_: Incorrecto. uint8_t admite operaciones aritméticas con normalidad (se promociona internamente durante el cálculo); el código compila sin problemas, el fallo es de lógica en tiempo de ejecución, no de compilación.
- [ ] **El comportamiento es indefinido, igual que el desbordamiento de un entero con signo como int, porque el estándar de C++ trata igual el overflow con y sin signo.** — _incorrecta_: Incorrecto. El overflow de enteros sin signo (como uint8_t) está bien definido por el estándar como aritmética módulo 2^n; es el overflow de enteros con signo (como int) el que constituye comportamiento indefinido.
- [x] **La suma real (350) desborda el rango de uint8_t (0-255), y el resultado se trunca silenciosamente mediante aritmética módulo 256, sin lanzar ninguna advertencia ni excepción.** — _correcta_: Correcto. 350 mod 256 = 94; el desbordamiento de un tipo entero sin signo simplemente 'da la vuelta' (wraparound), sin ningún aviso en tiempo de ejecución.
- [x] **Usar uint8_t como tipo acumulador es una fuente común de bugs sutiles en bucles de suma; es preferible usar un tipo con más rango (por ejemplo int o uint32_t) para acumular y convertir al final si es necesario.** — _correcta_: Correcto. Esta es una buena práctica habitual: acumular en un tipo con margen suficiente evita overflow silencioso durante el bucle, incluso si el resultado final se necesita en un tipo más pequeño.
- [x] **Declarar `total` como int y hacer `static_cast<uint8_t>(total)` solo al final evitaría el truncamiento intermedio, aunque el valor final seguiría fuera de rango si la suma total supera 255.** — _correcta_: Correcto. Acumular en un tipo con más rango evita truncamientos parciales en cada suma; el cast final solo trunca una vez, aunque sigue perdiendo información si el total supera 255.

> Acumular en tipos enteros pequeños como uint8_t es una fuente frecuente de bugs difíciles de detectar, porque el desbordamiento de enteros sin signo está bien definido (wraparound módulo 2^n) en lugar de producir un error o comportamiento indefinido, por lo que el programa sigue ejecutándose con datos incorrectos sin ningún aviso. La práctica recomendada es usar un tipo acumulador con rango suficiente (int, unsigned, uint32_t, etc.) y convertir al tipo final solo si realmente hace falta.
>
> Repasar: `overflow de enteros sin signo, promoción de enteros, elección de tipo acumulador`
