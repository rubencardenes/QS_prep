# Plan de preparación — Senior AI Software Engineer @ Quantum Systems

**Perfil del puesto:** visión por computador en sistemas no tripulados (drones, marítimos, terrestres). Llevar algoritmos de CV de prototipo a producción sobre hardware embebido. Claves de la oferta: **C++ moderno, NVIDIA Jetson / embedded, Computer Vision (tradicional + Deep Learning), OpenCV, ROS2, optimización sobre hardware real, integración de sensores/gimbals**.

**Tu situación:** 2 días, refrescar todo, formato del test aún desconocido. Este plan prioriza lo que más probablemente caiga en un ejercicio de ~1h en coderpad y lo que más te ayuda en la entrevista técnica.

---

## Prioridades (dónde invertir el tiempo)

Un ejercicio de coderpad para este rol casi siempre es **C++ + algún problema de procesamiento de imagen o estructura de datos**, no montar TensorRT en vivo (eso no cabe en coderpad). Por eso:

1. **C++ moderno fluido** — es lo que vas a *escribir* en vivo. Máxima prioridad.
2. **Fundamentos de CV / OpenCV** — probable tema del enunciado; te lo preguntan y quizá lo implementas a mano.
3. **Jetson / embedded / optimización** — más para la conversación y preguntas de diseño que para teclear. Repaso conceptual.
4. **ROS2** — mencionar que lo conoces; poco probable en coderpad.

---

## DÍA 1 — C++ moderno + fundamentos de CV

### Bloque 1 (2–3 h): C++ moderno, lo esencial

Repasa y **escribe código** de cada punto (no solo leer):

- **Gestión de memoria y RAII:** `std::unique_ptr`, `std::shared_ptr`, `std::make_unique`, cuándo cada uno. Regla de oro: nada de `new`/`delete` crudos.
- **Move semantics:** `std::move`, rvalue references (`&&`), copy vs move, la *rule of 0/3/5*. Por qué importa en código de alto rendimiento (evitar copias de imágenes/buffers).
- **STL contenedores y algoritmos:** `vector`, `unordered_map`, `map`, `set`; `std::sort`, `std::find`, `std::accumulate`, `std::transform`, `std::for_each`. Complejidad de cada operación.
- **Lambdas y `std::function`:** captura por valor/referencia, uso con algoritmos STL.
- **`auto`, range-based for, structured bindings** (`auto [k, v] : map`).
- **`const` correctness, referencias vs punteros, `constexpr`.**
- **Templates básicos** y `std::optional`, `std::variant`, `std::string_view` (C++17).
- **Concurrencia mínima:** `std::thread`, `std::mutex`, `std::atomic` — saber explicarlo aunque no lo teclees.

Ejercicio práctico: implementa una clase `Matrix`/`Image` sencilla (buffer contiguo `std::vector<uint8_t>`, acceso `at(row,col)`, move constructor). Es exactamente el tipo de warm-up que pueden pedir.

### Bloque 2 (2–3 h): Computer Vision tradicional

Entiende el *qué* y el *cuándo*, y sé capaz de implementar los básicos a mano:

- **Representación de imagen:** matriz H×W×C, tipos de dato (`uint8`, `float32`), row-major, stride/padding, espacios de color (RGB, BGR —ojo, OpenCV usa BGR—, grayscale, HSV).
- **Convolución y filtros:** kernel 2D, cómo se computa; blur (media, gaussiano), Sobel/gradientes, bordes (Canny a alto nivel). **Sé implementar una convolución/box blur a mano** — cae mucho.
- **Thresholding** (binarización, Otsu a alto nivel), operaciones morfológicas (erosión/dilatación).
- **Detección de features:** esquinas (Harris), keypoints (ORB/SIFT a nivel conceptual), qué es un descriptor y para qué sirve el matching.
- **Transformaciones geométricas:** afín vs homografía, warping, interpolación (nearest, bilinear).
- **Histogramas** y ecualización.
- **Pipeline mental:** captura → preproceso → detección/segmentación → post-proceso → tracking.

Ejercicio práctico: implementa en C++ puro (sin OpenCV) un **box blur 3×3** o un **umbral binario** sobre tu clase `Image`. Cronométrate.

---

## DÍA 2 — OpenCV + Jetson/embedded + simulacro

### Bloque 3 (2 h): OpenCV en la práctica

Ten fresca la API C++, aunque el patrón se parece en Python:

- **`cv::Mat`:** creación, tipos (`CV_8UC3`, `CV_32FC1`), acceso a píxeles (`at<>()`, punteros de fila `ptr<>()`), ROI, clonado vs referencia (¡`Mat` comparte datos por defecto!).
- **I/O:** `imread`, `imwrite`, `imshow`, `VideoCapture`.
- **Operaciones núcleo:** `cvtColor`, `resize`, `GaussianBlur`, `threshold`, `Canny`, `findContours`, `warpAffine`/`warpPerspective`, `matchTemplate`.
- **DNN module:** `cv::dnn::readNet`, `blobFromImage`, `forward` — cómo cargar un ONNX y correr inferencia. Menciona que en Jetson lo suyo es TensorRT, no el DNN de OpenCV.
- **Rendimiento:** OpenCV usa BGR; conversiones cuestan; evita copias; usa `UMat`/CUDA modules si hay GPU.

Repasa las *gotchas*: BGR vs RGB, índices `(y,x)` vs `(x,y)`, `Mat` como vista compartida.

### Bloque 4 (1.5 h): Jetson / embedded / optimización — nivel conversación

No lo teclearás, pero te lo preguntarán. Ten un relato claro de:

- **Familia Jetson:** Nano / Xavier NX / Orin (Orin es lo actual). GPU NVIDIA + CPU ARM64, memoria unificada CPU-GPU.
- **Stack de deployment:** entrenas en PyTorch/TF → exportas a **ONNX** → optimizas con **TensorRT** (fusión de capas, precisión reducida **FP16/INT8**, calibración INT8) → runtime en el dispositivo. **DeepStream** para pipelines de vídeo multi-stream.
- **Optimización en el edge:** cuantización (FP16/INT8), pruning, batch size, uso de **NVENC/NVDEC** para codec por hardware, **zero-copy** con memoria unificada, `nvpmodel` y `jetson_clocks` para gestionar potencia/frecuencia, monitorización con `tegrastats`/`jtop`.
- **Cuellos de botella típicos:** transferencias CPU↔GPU, preproceso en CPU, I/O de cámara, térmica/consumo. Cómo medirlos y atacarlos.
- **Integración de sensores/gimbals:** latencia, sincronización temporal (timestamps), throughput, pipeline GStreamer para la cámara.
- **ROS2 (menciónalo):** nodos, topics, `rclcpp`, `sensor_msgs/Image`, QoS, por qué ROS2 (DDS, tiempo real) frente a ROS1.

Prepara **2–3 anécdotas propias** ("cómo optimicé X de N ms a M ms", "cómo integré un modelo en dispositivo"). Es un rol de "prototipo → producción": valoran historias de deployment real.

### Bloque 5 (1.5–2 h): Simulacro en coderpad

Haz un ensayo real (ver estrategia abajo). Resuelve 1–2 problemas cronometrados en [coderpad.io](https://coderpad.io) (tienen sandbox de práctica) o en un editor a pelo. Ideas de problemas representativos:

- Implementar convolución / box blur / detección de bordes sobre una matriz.
- Rotar una imagen (matriz) 90°, flip, transpuesta in-place.
- Contar componentes conexas / flood fill (islas) — clásico y muy "visión".
- Non-Maximum Suppression (NMS) de bounding boxes — muy de detección de objetos, cae en roles de CV.
- IoU entre dos cajas.
- Sliding window / promedio móvil 2D.

---

## Estrategia para el test en coderpad.io

**Antes:**

- Entra 5 min antes. Prueba el entorno: coderpad ejecuta código real — selecciona **C++** y confirma que compilas y ves stdout. Conoce el atajo de *Run* y que el `main()` con prints es tu forma de depurar.
- Ten a mano una plantilla mental de C++: includes (`<vector>`, `<iostream>`, `<algorithm>`, `<unordered_map>`), `using namespace std;` (aceptable en entrevista para ir rápido), un `main` con casos de prueba.

**Durante — el patrón que evalúan (comunicación > solución perfecta):**

1. **Reformula el problema** en voz alta y confirma con el entrevistador. Pregunta por restricciones: tamaño de entrada, tipos, bordes, memoria.
2. **Da ejemplos** de entrada/salida antes de codear. Acuerda el caso feliz y los edge cases (imagen vacía, 1 píxel, bordes de la convolución).
3. **Propón enfoque y complejidad** (tiempo/espacio) *antes* de teclear. Menciona la solución fuerza bruta y luego la óptima.
4. **Piensa en voz alta mientras codeas.** El silencio penaliza más que un fallo. Verbaliza decisiones ("uso `unordered_map` por O(1) medio").
5. **Escribe código limpio:** nombres claros, funciones pequeñas, RAII, sin fugas. En C++ demuestra que dominas STL y punteros inteligentes: es tu señal de seniority.
6. **Prueba tú mismo:** añade 2–3 casos en `main`, ejecuta, razona el output. Trata los edge cases explícitamente.
7. **Optimiza si sobra tiempo** y comenta trade-offs (legibilidad vs rendimiento, cache-friendliness, evitar copias).

**Gestión del tiempo (ejercicio ~45–60 min):** ~5 min entender + ejemplos, ~5 min diseño, ~25–30 min código, ~10 min pruebas y refactor, ~5 min discusión/optimización. Si te atascas, di tu bloqueo en voz alta y propón un plan B.

**Errores a evitar:** empezar a teclear sin acordar el enfoque; quedarte callado; ignorar edge cases; sobre-optimizar antes de tener algo que funcione; fugas de memoria o `new` sin `delete`.

**Señales de seniority que buscan:** hablar de complejidad, de rendimiento en hardware embebido, de precisión numérica (`uint8` overflow al sumar píxeles → usa `int`/clamp), de por qué una estructura y no otra, y de cómo lo testearías en producción.

---

## Cómo usar Claude Code de forma eficiente

Claude Code es tu compañero de terminal para **preparar** el ejercicio (no lo uses de forma que viole las reglas del test en vivo — pregunta si se permite; normalmente el entrevistador observa y no está permitido).

**Para preparar estos 2 días:**

- **Monta un repo de práctica** y pídele que ande contigo: `mkdir prep && cd prep && claude`. Luego pídele por ejemplo: *"Genera 5 ejercicios de coderpad tipo CV en C++ con enunciado y tests, de dificultad creciente, sin darme la solución todavía."*
- **Práctica activa, no pasiva:** resuelve tú, y usa Claude para **revisar**: *"Revisa mi implementación de box blur: corrección, edge cases, estilo C++ moderno y rendimiento."* Pide crítica de senior, no solo el "está bien".
- **Refresca conceptos a demanda:** *"Explícame move semantics con un ejemplo de una clase Image que evite copias de buffer."* o *"Enséñame la API C++ de cv::Mat con los gotchas de BGR y vistas compartidas."*
- **Tarjetas de repaso:** *"Hazme un quiz rápido de 15 preguntas sobre Jetson/TensorRT/optimización edge, una a una, y corrígeme."*
- **Simulacro de entrevista:** *"Hazme de entrevistador: dame un problema de NMS, no me des la solución, hazme preguntas de seguimiento y evalúa mi comunicación."*
- **Monta un mini-proyecto realista** que puedas comentar en la entrevista: un pipeline en C++/OpenCV que cargue una imagen, detecte contornos y dibuje cajas; pídele ayuda para estructurarlo con CMake. Tener algo tuyo que enseñar vale oro.

**Reglas para que sea eficiente:**

- Dale **contexto una vez** (crea un `CLAUDE.md`: "estoy preparando entrevista de Senior AI SW Eng, foco C++/CV/Jetson, quiero que me trates como senior y me hagas pensar").
- Pide **una cosa concreta por vez** y con formato ("dame solo el esqueleto", "solo revisa, no reescribas").
- Úsalo para **explicar errores de compilación** y para **profundizar** ("¿por qué esto es UB?", "¿coste de esta copia?").
- **No** dependas de él durante el test en vivo si el entrevistador observa: se nota y suele estar prohibido. Su valor es dejarte afilado *antes*.

---

## Checklist rápido pre-test

- [ ] Compilo y ejecuto C++ en coderpad sin dudar (includes + main + Run).
- [ ] Implemento a mano: convolución/blur, threshold, flood fill, NMS, IoU, rotación de matriz.
- [ ] Domino smart pointers, move semantics, STL y su complejidad.
- [ ] Sé el flujo Jetson: PyTorch → ONNX → TensorRT (FP16/INT8) → runtime; DeepStream; tegrastats.
- [ ] Gotchas OpenCV: BGR, `Mat` comparte datos, índices (y,x), overflow uint8.
- [ ] Tengo 2–3 anécdotas de "prototipo → producción" y de optimización.
- [ ] Practico comunicar en voz alta: reformular, ejemplos, complejidad, tests.
- [ ] Menciono ROS2 con soltura (nodos, topics, rclcpp, QoS).
