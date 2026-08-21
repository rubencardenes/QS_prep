# Curso de refuerzo — Ingeniería de software en Python

Basado en tus tests 05 y 12 (47% en ambos). Acertaste de pleno el GIL/concurrencia y el profiling con cProfile (tottime vs cumtime) — esos dos los repaso rápido al final, a modo de consolidación. El resto de conceptos —generadores, descriptores, pydantic, empaquetado/SemVer, closures, context managers y garbage collection— tuvieron fallos parciales, así que vamos uno a uno con calma.

## Índice

1. Generadores e iteradores
2. Protocolo de descriptores
3. Type hints vs. pydantic: anotaciones vs. validación real
4. Profiling y numpy: eligiendo la herramienta correcta
5. Empaquetado y versionado semántico (SemVer)
6. Closures y el bug de late binding
7. Context managers y `contextlib`
8. Garbage collection, ciclos de referencia y `weakref`
9. Repaso rápido: GIL, threading vs. multiprocessing
10. Repaso rápido: cProfile, tottime vs. cumtime

---

## 1. Generadores e iteradores

### ¿Qué es un generador?

Una función que contiene `yield` en su cuerpo no es una función normal: al llamarla, **no ejecuta nada de su cuerpo**. Solo crea un objeto generador. El código empieza a correr, línea a línea, cada vez que alguien pide el siguiente valor (llamando a `next()` sobre él, típicamente de forma implícita en un `for`).

```python
def leer_lineas(path):
    with open(path) as f:
        for line in f:
            yield line.strip()

gen = leer_lineas("grande.txt")   # el cuerpo NO se ejecuta todavía
```

Esto es "evaluación perezosa" (*lazy evaluation*): el generador produce valores bajo demanda, uno a uno, en vez de calcularlos todos de golpe.

### Por qué ahorra memoria

```python
total = sum(1 for _ in leer_lineas("grande.txt"))
```

La expresión generadora `(1 for _ in ...)` (sin corchetes) produce un `1` cada vez que `sum` le pide el siguiente valor, sin mantener nada más en memoria. Si en cambio hicieras `[line.strip() for line in f]` dentro de la función, construirías y mantendrías **todas** las líneas procesadas simultáneamente en una lista — con archivos grandes, la diferencia de memoria pico es enorme. No es una optimización "que Python hace igual en ambos casos": son estrategias fundamentalmente distintas.

### El ciclo de vida y `GeneratorExit`

Un generador implementa el protocolo iterador (`__iter__` y `__next__`). Cuando se agota (ha hecho todos los `yield` que tenía y termina su cuerpo), lanza internamente `StopIteration`, y **no puede reiniciarse**: si necesitas recorrerlo de nuevo, tienes que llamar otra vez a la función generadora para obtener un objeto nuevo.

Lo interesante para tu código con `with` dentro del generador: si alguien deja de iterar el generador antes de que termine (por ejemplo, hace `break` en el `for` que lo consume) y luego el generador se recolecta o se llama a `.close()` explícitamente sobre él, CPython lanza una excepción especial, `GeneratorExit`, **en el punto exacto donde el generador estaba suspendido** (justo en el `yield`). Eso dispara el `__exit__` del `with` que envuelve ese punto, cerrando el fichero correctamente incluso si nunca llegaste al final del archivo.

```python
gen = leer_lineas("grande.txt")
primera = next(gen)          # el generador se suspende justo después del yield
gen.close()                  # lanza GeneratorExit en ese punto -> se ejecuta
                              # el __exit__ del "with open(...)" -> se cierra el fichero
```

### Ejercicio 1

```python
def numeros_pares(limite):
    for i in range(limite):
        if i % 2 == 0:
            yield i

gen = numeros_pares(10)
print(next(gen))
print(next(gen))
print(list(gen))
print(list(gen))
```

Predice la salida exacta de las cuatro líneas de `print`, explicando por qué la última difiere de la anterior.

---

## 2. Protocolo de descriptores

### ¿Qué es un descriptor?

Es cualquier objeto cuya clase define al menos uno de `__get__`, `__set__` o `__delete__`, y que se usa como **atributo de clase** (no de instancia). Cuando accedes a `instancia.atributo` y `atributo` es un descriptor definido en la clase, Python no te devuelve el descriptor tal cual: invoca su `__get__` y te devuelve lo que ese método retorne. Es el mecanismo que hay *debajo* de `property`, de los métodos normales (sí, incluso las funciones son descriptores — así es como `self` se vincula automáticamente) y de ORMs enteros.

```python
class Cached:
    def __set_name__(self, owner, name):
        self.name = "_" + name

    def __get__(self, obj, owner=None):
        if obj is None:
            return self
        return obj.__dict__.get(self.name)

    def __set__(self, obj, value):
        obj.__dict__[self.name] = value * 2

class Foo:
    x = Cached()

f = Foo()
f.x = 5
print(f.x)   # 10
```

### `__set_name__`: cuándo se ejecuta exactamente

Se invoca **una sola vez**, durante la creación de la clase (mientras se ejecuta el cuerpo de `class Foo:`), no en cada acceso a `f.x`. Es un "hook" que le dice al descriptor con qué nombre fue asignado en la clase que lo contiene, para que pueda, por ejemplo, elegir dónde guardar el valor real (`self.name = "_x"` aquí).

### Data descriptors vs. non-data descriptors: la regla de prioridad

Esta es la parte donde fallaste, y es contraintuitiva la primera vez:

- **Data descriptor**: define `__set__` y/o `__delete__` (con o sin `__get__`). Tiene **prioridad absoluta** sobre lo que haya en `obj.__dict__` al resolver `obj.atributo`.
- **Non-data descriptor**: define **solo** `__get__`. **Cede prioridad** frente a una entrada ya existente en `obj.__dict__` con el mismo nombre.

```python
class SoloGet:
    def __get__(self, obj, owner=None):
        return "desde el descriptor"

class Bar:
    x = SoloGet()

b = Bar()
b.__dict__["x"] = "desde la instancia"
print(b.x)  # "desde la instancia" -- el __dict__ de instancia gana,
            # porque SoloGet es un non-data descriptor
```

`Cached` en el ejemplo de arriba define `__set__`, así que **es** un data descriptor y siempre tiene prioridad sobre `f.__dict__`, sin importar lo que haya ahí guardado.

### property() es exactamente esto

`property(fget, fset, fdel)` es una implementación estándar de este mismo protocolo: internamente define `__get__`, `__set__` y `__delete__` que llaman a las funciones que le pasaste. No hay magia adicional — `Cached` de arriba es, conceptualmente, una `property` hecha a mano con lógica de cacheo/transformación.

### Ejercicio 2

```python
class Validado:
    def __set_name__(self, owner, name):
        self.name = "_" + name

    def __get__(self, obj, owner=None):
        if obj is None:
            return self
        return getattr(obj, self.name, None)

    def __set__(self, obj, value):
        if value < 0:
            raise ValueError("no puede ser negativo")
        setattr(obj, self.name, value)

class Producto:
    precio = Validado()

p = Producto()
p.precio = 10
p.__dict__["precio"] = "manipulado"
print(p.precio)
```

a) ¿Qué imprime la última línea? ¿Por qué la manipulación directa de `p.__dict__["precio"]` no cambia el resultado?
b) ¿Qué pasaría si `Validado` solo definiera `__get__` (quitando `__set__`)? Reescribe el escenario para ese caso.

---

## 3. Type hints vs. pydantic: anotaciones vs. validación real

### La confusión central que tuviste

Las anotaciones de tipo de Python (`nombre: str`, `edad: int`) son **puramente informativas**. El intérprete de CPython **no las comprueba en tiempo de ejecución**. Puedes hacer esto sin ningún error:

```python
def saluda(nombre: str) -> str:
    return "hola " + nombre

saluda(42)   # no lanza nada al llamarla; falla luego dentro, al hacer "hola " + 42
```

Para que las anotaciones tengan efecto, necesitas una herramienta externa:

- **`mypy`** (u otros type checkers): análisis **estático**. Se ejecuta como un paso separado, **antes** de correr tu programa (normalmente en CI o en tu editor). No interviene ni detiene nada mientras el script corre.
- **`pydantic`**: validación y coerción en **tiempo real** (runtime). Cuando instancias un `BaseModel`, pydantic sí revisa los valores recibidos.

### pydantic v2: coerción, no solo validación

```python
from pydantic import BaseModel

class Usuario(BaseModel):
    nombre: str
    edad: int
    activo: bool = True

u = Usuario(nombre="Ana", edad="30")
print(type(u.edad))   # <class 'int'>
```

Por defecto (modo "lax"), pydantic v2 no solo *rechaza* tipos incorrectos: intenta **coaccionarlos** de forma razonable. `"30"` (string) se convierte a `30` (int) porque es un string numéricamente válido. Si pasaras `edad="treinta"`, ahí sí pydantic lanza `ValidationError`, porque no hay forma sensata de convertir eso a `int`.

`activo: bool = True` define un valor por defecto: el campo se vuelve **opcional** al instanciar (si no lo pasas, toma `True`).

### Ejercicio 3

```python
from pydantic import BaseModel, ValidationError

class Config(BaseModel):
    puerto: int
    debug: bool = False
    nombre: str

try:
    c = Config(puerto="8080", nombre="servidor-a", debug="yes")
    print(c)
except ValidationError as e:
    print("error:", e)
```

Predice si esto lanza `ValidationError` o construye el objeto correctamente, e indica el tipo final de cada campo si se construye. (Pista: piensa qué strings pydantic v2 considera "booleanos válidos" en modo coerción.)

---

## 4. Profiling y numpy: eligiendo la herramienta correcta

### Tres herramientas, tres propósitos distintos

- **`cProfile`**: perfila un programa o función completa, dándote estadísticas **por función**: número de llamadas, tiempo propio (`tottime`), tiempo acumulado incluyendo subllamadas (`cumtime`). Ideal para encontrar "en qué función se va el tiempo" a nivel macro.
- **`timeit`**: microbenchmarks. Mide el tiempo de un fragmento de código pequeño repitiéndolo muchas veces y minimizando ruido (evita efectos de arranque en frío, GC, etc.). No te da desglose por función.
- **`line_profiler`** (decorador `@profile`): desglosa el tiempo **línea por línea** dentro de una función concreta. Nivel de detalle distinto y complementario a los otros dos — no son "lo mismo con distinto nombre".

### Por qué numpy es tan rápido

```python
def suma_cuadrados_python(datos):
    total = 0
    for x in datos:
        total += x ** 2
    return total

def suma_cuadrados_numpy(datos):
    arr = np.asarray(datos)
    return np.sum(arr ** 2)
```

El bucle Python puro interpreta **bytecode** en cada iteración: overhead considerable por elemento. `arr ** 2` y `np.sum` en cambio ejecutan bucles **compilados en C** por dentro, vectorizados: la diferencia de rendimiento suele ser de uno o varios órdenes de magnitud para arrays grandes.

Detalle que se te escapó: si `datos` es una lista Python normal (no ya un array numpy), `np.asarray(datos)` tiene que **recorrer y copiar** cada elemento a un buffer contiguo tipado antes de poder vectorizar nada. Ese coste de conversión hay que tenerlo en cuenta al medir — si llamas a esta función muchas veces con listas, ese coste se repite cada vez; si puedes mantener los datos ya en un array numpy de origen, te lo ahorras.

### El GIL y multiprocessing: no es una regla absoluta en un sentido u otro

Afirmar categóricamente que "multiprocessing nunca puede mejorar sobre numpy" es una generalización falsa: depende del tamaño de los datos y de cómo repartas la carga. Lo que sí es cierto siempre es que numpy vectorizado evita el overhead del intérprete, así que suele ganar cuando aplica limpiamente.

### Ejercicio 4

Tienes una función que tarda "mucho" en producción. Ordena estos tres pasos en el orden en que normalmente tiene sentido aplicarlos, y justifica cada uno en una frase: (a) `line_profiler` sobre la función sospechosa, (b) `cProfile` sobre el programa completo, (c) `timeit` sobre la línea concreta que identificaste como el cuello de botella tras los dos pasos anteriores.

---

## 5. Empaquetado y versionado semántico (SemVer)

### ¿Qué es SemVer?

Un esquema de numeración `MAJOR.MINOR.PATCH` (por ejemplo `2.3.1`) con reglas estrictas:

- **MAJOR**: se incrementa ante **cualquier** cambio incompatible con versiones anteriores de la API pública (breaking change). Al incrementarlo, MINOR y PATCH vuelven a 0.
- **MINOR**: se incrementa al añadir funcionalidad nueva de forma retrocompatible.
- **PATCH**: se incrementa para correcciones de bugs retrocompatibles.

### La regla que fallaste: SemVer no "promedia" ni "combina" cambios

```
Versión actual: 2.3.1
Cambios en el próximo release:
  - se elimina un parámetro de una función pública (breaking change)
  - se corrige un bug menor no relacionado
```

La siguiente versión debe ser **3.0.0**. No es "2.4.0 porque hay una mezcla de cambio de API y fix", ni "2.3.2 porque el fix es lo dominante": basta con que exista **un solo** cambio incompatible en todo el release para que tengas que incrementar MAJOR, sin importar cuántos otros cambios menores lo acompañen. SemVer no tiene un concepto de "cambio dominante"; es una regla de umbral, no de promedio.

Tampoco importa el mecanismo técnico que uses para inyectar el número de versión en tu paquete (estático en `pyproject.toml`, dinámico vía `setuptools_scm` a partir de tags de git, etc.) — eso es un detalle de tooling, completamente independiente de qué número te exige SemVer.

### Ejercicio 5

Tu librería está en `1.8.4`. En el próximo release: añades una función nueva (retrocompatible) y deprecas (pero no eliminas todavía) un parámetro antiguo con un warning. ¿Qué versión te corresponde y por qué? ¿Cambiaría tu respuesta si además arreglases dos bugs menores en el mismo release?

---

## 6. Closures y el bug de late binding

### ¿Qué es una closure en Python?

Una función anidada que "recuerda" variables del ámbito que la contiene, aunque ese ámbito ya haya terminado de ejecutarse. Pero la palabra clave es *cómo* las recuerda: **por referencia a la variable (la "celda"), no por el valor que tenía en el momento de crear la función**.

```python
def crear_multiplicadores():
    multiplicadores = []
    for i in range(3):
        def multiplicar(x):
            return x * i
        multiplicadores.append(multiplicar)
    return multiplicadores

resultados = [f(10) for f in crear_multiplicadores()]
# resultados == [20, 20, 20]   -- NO [0, 10, 20]
```

### Por qué da [20, 20, 20] y no [0, 10, 20]

El bucle `for` en Python **no crea un nuevo ámbito en cada iteración** (a diferencia de otros lenguajes como JavaScript con `let`). Las tres funciones `multiplicar` comparten la **misma** variable `i`, la del ámbito de `crear_multiplicadores`. Cuando finalmente llamas a cada función (después de que el bucle ya terminó), `i` vale `2` para las tres, porque todas leen la misma celda de memoria en el momento de la llamada, no en el momento de la definición.

Esto es idéntico para `lambda x: x * i`: las lambdas siguen exactamente las mismas reglas de scope y clausura que `def`. No copian nada por el hecho de ser lambdas.

### La solución idiomática: forzar la evaluación temprana con un valor por defecto

```python
def crear_multiplicadores():
    multiplicadores = []
    for i in range(3):
        def multiplicar(x, i=i):   # el valor por defecto SE EVALÚA al definir
            return x * i            # la función, no al llamarla
        multiplicadores.append(multiplicar)
    return multiplicadores
```

Los argumentos por defecto en Python se evalúan **una vez, en el momento de definirse la función** (en cada vuelta del bucle, aquí). Al capturar el valor actual de `i` como default, cada `multiplicar` queda con su propio valor fijo, independiente de lo que `i` valga después.

### Ejercicio 6

```python
handlers = {}
for evento in ["click", "hover", "submit"]:
    handlers[evento] = lambda: print(f"manejando {evento}")

for nombre, h in handlers.items():
    h()
```

a) ¿Qué imprime este código? (No es lo que el nombre de la clave `nombre` sugiere.)
b) Corrígelo usando el truco del argumento por defecto.

---

## 7. Context managers y `contextlib`

### ¿Qué es el protocolo?

Cualquier objeto con `__enter__` y `__exit__` puede usarse en un `with`. `contextlib.contextmanager` te permite escribir uno usando una función generadora con un único `yield`: todo lo anterior al `yield` es el `__enter__`, todo lo posterior (normalmente en un `finally`) es el `__exit__`.

```python
from contextlib import contextmanager

@contextmanager
def recurso(nombre):
    print(f"abriendo {nombre}")
    try:
        yield nombre
    finally:
        print(f"cerrando {nombre}")
```

### Orden LIFO con múltiples recursos

```python
with recurso("A") as a, recurso("B") as b:
    print(f"usando {a} y {b}")
    raise ValueError("fallo")
```

`with a, b:` es equivalente a anidar `with a:` conteniendo un `with b:` dentro. Al salir (con o sin excepción), los cierres ocurren en orden **inverso** (LIFO) al que se abrieron: primero se cierra B, luego A. Salida completa:

```
abriendo A
abriendo B
usando A y B
cerrando B
cerrando A
```
...y después la excepción `ValueError` se sigue propagando hacia arriba, porque ningún `finally` la capturó ni la absorbió.

### Cómo se propaga (o se suprime) la excepción

Internamente, `contextlib` inyecta la excepción dentro del generador con `gen.throw()`, exactamente en el punto donde estaba suspendido (`yield`). Si nada la captura dentro del generador, sigue propagándose normalmente tras ejecutarse los `finally`. Si en cambio el generador la captura con `except` y **no** la relanza (retorna con normalidad), eso le dice a `contextlib` que la excepción queda suprimida — el bloque `with` termina sin propagarla, como si nada hubiera pasado.

```python
@contextmanager
def recurso_silencioso(nombre):
    try:
        yield nombre
    except ValueError:
        print(f"{nombre}: absorbiendo el error")
    finally:
        print(f"cerrando {nombre}")
```

Y no hay ninguna limitación al número de recursos gestionables en una misma sentencia `with`; `a, b, c, ...` funciona igual con generadores decorados que con cualquier otro context manager.

### Ejercicio 7

```python
@contextmanager
def transaccion(nombre):
    print(f"BEGIN {nombre}")
    try:
        yield
    except Exception:
        print(f"ROLLBACK {nombre}")
        raise
    else:
        print(f"COMMIT {nombre}")

with transaccion("pedido"):
    print("insertando fila")
    raise RuntimeError("fallo de red")
```

Predice la salida completa, incluyendo si el programa termina con una excepción sin capturar al final o no.

---

## 8. Garbage collection, ciclos de referencia y `weakref`

### Los dos mecanismos de CPython

1. **Conteo de referencias (refcounting)**: mecanismo **principal**, siempre activo. Cada objeto lleva un contador de cuántas referencias apuntan a él; al llegar a cero, se libera inmediatamente.
2. **Recolector de ciclos (`gc`)**: un mecanismo adicional que detecta grupos de objetos que se referencian entre sí (ciclos) pero que ya son inalcanzables desde el resto del programa — casos que el refcounting, por diseño, **no puede resolver por sí solo**.

```python
class Nodo:
    def __init__(self):
        self.otro = None
    def __del__(self):
        print("destruido")

a = Nodo()
b = Nodo()
a.otro = b
b.otro = a
del a
del b
```

Tras los dos `del`, ni `a` ni `b` llegan a refcount cero: cada uno sigue teniendo una referencia entrante desde el otro (`a.otro` apunta a `b`, `b.otro` apunta a `a`). El refcounting nunca los liberaría por sí solo. Hace falta que el recolector generacional de ciclos detecte ese grupo inalcanzable-pero-referenciado-internamente y lo libere — no es que "el refcounting esté desactivado", es que este caso concreto está fuera de su alcance por diseño.

### PEP 442: el matiz sobre `__del__`

Antes de Python 3.4, si un ciclo de referencias contenía objetos con `__del__` definido, el recolector **no podía** finalizarlos automáticamente (el orden de destrucción no estaba garantizado y podía ser inseguro), así que quedaban varados en `gc.garbage` sin liberarse — una fuga de memoria real en la práctica. Desde PEP 442 (Python 3.4+), el recolector de ciclos **sí puede** finalizar y liberar objetos con `__del__` involucrados en ciclos. No asumas la fuga automática si trabajas con Python moderno.

### Romper el ciclo con weakref

```python
import weakref

class Nodo:
    def __init__(self):
        self.otro = None

a = Nodo()
b = Nodo()
a.otro = b
b.otro = weakref.ref(a)   # referencia débil: no incrementa el refcount de a
```

Una referencia débil no cuenta para el refcounting. Al usarla en uno de los dos lados, rompes el ciclo fuerte: en cuanto la última referencia fuerte externa a `a` desaparece, su refcount llega a cero y se libera **inmediatamente**, sin depender de que el recolector de ciclos pase por ahí (que no tiene un momento garantizado, salvo llamada explícita a `gc.collect()`).

### Ejercicio 8

```python
import gc, weakref

class Contenedor:
    def __init__(self, nombre):
        self.nombre = nombre
        self.hijos = []
    def __del__(self):
        print(f"liberando {self.nombre}")

padre = Contenedor("padre")
hijo = Contenedor("hijo")
padre.hijos.append(hijo)
hijo.padre = padre     # referencia fuerte de vuelta al padre -> ciclo

del padre
del hijo
print("tras los del, antes de gc.collect()")
gc.collect()
print("después de gc.collect()")
```

a) ¿En qué momento exacto (antes o después de `gc.collect()`) se imprime "liberando padre" / "liberando hijo"? Justifica.
b) Reescribe `hijo.padre` como una referencia débil y explica cómo cambia el momento de liberación.

---

## 9. Repaso rápido: GIL, threading vs. multiprocessing

Esto lo acertaste — un repaso breve para consolidarlo.

El GIL (*Global Interpreter Lock*) de CPython permite que **solo un hilo ejecute bytecode Python a la vez**, incluso en máquinas multinúcleo. No se libera "automáticamente en bucles largos de Python puro": solo se libera en llamadas a ciertas funciones de C/extensiones (como operaciones de numpy) o durante I/O bloqueante (leer de red, de disco, etc.).

Consecuencia práctica:

- **Tareas I/O-bound** (descargar archivos, consultas de red): usa **`threading`**. El GIL se libera durante las esperas de I/O, así que varios hilos pueden solapar esas esperas eficazmente.
- **Tareas CPU-bound en Python puro** (bucles de cómputo intensivo sin liberar el GIL): usa **`multiprocessing`**. Cada proceso tiene su propio intérprete y su propio GIL, logrando paralelismo real entre núcleos.
- `asyncio` no ayuda en CPU-bound: corre sobre un único hilo con un event loop cooperativo, sin paralelismo real de CPU.

---

## 10. Repaso rápido: cProfile, tottime vs. cumtime

También lo acertaste — la clave a recordar:

```
   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.001    0.001    5.230    5.230 main.py:10(procesar)
     1000    0.020    0.000    5.100    0.005 main.py:15(consultar_db)
     1000    5.080    0.005    5.080    0.005 {method 'recv' of '_socket.socket'}
```

- **`cumtime`** (tiempo acumulado): incluye el tiempo de **todas** las subllamadas. `procesar` tiene el `cumtime` más alto, pero eso solo dice que "por ahí pasa mucho tiempo", no que el trabajo se haga ahí.
- **`tottime`** (tiempo propio): tiempo consumido **solo** por esa función, sin contar subllamadas. Aquí casi todo el `tottime` real está en `recv` — la señal inequívoca de que el cuello de botella es la espera de I/O de red, no la lógica Python de `procesar` (que apenas tiene `tottime` propio: 0.001s).

La estrategia correcta ante esto es paralelizar las esperas de I/O (asyncio o hilos), no optimizar la lógica interna de `procesar`, que casi no pesa nada por sí sola.

---

## Soluciones

### Solución 1

```
0
2
[4, 6, 8]
[]
```
Las dos primeras líneas consumen los dos primeros pares (`0`, `2`) uno a uno con `next()`. `list(gen)` agota el resto del generador de una vez, produciendo los pares restantes hasta `limite=10` (`4, 6, 8`). La segunda llamada a `list(gen)` da `[]` porque el generador ya está agotado (lanzó `StopIteration` internamente al terminar) y no puede recorrerse de nuevo; haría falta llamar otra vez a `numeros_pares(10)` para obtener un generador nuevo.

### Solución 2

a) Imprime `10`. `Validado` define `__set__`, así que es un **data descriptor**, y los data descriptors tienen prioridad absoluta sobre `obj.__dict__` al resolver el atributo — sin importar que hayas escrito directamente en `p.__dict__["precio"]`, Python sigue invocando `__get__` del descriptor de clase, que a su vez lee de `p._precio` (el atributo interno con el nombre que fijó `__set_name__`), no de `p.__dict__["precio"]`.

b) Si `Validado` solo definiera `__get__` (sin `__set__`), sería un **non-data descriptor**, y entonces `p.__dict__["precio"] = "manipulado"` sí tendría efecto: `p.precio` devolvería `"manipulado"` directamente desde el `__dict__` de instancia, ignorando el descriptor de clase, porque los non-data descriptors ceden prioridad frente al `__dict__` de la instancia.

### Solución 3

Se construye correctamente, sin lanzar `ValidationError`. En modo coerción de pydantic v2: `"8080"` (string numérico) se coacciona a `int` → `puerto: int = 8080`. `"yes"` es uno de los strings que pydantic v2 acepta como booleano verdadero en modo lax (junto con `"true"`, `"1"`, `"on"`, etc., case-insensitive) → `debug: bool = True`. `"servidor-a"` ya es un `str` válido tal cual. Los tres campos quedan con los tipos declarados (`int`, `bool`, `str`).

### Solución 4

Orden correcto: **(b) `cProfile` primero** — te da una vista global de qué función concentra el tiempo (por `tottime`/`cumtime`), sin necesidad de sospechar de antemano dónde está el problema. Luego **(a) `line_profiler`** sobre la función concreta que `cProfile` señaló, para ver exactamente qué línea dentro de ella consume el tiempo. Finalmente **(c) `timeit`** sobre esa línea o expresión puntual ya identificada, para medir con precisión el efecto de una optimización concreta que propongas, aislada de ruido externo.

### Solución 5

`1.9.0`: añadir funcionalidad retrocompatible (la función nueva) incrementa MINOR y resetea PATCH a 0; deprecar con un warning **sin eliminar** el parámetro no es un breaking change (el código existente sigue funcionando, solo avisa). Si además arreglas dos bugs menores en el mismo release, la respuesta **no cambia**: sigue siendo `1.9.0`, porque MINOR ya "engloba" los PATCH de ese release (no se numeran por separado fixes y features dentro del mismo release; solo importa el nivel más alto de cambio presente, que aquí es MINOR por la función nueva).

### Solución 6

a) Imprime tres veces `"manejando submit"`. Las tres lambdas comparten la misma variable `evento` del ámbito envolvente; en el momento en que finalmente se llaman (después de que el bucle terminó), `evento` vale `"submit"`, el último valor asignado.

b)
```python
handlers = {}
for evento in ["click", "hover", "submit"]:
    handlers[evento] = lambda evento=evento: print(f"manejando {evento}")
```

### Solución 7

```
BEGIN pedido
insertando fila
ROLLBACK pedido
```
Y después el programa termina propagando `RuntimeError: fallo de red` sin capturar (se ve el traceback), porque el `except Exception: ... raise` relanza la excepción tras imprimir el rollback — no la absorbe, solo actúa antes de dejarla seguir su curso. `COMMIT pedido` nunca se imprime porque la rama `else` del `try` solo se ejecuta si no hubo excepción.

### Solución 8

a) Ninguna de las dos líneas "liberando..." se imprime **antes** de `gc.collect()`. `padre` y `hijo` forman un ciclo de referencias (`padre.hijos` contiene a `hijo`, `hijo.padre` apunta de vuelta a `padre`), así que tras los `del`, ninguno de los dos llega a refcount cero por sí solo — cada uno sigue siendo referenciado por el otro. Hace falta que `gc.collect()` (el recolector de ciclos) detecte el grupo inalcanzable y lo libere; ambos mensajes "liberando padre" / "liberando hijo" aparecen **después** de la llamada a `gc.collect()` (el orden relativo entre ellos no está garantizado).

b)
```python
import weakref
hijo.padre = weakref.ref(padre)   # referencia débil, no incrementa refcount
```
Con esto, `hijo` ya no mantiene vivo a `padre` mediante una referencia fuerte. Al hacer `del padre`, su refcount llega a cero inmediatamente (ya no hay ciclo) y se libera al instante, sin esperar a `gc.collect()`. El mensaje "liberando padre" aparecería justo en el `del padre`, mucho antes que "liberando hijo" (que sigue dependiendo de cuándo se destruya `hijo` por su propio refcount, ya sin ciclo).
