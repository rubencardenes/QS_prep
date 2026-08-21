# Resultado del test — Ingeniería de software en Python

- Fecha: 2026-08-05 14:47
- Nivel: media
- Puntuación: **47%** (2.33/5 puntos)
- Preguntas perfectas: 1/5

## Revisión pregunta a pregunta

### ❌ Pregunta 1 — Empaquetado, versionado semántico y distribución de librerías Python

Tu equipo mantiene una librería interna publicada en un índice PyPI privado, actualmente en la versión `2.3.1`, siguiendo Versionado Semántico (SemVer). En el próximo release se elimina un parámetro de una función pública (cambio incompatible con código existente) y, además, se corrige un bug menor no relacionado. ¿Cuál es la práctica correcta según SemVer para numerar y publicar esta versión?

- [ ] **La siguiente versión debe ser 3.0.0: al existir un cambio incompatible (breaking change) se incrementa MAJOR y se reinician MINOR y PATCH a 0, sin importar que también haya un fix menor incluido en el mismo release.** — _correcta_: Correcto: SemVer establece que basta un único cambio incompatible en la API pública para obligar a incrementar MAJOR; los demás cambios (fixes, mejoras) del mismo release no alteran esa regla.
- [ ] **Debe ser 3.0.0, pero solo si el proyecto gestiona la versión con `setuptools_scm`; si el número de versión es estático en pyproject.toml, el cambio incompatible no obliga a incrementar MAJOR.** — _incorrecta_: Incorrecto: el mecanismo usado para inyectar la versión en el paquete (estático en pyproject.toml, setuptools_scm, etc.) es independiente de las reglas de SemVer; en ambos casos un breaking change exige subir MAJOR.
- [x] **La siguiente versión debe ser 2.4.0, porque solo se incrementa MINOR cuando el release combina un cambio de API con una corrección de bug, reservando MAJOR para versiones sin fixes.** — _incorrecta_: Incorrecto: SemVer no combina ni promedia el nivel según el número de cambios; cualquier cambio incompatible por sí solo ya exige incrementar MAJOR, independientemente de qué más incluya el release.
- [ ] **La siguiente versión debe ser 2.3.2, ya que el fix de bug es el cambio dominante y la eliminación del parámetro se documenta solo en el CHANGELOG sin afectar el número de versión.** — _incorrecta_: Incorrecto: un cambio incompatible en la API pública siempre debe reflejarse en el número MAJOR; documentarlo en el CHANGELOG no sustituye la obligación de comunicar el breaking change vía versión.

> SemVer (MAJOR.MINOR.PATCH) exige incrementar MAJOR ante cualquier cambio incompatible con versiones anteriores de la API pública, reiniciando MINOR y PATCH a 0, con independencia de otros cambios menores incluidos en el mismo release y del mecanismo técnico usado para definir la versión en el empaquetado (pyproject.toml, setuptools_scm, etc.).
>
> Repasar: `SemVer, pyproject.toml, versionado de paquetes`

### ⚠️ Pregunta 2 — Decoradores, closures y captura de variables en scope

Analiza el siguiente código:

```python
def crear_multiplicadores():
    multiplicadores = []
    for i in range(3):
        def multiplicar(x):
            return x * i
        multiplicadores.append(multiplicar)
    return multiplicadores

resultados = [f(10) for f in crear_multiplicadores()]
```

¿Qué afirmaciones sobre el comportamiento de las clausuras (closures) en Python son correctas?

- [x] **Se puede solucionar cambiando la definición a `def multiplicar(x, i=i): return x * i`, ya que los valores por defecto se evalúan una vez, en el momento de definir la función.** — _correcta_: Correcto: los argumentos por defecto se evalúan al definirse la función (en cada iteración del bucle), por lo que cada `multiplicar` queda con su propio valor fijo de i.
- [ ] **El mismo problema ocurriría igual si en vez de una función anidada se usara `lambda x: x * i`, porque las lambdas también capturan variables libres por referencia.** — _correcta_: Correcto: las lambdas siguen exactamente las mismas reglas de scope y clausura que las funciones definidas con def; no copian el valor de las variables libres.
- [ ] **El problema desaparece automáticamente en Python 3.x porque cada iteración del bucle for crea un nuevo scope local para i.** — _incorrecta_: Incorrecto: a diferencia de otros lenguajes, el bucle for en Python no introduce un nuevo scope por iteración; la variable i vive en el scope de la función contenedora y se reutiliza en cada vuelta.
- [ ] **resultados es [20, 20, 20], porque las funciones anidadas capturan la variable i por referencia (closure), y tras terminar el bucle i vale 2 para las tres.** — _correcta_: Correcto: las tres funciones comparten la misma celda de variable libre i; cuando se ejecutan, i ya vale 2 (el último valor tras el bucle), así que las tres devuelven 10*2=20.
- [ ] **resultados es [0, 10, 20], porque cada función anidada captura el valor de i que tenía en el momento de su creación.** — _incorrecta_: Incorrecto: Python no captura el valor de la variable en el momento de definir la función, sino una referencia a la variable del scope envolvente, que se resuelve al llamar a la función.

> Las funciones anidadas en Python capturan variables libres por referencia al entorno (closure sobre la celda de la variable), no por valor en el instante de creación. Esto provoca el clásico bug de 'late binding' en bucles, que se corrige forzando la evaluación temprana mediante un argumento por defecto o usando functools.partial.
>
> Repasar: `closures, late binding, scope léxico`

### ⚠️ Pregunta 3 — Context managers, protocolos y gestión determinista de recursos

Dado el siguiente código:

```python
from contextlib import contextmanager

@contextmanager
def recurso(nombre):
    print(f"abriendo {nombre}")
    try:
        yield nombre
    finally:
        print(f"cerrando {nombre}")

with recurso("A") as a, recurso("B") as b:
    print(f"usando {a} y {b}")
    raise ValueError("fallo")
```

¿Qué afirmaciones son correctas sobre el comportamiento del protocolo de context managers en este ejemplo?

- [x] **El orden de salida es: abriendo A, abriendo B, usando A y B, cerrando B, cerrando A — los gestores de contexto se cierran en orden inverso (LIFO) al que se abrieron.** — _correcta_: Correcto: `with a, b:` es equivalente a anidar `with a:` dentro de él `with b:`, por lo que al salir se invoca primero __exit__ de B y después el de A.
- [ ] **La excepción ValueError se propaga tras ejecutarse ambos bloques finally, ya que ninguno de los generadores la captura con except.** — _correcta_: Correcto: internamente contextlib usa gen.throw() para inyectar la excepción en el punto del yield; como no hay except que la absorba, el finally se ejecuta y luego la excepción sigue propagándose hacia arriba.
- [ ] **El código es equivalente a usar try/finally manualmente, pero contextlib.contextmanager no soporta gestionar dos recursos en una misma sentencia with.** — _incorrecta_: Incorrecto: la sintaxis `with a, b:` funciona igual con generadores decorados con @contextmanager que con cualquier otro context manager; no hay limitación al número de recursos.
- [ ] **Si la excepción no es capturada por ningún generador, el finally de recurso('B') no llega a ejecutarse, porque la excepción sale directamente sin invocar __exit__.** — _incorrecta_: Incorrecto: al salir del bloque with siempre se invoca __exit__ (que dispara el finally del generador) independientemente de si hay excepción o no; eso es precisamente lo que garantiza la gestión determinista de recursos.
- [ ] **Si añadiéramos `except ValueError: pass` justo después del yield en recurso, la excepción quedaría suprimida y el bloque with terminaría sin propagarla.** — _correcta_: Correcto: si el generador captura la excepción y retorna con normalidad (sin relanzarla), contextlib interpreta eso como una señal para que __exit__ devuelva True, suprimiendo la excepción.

> El protocolo de context managers (__enter__/__exit__) garantiza que la limpieza de recursos ocurra siempre, incluso ante excepciones, y en múltiples with los cierres se hacen en orden LIFO. contextlib.contextmanager traduce un generador con try/finally en ese protocolo, usando gen.throw() para propagar excepciones al punto del yield.
>
> Repasar: `contextlib.contextmanager, protocolo __enter__/__exit__`

### ⚠️ Pregunta 4 — Garbage collection, referencias circulares y trampas de memoria

Analiza el siguiente código en CPython:

```python
import gc

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

¿Qué afirmaciones son correctas sobre el comportamiento de memoria de este código?

- [x] **`a` y `b` forman un ciclo de referencias, por lo que tras los `del` su conteo de referencias no llega a cero y su liberación depende del recolector de ciclos generacional (módulo `gc`), no del conteo de referencias.** — _correcta_: Correcto: cada objeto es referenciado por el otro a través de `self.otro`, así que el refcounting por sí solo no puede liberarlos; hace falta que el gc de ciclos detecte el grupo inalcanzable.
- [ ] **`gc.collect()` es necesario porque el conteo de referencias está deshabilitado por defecto en CPython.** — _incorrecta_: Falso: el conteo de referencias siempre está activo en CPython y es el mecanismo principal de liberación; `gc` solo se encarga de los ciclos que el refcounting no puede resolver.
- [ ] **Como las instancias definen `__del__`, CPython nunca podrá liberarlas automáticamente y se produce una fuga de memoria garantizada.** — _incorrecta_: Es el comportamiento antiguo (pre-3.4). Con PEP 442 el recolector de ciclos sí puede finalizar y liberar objetos con `__del__` involucrados en ciclos.
- [x] **Sustituir `self.otro` en uno de los dos objetos por un `weakref.ref` evitaría crear el ciclo fuerte y permitiría liberar los objetos inmediatamente por conteo de referencias, sin depender del gc.** — _correcta_: Correcto: una referencia débil no incrementa el refcount, así que se rompe el ciclo y la liberación vuelve a ser determinista vía refcounting en cuanto la referencia fuerte externa desaparece.
- [ ] **Desde CPython 3.4 (PEP 442), el hecho de que las clases definan `__del__` ya no impide que el recolector de ciclos pueda recolectarlos automáticamente.** — _correcta_: Correcto: antes de PEP 442, los ciclos con `__del__` quedaban en `gc.garbage` sin liberarse; desde 3.4 el gc puede finalizarlos y liberarlos igualmente.

> Los ciclos de referencias son la trampa de memoria clásica en Python: el conteo de referencias (mecanismo principal de CPython) no puede liberarlos porque ningún objeto del ciclo llega a refcount cero. El recolector generacional de ciclos (`gc`) existe justamente para esto, y desde PEP 442 (Python 3.4) también puede finalizar objetos con `__del__` involucrados en ciclos, algo que antes los dejaba varados en `gc.garbage`.
>
> Repasar: `gc module, PEP 442, weakref, conteo de referencias vs recolector de ciclos`

### ✅ Pregunta 5 — Profiling, benchmarking y optimización de cuellos de botella

Un desarrollador perfila una función con `cProfile` y obtiene esta salida (ordenada por `cumtime`):

```
   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.001    0.001    5.230    5.230 main.py:10(procesar)
     1000    0.020    0.000    5.100    0.005 main.py:15(consultar_db)
     1000    5.080    0.005    5.080    0.005 {method 'recv' of '_socket.socket'}
```

¿Cuál es la interpretación correcta y la estrategia de optimización más adecuada?

- [x] **El verdadero cuello de botella es la espera de red en las llamadas al socket (`tottime` alto en `recv`); conviene paralelizar las 1000 consultas con concurrencia (asyncio o hilos) en lugar de optimizar la lógica Python de `procesar`.** — _correcta_: Correcto: `tottime` (tiempo propio, sin subllamadas) es casi todo el tiempo total en `recv`, lo que indica I/O bloqueante repetido; al ser I/O, hilos o asyncio permiten solapar las esperas y reducir el tiempo total.
- [ ] **El cuello de botella está en `procesar`, ya que tiene el `cumtime` más alto de la tabla, así que hay que optimizar su lógica interna.** — _incorrecta_: Engañoso: `cumtime` incluye el tiempo de todas las llamadas anidadas, y el `tottime` propio de `procesar` es solo 0.001s, es decir, casi no hace trabajo por sí misma.
- [ ] **Como el `tottime` de `consultar_db` es bajo (0.020s), el problema ya está localizado y resuelto sin necesidad de mirar más filas.** — _incorrecta_: Falso: el bajo `tottime` propio de `consultar_db` es justo la pista de que el coste real está en una función que llama (`recv`), no de que el problema esté resuelto.
- [ ] **Para confirmar la hipótesis conviene usar `timeit` sobre `procesar` completa, ya que da mediciones más precisas que `cProfile` para código con I/O de red.** — _incorrecta_: `timeit` está pensado para microbenchmarks de fragmentos de código repetibles y deterministas; con I/O de red añade ruido y no aporta desglose por función, que es justo lo que ya dio `cProfile`.
- [ ] **`cProfile` no puede medir correctamente el tiempo de espera en I/O bloqueante como `recv`, por lo que estos resultados subestiman el verdadero cuello de botella.** — _incorrecta_: Falso: `cProfile` es un profiler determinista basado en eventos de llamada/retorno y sí contabiliza el tiempo de reloj transcurrido dentro de `recv`, incluida la espera bloqueante.

> Al leer una salida de `cProfile`, `cumtime` (tiempo acumulado, incluye subllamadas) sirve para ver dónde se concentra el tiempo total del árbol de llamadas, pero `tottime` (tiempo propio) es el que identifica dónde se consume realmente el tiempo. Aquí casi todo el `tottime` está en `recv`, señal de un cuello de botella de I/O de red, que se resuelve con concurrencia (asyncio/hilos), no reescribiendo la lógica Python que apenas pesa.
>
> Repasar: `cProfile, tottime vs cumtime, I/O-bound vs CPU-bound, concurrencia con asyncio/threading`
