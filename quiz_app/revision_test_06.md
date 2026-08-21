# Resultado del test — Mixto (entrevista completa)

- Fecha: 2026-08-04 16:13
- Nivel: media
- Puntuación: **40%** (2.00/5 puntos)
- Preguntas perfectas: 1/5

## Revisión pregunta a pregunta

### ❌ Pregunta 1 — Gestión de memoria en Python con extensiones de C++11

Estás escribiendo una extensión de Python con pybind11 (C++11) que expone una clase C++ mediante `py::class_<T>`. ¿Cuál de las siguientes afirmaciones sobre la gestión de memoria es correcta?

- [ ] **Si código C++ retiene un puntero crudo PyObject* sin llamar a Py_INCREF, el recolector de basura de Python garantiza que el objeto no se liberará mientras ese puntero exista en el stack de C++.** — _incorrecta_: CPython no rastrea punteros crudos en el stack de C++; sin un Py_INCREF (o el uso de py::object, que lo hace automáticamente) el objeto puede liberarse mientras el puntero crudo sigue existiendo, produciendo un use-after-free.
- [x] **pybind11 usa std::shared_ptr internamente para todos los objetos expuestos a Python, delegando el conteo de referencias exclusivamente en C++ y evitando así el mecanismo de refcounting de CPython.** — _incorrecta_: El holder por defecto de pybind11 es std::unique_ptr, no shared_ptr (aunque puede configurarse), y en todos los casos el objeto Python que envuelve a la instancia C++ sigue sujeto al refcounting normal de CPython.
- [ ] **Es seguro invocar funciones que manipulan PyObject* (como Py_INCREF) dentro de una sección protegida por `py::gil_scoped_release`, ya que pybind11 reactiva el GIL automáticamente ante cualquier acceso a la API de Python.** — _incorrecta_: pybind11 no reactiva el GIL automáticamente; tras liberar el GIL con gil_scoped_release, cualquier llamada a la API de Python (incluido Py_INCREF/Py_DECREF) sin volver a adquirirlo explícitamente (gil_scoped_acquire) es undefined behavior.
- [ ] **Al exponer una clase con `py::class_<T>`, por defecto el objeto Python creado posee (owns) la instancia C++ y la destruye automáticamente cuando su refcount de Python llega a cero, gestionado internamente mediante un holder (std::unique_ptr por defecto).** — _correcta_: Este es el comportamiento por defecto de pybind11: el wrapper Python es dueño de la instancia C++ vía un holder (unique_ptr salvo que se especifique otro), y cuando CPython libera el objeto Python (refcount a cero), se destruye el objeto C++.

> En extensiones pybind11, la propiedad de las instancias C++ expuestas a Python se gestiona mediante holders (unique_ptr por defecto), y el ciclo de vida final sigue dependiendo del refcounting de CPython sobre el objeto Python wrapper. Manipular PyObject* de forma segura exige respetar tanto el conteo de referencias explícito (Py_INCREF/DECREF o py::object) como la disciplina del GIL.
>
> Repasar: `pybind11 holders, refcounting de CPython, GIL scoped release/acquire`

### ⚠️ Pregunta 2 — Pipelines de visión con OpenCV: sincronización y performance

Diseñas un pipeline de captura y procesamiento con OpenCV en Python para una cámara a 30 FPS. Un hilo de captura lee frames con `cv2.VideoCapture` y los inserta en una `queue.Queue()` (sin límite de tamaño) que consume un hilo de inferencia. Tras varios minutos de ejecución observas que la latencia entre captura e inferencia crece progresivamente. ¿Cuáles de las siguientes afirmaciones son correctas?

```python
cap = cv2.VideoCapture(0)
q = queue.Queue()

def capture_loop():
    while True:
        ok, frame = cap.read()
        if ok:
            q.put(frame)

def infer_loop():
    while True:
        frame = q.get()
        run_inference(frame)
```

- [x] **`cv2.VideoCapture.read()` siempre devuelve una copia de memoria completamente nueva en cualquier backend, por lo que hacer `frame.copy()` antes de encolar es completamente redundante en todos los casos.** — _incorrecta_: Incorrecto por la generalización: el comportamiento de reutilización de buffers depende del backend (V4L2, GStreamer, decodificadores hardware), por lo que copiar explícitamente antes de encolar es una práctica defensiva razonable, no siempre redundante.
- [x] **Al no tener tamaño máximo, la cola acumula frames cuando el consumidor es más lento que el productor, y esa acumulación es la causa directa del crecimiento de la latencia.** — _correcta_: Correcto: sin `maxsize`, cada frame que la inferencia no llega a consumir a tiempo se queda en cola, aumentando el retraso acumulado entre captura y procesamiento.
- [x] **Usar una cola de tamaño 1 que descarte el frame antiguo al llegar uno nuevo mantiene siempre el frame más reciente disponible, sacrificando frames intermedios pero acotando la latencia.** — _correcta_: Correcto: en pipelines de tiempo real es habitual priorizar la actualidad del dato sobre procesar todos los frames, descartando los que quedan obsoletos.
- [ ] **La solución consiste simplemente en aumentar el tamaño máximo de la cola para evitar bloqueos del productor.** — _incorrecta_: Incorrecto: aumentar el tamaño de la cola solo retrasa el problema (y consume más memoria), pero no evita que la latencia siga creciendo si el consumidor sigue siendo más lento que el productor.
- [x] **El buffer interno de `cv2.VideoCapture` también puede acumular frames si el hilo de captura no lee tan rápido como llegan del driver/cámara, contribuyendo a la latencia si no se gestiona (p. ej. vaciándolo o ajustando `CAP_PROP_BUFFERSIZE`).** — _correcta_: Correcto: es un problema conocido de OpenCV/V4L2/GStreamer; si no se controla el buffer interno del backend, se puede introducir latencia adicional independiente de la cola de Python.

> El crecimiento progresivo de latencia en pipelines productor-consumidor suele deberse a colas sin límite que absorben la diferencia de velocidad entre etapas. La solución típica combina colas acotadas con política de descarte ('drop-latest') y control explícito del buffering interno de captura, en vez de simplemente agrandar buffers.
>
> Repasar: `Backpressure y colas acotadas en pipelines de visión (cv2.VideoCapture, queue.Queue, CAP_PROP_BUFFERSIZE)`

### ⚠️ Pregunta 3 — Move semantics en C++17: casos de uso y trampas comunes

Dado el siguiente código en C++17:

```cpp
class Buffer {
public:
    explicit Buffer(std::vector<int> data) : data_(std::move(data)) {}
    std::vector<int> data_;
};

Buffer make() {
    std::vector<int> v = {1, 2, 3};
    return Buffer(std::move(v));
}
```

¿Cuáles de las siguientes afirmaciones sobre este código y sobre move semantics en C++17 son correctas? (selecciona todas las que apliquen)

- [x] **std::move(v) convierte v en un xvalue, lo que permite que se invoque el constructor de movimiento de std::vector en lugar de copiar los elementos.** — _correcta_: std::move no mueve nada por sí mismo; realiza un static_cast a rvalue reference, habilitando la resolución de sobrecarga hacia el constructor de movimiento del tipo destino.
- [ ] **Gracias a la copia elidida garantizada (guaranteed copy elision) de C++17, el `return Buffer(std::move(v));` no produce absolutamente ninguna operación de movimiento, ni siquiera al inicializar el miembro data_ a partir del parámetro data.** — _incorrecta_: La elisión garantizada evita la construcción por copia/movimiento del objeto Buffer devuelto, pero no elimina el movimiento interno de std::move(data) al inicializar data_ dentro del constructor: ese movimiento del vector sí se ejecuta.
- [ ] **Tras `Buffer(std::move(v))`, la variable v queda en un estado válido pero no especificado; el estándar prohíbe usar sus valores sin reasignarla antes, aunque no es undefined behavior acceder a ella (p. ej. llamar a v.size()).** — _correcta_: El estándar garantiza para los tipos de la biblioteca (como std::vector) que un objeto movido-desde queda en un estado válido pero no especificado; se puede seguir usando de forma segura (destruirlo, reasignarlo), pero su contenido no debe darse por supuesto.
- [ ] **std::move(v) por sí solo no garantiza que ocurra un movimiento real; solo produce un xvalue, y que se ejecute o no un move constructor/move assignment depende de si el tipo destino ofrece una sobrecarga aplicable para rvalue references.** — _correcta_: Es una trampa clásica: si el tipo destino no tiene constructor de movimiento (o no es noexcept y el compilador prefiere copiar en ciertos contextos), std::move puede acabar invocando una copia en su lugar.
- [ ] **Usar std::move(data) dentro del constructor de Buffer es un error, porque el parámetro `data` ya es una referencia rvalue al haberse construido a partir de std::move(v) en la llamada, por lo que se movería automáticamente sin necesidad de std::move.** — _incorrecta_: Un parámetro nombrado, aunque se haya inicializado desde una rvalue reference, es en sí mismo un lvalue dentro del cuerpo de la función. Es necesario aplicar std::move(data) explícitamente para que se mueva en vez de copiarse.

> La semántica de movimiento en C++17 se basa en la conversión de lvalues a xvalues mediante std::move, pero el movimiento real depende de la resolución de sobrecarga del tipo destino. Además, la copia elidida garantizada por C++17 solo aplica a la construcción del objeto devuelto directamente como prvalue, no a los movimientos internos que ocurren dentro de sus constructores.
>
> Repasar: `std::move, copia elidida garantizada (guaranteed copy elision), parámetros por valor y move constructors`

### ❌ Pregunta 4 — Sincronización y deadlocks en arquitecturas ROS 2 multi-nodo

Un nodo ROS 2 (rclpy) tiene un callback de suscripción que, al recibir un mensaje, invoca un servicio de otro nodo de forma síncrona con `client.call(request)` (bloqueante). El nodo se ejecuta con `rclpy.spin(node)` estándar (executor de un solo hilo). Al ejecutar, el programa se queda colgado indefinidamente en la primera llamada al servicio. ¿Cuál es la causa más probable?

```python
class MyNode(Node):
    def __init__(self):
        super().__init__('my_node')
        self.client = self.create_client(Trigger, 'do_thing')
        self.sub = self.create_subscription(String, 'in', self.cb, 10)

    def cb(self, msg):
        req = Trigger.Request()
        resp = self.client.call(req)  # bloqueante
```

- [ ] **La causa más probable es una incompatibilidad de QoS entre el cliente y el servidor del servicio, que impide que la petición llegue al servidor.** — _incorrecta_: Incorrecto: los servicios usan QoS por defecto compatibles entre cliente y servidor salvo configuración explícita distinta; además un problema de QoS normalmente provoca que el servidor nunca aparezca disponible, no un colgado tras iniciarse la llamada.
- [ ] **El método síncrono `client.call()` no existe en rclpy, por lo que el código lanzaría un error de atributo antes de llegar a bloquearse.** — _incorrecta_: Incorrecto: `Client.call()` sí existe en rclpy como variante bloqueante de `call_async()`, precisamente por eso es una trampa habitual: es fácil de usar y provoca este deadlock si el nodo se ejecuta con un solo hilo.
- [ ] **Basta con asignar el suscriptor y el cliente a distintos `MutuallyExclusiveCallbackGroup` manteniendo `rclpy.spin(node)` (SingleThreadedExecutor) para resolver el bloqueo.** — _incorrecta_: Incorrecto: los callback groups solo determinan qué callbacks pueden ejecutarse en paralelo cuando el executor tiene varios hilos; con un `SingleThreadedExecutor` solo se ejecuta un callback a la vez sin importar los grupos, así que el deadlock persiste.
- [x] **Los servicios en ROS 2 no admiten ser llamados desde dentro de un callback de suscripción por diseño de la API; el código debería reestructurarse para usar únicamente temporizadores.** — _incorrecta_: Incorrecto: la API sí permite llamar a servicios desde callbacks; el problema no es una restricción de diseño sino la falta de concurrencia del executor para procesar la respuesta mientras el callback está bloqueado.
- [ ] **El executor de un solo hilo está ocupado ejecutando el callback de la suscripción, por lo que nunca puede procesar simultáneamente la respuesta entrante del servicio; hace falta un executor multihilo (con callback groups adecuados) o usar `call_async` con un spin/executor separado.** — _correcta_: Correcto: con un `SingleThreadedExecutor`, mientras se ejecuta `cb()` no se puede procesar ningún otro evento (incluida la respuesta del servicio), y como `call()` espera bloqueando a que esa respuesta llegue, se produce un deadlock clásico de ROS 2.

> Es un antipatrón muy común en ROS 2: bloquear con una llamada síncrona a servicio dentro de un callback que corre en el mismo executor de un solo hilo que debe procesar la respuesta. La solución pasa por usar `MultiThreadedExecutor` con callback groups apropiados, o realizar la llamada de forma asíncrona (`call_async` + futuro) sin bloquear el hilo del executor.
>
> Repasar: `Deadlock por llamadas síncronas a servicio dentro de callbacks (SingleThreadedExecutor vs MultiThreadedExecutor, callback groups)`

### ✅ Pregunta 5 — Cuantización y optimización de modelos en TensorRT para edge

Estás desplegando un modelo de visión (por ejemplo, un detector de objetos) en una Jetson usando TensorRT. ¿Cuáles de las siguientes afirmaciones sobre cuantización INT8 y optimización del engine son correctas? (selecciona todas las que apliquen)

- [ ] **TensorRT garantiza que un modelo cuantizado a INT8 siempre tendrá mayor exactitud (accuracy) que su versión en FP16, ya que INT8 consume menos memoria.** — _incorrecta_: Es al contrario: INT8 reduce el rango dinámico y la precisión numérica frente a FP16, por lo que normalmente introduce cierta pérdida de exactitud que hay que validar; menor uso de memoria no implica mayor precisión.
- [x] **La fusión de capas (layer/tensor fusion), como combinar Conv + BatchNorm + ReLU en un único kernel, es una optimización que aplica el builder de TensorRT y reduce la latencia y los accesos a memoria, independientemente de la precisión usada.** — _correcta_: TensorRT aplica fusiones verticales y horizontales de capas durante la construcción del engine para reducir el número de kernels y lecturas/escrituras intermedias en memoria, en FP32, FP16 o INT8.
- [x] **La cuantización INT8 en TensorRT requiere, salvo que se use quantization-aware training (QAT) con rangos explícitos, una fase de calibración post-entrenamiento con un dataset representativo para determinar los rangos dinámicos de las activaciones.** — _correcta_: TensorRT usa un IInt8Calibrator (p. ej. entropy calibration) que recorre un conjunto de datos representativo para calcular los factores de escala por tensor, salvo que se proporcionen rangos ya calculados vía QAT/ONNX Q/DQ nodes.
- [x] **En una Jetson con núcleos Tensor compatibles, usar FP16 suele ofrecer un buen equilibrio entre velocidad y precisión, y no exige el paso de calibración que sí necesita INT8.** — _correcta_: FP16 conserva un rango dinámico mucho más cercano a FP32 que INT8 y no requiere calibración, mientras aprovecha los Tensor Cores para acelerar la inferencia, por lo que es una opción habitual antes de dar el salto a INT8.
- [ ] **Un engine serializado de TensorRT construido en una Jetson Xavier es totalmente portable y puede ejecutarse sin recompilar en una Jetson Orin, siempre que se use la misma versión de TensorRT.** — _incorrecta_: Los engines de TensorRT están optimizados para la arquitectura de GPU concreta (y versión de TensorRT/CUDA/cuDNN) sobre la que se construyeron; al cambiar de arquitectura (p. ej. Volta a Ampere) normalmente hay que reconstruir el engine.

> TensorRT optimiza modelos para edge combinando fusión de capas, selección de kernels y precisión reducida (FP16/INT8). INT8 exige calibración (o QAT) por su menor rango dinámico y no garantiza mejor precisión, y los engines generados son específicos de la arquitectura de GPU y versión de TensorRT usadas en la construcción.
>
> Repasar: `Calibración INT8, layer fusion, portabilidad de engines TensorRT`
