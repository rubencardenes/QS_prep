# Resultado del test — Ingeniería de software en Python

- Fecha: 2026-08-04 16:00
- Nivel: media
- Puntuación: **47%** (2.33/5 puntos)
- Preguntas perfectas: 1/5

## Revisión pregunta a pregunta

### ⚠️ Pregunta 1 — Generadores, iteradores y memory efficiency en secuencias

Sobre el siguiente código, ¿qué afirmaciones son correctas respecto al comportamiento de generadores e iteradores en Python?

```python
def leer_lineas(path):
    with open(path) as f:
        for line in f:
            yield line.strip()

total = sum(1 for _ in leer_lineas("grande.txt"))
```

- [x] **El uso de with dentro del generador garantiza el cierre del archivo incluso si el consumidor deja de iterar antes del final, siempre que el generador se cierre explícitamente (close()) o sea recolectado por el recolector de basura.** — _correcta_: Correcto: al hacer close() (o al recolectarse el objeto), CPython lanza GeneratorExit en el punto donde el generador está suspendido en yield, lo que dispara el __exit__ del with y cierra el archivo.
- [x] **Reemplazar el bucle for por una comprensión de lista dentro de la función ([line.strip() for line in f]) tendría el mismo consumo de memoria pico, ya que Python optimiza ambas formas de igual manera.** — _incorrecta_: Incorrecto: una comprensión de lista construye y mantiene en memoria todas las líneas procesadas simultáneamente, mientras que el generador solo mantiene una línea a la vez, con un consumo de memoria muy inferior en archivos grandes.
- [x] **leer_lineas es una función generadora; al llamarla (leer_lineas("grande.txt")) no se ejecuta su cuerpo, solo se crea un objeto generador.** — _correcta_: Correcto: el cuerpo de una función con yield no se ejecuta al invocarla; se crea un objeto generador y el código corre solo al iterar (llamando a next()).
- [ ] **La expresión sum(1 for _ in leer_lineas(...)) carga todo el archivo en memoria antes de sumar, igual que sum([1 for _ in leer_lineas(...)]).** — _incorrecta_: Incorrecto: la expresión generadora (sin corchetes) produce valores uno a uno bajo demanda; en cambio, la comprensión de lista sí materializa todos los elementos en memoria antes de pasarlos a sum().
- [ ] **Un generador implementa el protocolo iterador (__iter__ y __next__), por lo que una vez agotado no puede volver a recorrerse sin crear un nuevo objeto generador.** — _correcta_: Correcto: los generadores son de un solo uso; tras agotarse (StopIteration), hay que llamar de nuevo a la función generadora para obtener un nuevo objeto iterable.

> Los generadores implementan el protocolo iterador de forma perezosa (lazy), produciendo valores bajo demanda y evitando cargar estructuras completas en memoria, lo que los hace idóneos para procesar archivos o secuencias grandes. Su ciclo de vida está ligado al protocolo de excepciones (StopIteration/GeneratorExit), lo que permite combinarlos con context managers para liberar recursos correctamente.
>
> Repasar: `Generadores / protocolo iterador / lazy evaluation / GeneratorExit`

### ⚠️ Pregunta 2 — Decoradores, descriptores y metaclases en el modelo de objetos

Dado el siguiente código, ¿qué afirmaciones sobre el protocolo de descriptores son correctas?

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
print(f.x)
```

- [ ] **__set_name__ se ejecuta en cada acceso a f.x para determinar dinámicamente el nombre del atributo interno.** — _incorrecta_: Incorrecto: __set_name__ se invoca una única vez, cuando se crea la clase (durante la ejecución del cuerpo de class Foo), no en cada acceso.
- [ ] **property() es, internamente, una implementación de este mismo protocolo de descriptores, usando __get__, __set__ y __delete__.** — _correcta_: Correcto: property es un data descriptor construido con fget, fset y fdel que internamente implementa __get__/__set__/__delete__.
- [ ] **Si Cached solo definiera __get__ (sin __set__ ni __delete__), seguiría teniendo prioridad sobre una variable del mismo nombre guardada en el __dict__ de la instancia.** — _incorrecta_: Incorrecto: sin __set__/__delete__ sería un 'non-data descriptor', y estos ceden prioridad frente a entradas ya existentes en el __dict__ de la instancia.
- [ ] **Cached es un "data descriptor" porque define __set__ (además de __get__), por lo que tiene prioridad sobre el __dict__ de la instancia al resolver f.x.** — _correcta_: Correcto: basta con implementar __set__ o __delete__ para que un descriptor sea de tipo 'data descriptor', y estos siempre tienen prioridad sobre el __dict__ de la instancia en la búsqueda de atributos.
- [x] **print(f.x) imprime 10, porque __set__ multiplica el valor asignado (5) por 2 antes de guardarlo en el __dict__ de la instancia.** — _correcta_: Correcto: f.x = 5 invoca __set__, que guarda 10 en obj.__dict__['_x']; luego __get__ recupera ese valor.

> El protocolo de descriptores (definido en el 'data model' de Python) distingue entre data descriptors (con __set__ y/o __delete__), que tienen prioridad sobre el __dict__ de la instancia, y non-data descriptors (solo __get__), que no la tienen. __set_name__ es un 'hook' que se ejecuta solo en la creación de la clase.
>
> Repasar: `Descriptor Protocol / __set_name__ / data vs non-data descriptors`

### ⚠️ Pregunta 3 — Type hints, pydantic y validación de datos en runtime

Un compañero define el siguiente modelo con pydantic (v2) para validar datos de entrada de una API:

```python
from pydantic import BaseModel

class Usuario(BaseModel):
    nombre: str
    edad: int
    activo: bool = True

u = Usuario(nombre="Ana", edad="30")
print(type(u.edad))
```

¿Qué afirmaciones son correctas sobre el comportamiento de este código y sobre `typing`/pydantic en general?

- [x] **Si se pasa `edad="treinta"`, pydantic lanzará una `ValidationError` porque el string no se puede convertir a `int`.** — _correcta_: Correcto: pydantic solo coacciona strings que representen números válidos; un string no numérico provoca una `ValidationError`.
- [x] **`activo: bool = True` define un valor por defecto, y ese campo sigue siendo opcional al instanciar `Usuario`.** — _correcta_: Correcto: en pydantic, un campo con valor por defecto se vuelve opcional; si no se pasa `activo`, tomará `True`.
- [x] **Usar `mypy` sobre este archivo detectaría en tiempo de ejecución que `edad="30"` es un string, deteniendo la ejecución antes de crear el objeto.** — _incorrecta_: Falso: mypy es un analizador estático que se ejecuta como paso separado antes de correr el programa; no interviene ni detiene la ejecución en tiempo real del script.
- [ ] **Las anotaciones de tipo (`nombre: str`, `edad: int`) por sí solas, sin pydantic ni un validador, ya provocan un error en tiempo de ejecución si se pasa un tipo incorrecto.** — _incorrecta_: Falso: los type hints de Python son solo anotaciones informativas; el intérprete no las comprueba en tiempo de ejecución. Se necesita una herramienta como pydantic o mypy (estático) para validarlas.
- [ ] **El código se ejecuta sin error y `type(u.edad)` imprime `<class 'int'>`, porque pydantic coacciona el string `"30"` a `int` al validar.** — _correcta_: Correcto: pydantic v2 realiza coerción de tipos por defecto (modo 'lax'), convirtiendo strings numéricos válidos a int en campos anotados como `int`.

> Pydantic v2 usa las anotaciones de `typing` para validar y coaccionar datos en tiempo de ejecución, algo que Python no hace por defecto con simples type hints. Es clave distinguir entre validación estática (mypy) y validación/coerción en tiempo real (pydantic).
>
> Repasar: `pydantic BaseModel, coerción de tipos, ValidationError`

### ⚠️ Pregunta 4 — Profiling, numpy y optimización de código Python

Se quiere optimizar la siguiente función que suma los cuadrados de una lista/array grande, y se compara con una versión vectorizada usando numpy:

```python
import numpy as np

def suma_cuadrados_python(datos):
    total = 0
    for x in datos:
        total += x ** 2
    return total

def suma_cuadrados_numpy(datos):
    arr = np.asarray(datos)
    return np.sum(arr ** 2)
```

¿Qué afirmaciones sobre el rendimiento y las técnicas de profiling aplicables son correctas?

- [x] **Como el GIL impide la ejecución paralela real de bytecode Python, usar `multiprocessing` para paralelizar `suma_cuadrados_python` entre varios núcleos nunca puede mejorar el rendimiento frente a numpy, incluso repartiendo el trabajo en más procesos que elementos tiene el array.** — _incorrecta_: Falso como afirmación absoluta: aunque numpy suele ganar por evitar overhead de procesos, la comparación depende del tamaño de datos y el reparto de carga; además el enunciado incluye un caso extremo absurdo (más procesos que elementos) que no representa el argumento real sobre el GIL.
- [ ] **El módulo `cProfile` es adecuado para identificar qué función consume más tiempo total, pero para medir el tiempo de una única línea o expresión pequeña suele preferirse `timeit`, que repite la medición y minimiza el ruido.** — _correcta_: Correcto: `cProfile` da estadísticas por función (llamadas, tiempo acumulado), mientras que `timeit` está diseñado para microbenchmarks de fragmentos pequeños, ejecutando múltiples repeticiones y evitando efectos de arranque en frío.
- [x] **Si `datos` es una lista de Python (no un array numpy), `np.asarray(datos)` copia y convierte los datos a un array contiguo en memoria antes de operar, lo cual añade un coste de conversión que conviene tener en cuenta al medir el rendimiento.** — _correcta_: Correcto: convertir una lista Python a `ndarray` implica recorrer los elementos y copiarlos a un buffer contiguo tipado, coste que debe incluirse al comparar tiempos, especialmente si la conversión se repite en cada llamada.
- [ ] **Usar `%timeit` en un notebook de Jupyter y usar `line_profiler` (decorador `@profile`) son técnicas equivalentes y devuelven exactamente el mismo tipo de información: el tiempo total de ejecución de la celda completa.** — _incorrecta_: Falso: `%timeit` mide el tiempo total de ejecución repitiendo la llamada, mientras que `line_profiler` desglosa el tiempo línea por línea dentro de una función, ofreciendo un nivel de detalle distinto y complementario.
- [x] **`suma_cuadrados_numpy` suele ser significativamente más rápida para arrays grandes porque `arr ** 2` y `np.sum` se ejecutan en bucles compilados en C, evitando el overhead del bucle interpretado de Python.** — _correcta_: Correcto: numpy vectoriza las operaciones aritméticas, ejecutando el bucle en código C compilado en lugar de bytecode Python interpretado, lo que reduce drásticamente el overhead por elemento.

> La vectorización con numpy evita el overhead del intérprete de Python al mover los bucles a código C, lo que suele traducirse en mejoras de rendimiento de uno o varios órdenes de magnitud frente a bucles puros en Python. Elegir la herramienta de profiling correcta (`cProfile`, `timeit`, `line_profiler`) depende de si se busca un perfil global por función o una medición fina de una expresión o línea concreta.
>
> Repasar: `numpy vectorización, cProfile vs timeit vs line_profiler, GIL`

### ✅ Pregunta 5 — GIL, threading y multiprocessing: elección según caso de uso

Tienes dos tareas en Python (CPython estándar): (1) descargar 1000 archivos por HTTP y (2) calcular hashes SHA-256 sobre varios GB de datos usando bucles puros de Python (sin liberar el GIL). ¿Qué combinación de estrategias de concurrencia es la más adecuada para (1) y (2) respectivamente?

- [ ] **threading para el cálculo de hashes (el GIL se libera automáticamente en bucles largos de Python puro) y multiprocessing para las descargas.** — _incorrecta_: Incorrecto: el GIL no se libera automáticamente durante bucles de bytecode puro de Python; solo se libera en llamadas a ciertas funciones de C/extensiones o en operaciones de I/O bloqueante.
- [ ] **multiprocessing para ambas tareas, ya que siempre evita el GIL y ofrece mejor rendimiento que threading en cualquier escenario.** — _incorrecta_: Incorrecto: para I/O-bound, multiprocessing añade overhead innecesario (creación de procesos, serialización) sin beneficio real, ya que el cuello de botella no es la CPU sino la espera de red.
- [ ] **threading para ambas tareas, porque el GIL solo afecta a operaciones de red y no al cómputo en Python puro.** — _incorrecta_: Incorrecto: es justo al revés. El GIL impide el paralelismo real de CPU en bucles Python puros ejecutados en varios hilos; threading no acelera el cómputo CPU-bound puro.
- [ ] **asyncio para el cálculo de hashes, ya que las corrutinas se ejecutan en paralelo real sobre múltiples núcleos de CPU.** — _incorrecta_: Incorrecto: asyncio funciona sobre un único hilo y un event loop cooperativo; no ofrece paralelismo real de CPU en varios núcleos, por lo que no ayuda en tareas CPU-bound puras.
- [x] **threading para las descargas (el GIL se libera durante las esperas de I/O) y multiprocessing para el cálculo de hashes (evita el cuello de botella del GIL en cómputo puro de Python).** — _correcta_: Correcto: en I/O-bound, threading permite solapar esperas de red porque el GIL se libera durante las llamadas bloqueantes de I/O; en CPU-bound con bucles puros de Python, multiprocessing usa procesos independientes con su propio intérprete y GIL, logrando paralelismo real en varios núcleos.

> El GIL de CPython permite que solo un hilo ejecute bytecode Python a la vez. Para tareas I/O-bound, threading es eficaz porque el GIL se libera durante las esperas de I/O; para tareas CPU-bound en Python puro, hay que recurrir a multiprocessing (o extensiones en C que liberen el GIL, como numpy) para aprovechar varios núcleos.
>
> Repasar: `GIL / threading vs multiprocessing / I/O-bound vs CPU-bound`
