# Jetson + Drones + ROS2 — Preguntas y respuestas de entrevista

Formato: pregunta → respuesta corta (lo que dirías en voz alta) → detalle/matices para profundizar.
Los términos técnicos van en inglés porque así te los van a preguntar.

---

# PARTE 1 — NVIDIA Jetson

## 1.1 Hardware y familia

### P: ¿Qué es un Jetson y en qué se diferencia de una GPU de escritorio?

**Corto:** Es un SoC Tegra (SOM, System on Module) con CPU ARM64 + GPU NVIDIA + aceleradores fijos en el mismo chip, y **memoria física unificada** entre CPU y GPU.

**Detalle:**
- En un PC con GPU discreta hay dos memorias separadas y un bus PCIe en medio → todo dato que quieras procesar en GPU pasa por `cudaMemcpy`. En Jetson **la RAM es la misma**, así que el copy CPU↔GPU se puede eliminar (zero-copy) si usas el tipo de memoria correcto.
- El SOM se monta sobre una *carrier board* (NVIDIA devkit, o de terceros: Auvidea, Connect Tech, Leopard Imaging). En un dron casi siempre es carrier board custom o de tercero, más pequeña y ligera que el devkit.
- Además de CPU y GPU hay bloques dedicados: **NVENC/NVDEC** (codec H.264/H.265 por hardware), **DLA** (Deep Learning Accelerator), **PVA** (Programmable Vision Accelerator), **VIC** (Video Image Compositor: resize, conversión de formato, composición), **ISP** (procesado de la cámara MIPI).

### P: ¿Qué modelos conoces y cuál elegirías para un dron?

| Módulo | GPU | Potencia | INT8 (aprox.) | Notas |
|---|---|---|---|---|
| Jetson Nano | Maxwell 128 cores | 5–10 W | ~0.5 TFLOPS | Legacy, sin tensor cores. No lo elijas hoy. |
| Xavier NX | Volta 384 cores | 10–20 W | ~21 TOPS | Generación anterior, aún en campo. |
| **Orin Nano 4/8 GB** | Ampere 1024 cores | 7–25 W | 40 TOPS (67 en "Super") | **Sin NVENC** (solo decode) y **sin DLA**. |
| **Orin NX 8/16 GB** | Ampere 1024 cores | 10–25 W | ~70–100 TOPS | Tiene NVENC y DLA. El *sweet spot* en drones. |
| **AGX Orin 32/64 GB** | Ampere 2048 cores | 15–60 W | 200–275 TOPS | Potente pero pesado y caliente para un UAV pequeño. |
| Jetson Thor | Blackwell | ~40–130 W | — | Generación nueva, orientada a robótica/humanoides. |

**Nota sobre las unidades — TOPS vs TFLOPS.** Ambas son 10¹² operaciones por segundo (un MAC cuenta como 2 ops); la diferencia es el tipo de dato: **TFLOPS** = coma flotante (FP32/FP16), **TOPS** = enteros, en la práctica INT8. El Nano se mide en TFLOPS FP16 porque su GPU Maxwell **no tiene tensor cores ni ruta INT8 acelerada**; de Xavier en adelante sí, y por eso se publica en TOPS INT8. Equivalencia aproximada en tensor cores: `INT8 ≈ 2 × FP16 ≈ 4 × FP32`.

Tres matices: (1) los TOPS de Ampere que publica NVIDIA suelen ser **con structured sparsity 2:4**, que dobla la cifra → 40 TOPS del Orin Nano son ~20 densos; (2) es un **pico teórico** (`unidades MAC × 2 × frecuencia`) y la mayoría de las capas están limitadas por ancho de banda de memoria, no por cómputo → eficiencias reales del 10–40 %; (3) **no dimensiones nunca un sistema con TOPS**: sirven para descartar módulos, no para elegirlos. Se mide con `trtexec` en el hardware real.

**Corto:** "Para un dron mediano, **Orin NX 16 GB**: tiene encoder por hardware y DLA, entra en ~15–25 W y deja margen de memoria para varios modelos. Orin Nano si el presupuesto de peso/potencia es muy justo, asumiendo que no tengo NVENC y que tendré que codificar de otra forma o no codificar."

**El matiz que impresiona:** *el Orin Nano no tiene encoder de vídeo por hardware*. Si tu producto necesita grabar o hacer downlink de H.265, eso cambia la elección de módulo. Es exactamente el tipo de detalle que separa a quien ha desplegado de quien ha leído la web.

### P: ¿Qué es el DLA y cuándo lo usarías?

**Corto:** Un acelerador de inferencia de función fija, independiente de la GPU. Es mucho más eficiente en W/inferencia pero soporta un subconjunto de capas y solo FP16/INT8.

**Detalle:**
- Uso típico: mover una red "secundaria" y estable (p. ej. el detector principal) al DLA y **dejar la GPU libre** para preproceso CUDA, otra red o SLAM. Es paralelismo real, no time-slicing.
- Se activa en TensorRT con `--useDLACore=0 --allowGPUFallback`. Cuidado: si muchas capas caen en fallback a GPU, el troceo genera copias y puede salir **más lento** que solo GPU. Hay que mirar el log de build capa por capa.
- El Orin Nano no tiene DLA.

### P: ¿Qué es JetPack?

**Corto:** El SDK de NVIDIA para Jetson: **L4T** (Linux for Tegra: kernel + BSP + drivers, sobre Ubuntu) más CUDA, cuDNN, TensorRT, VPI, la Multimedia API y DeepStream.

**Detalle:** La versión de JetPack determina versión de CUDA/TensorRT y qué módulos soporta (JetPack 5 → Ubuntu 20.04; JetPack 6 → Ubuntu 22.04 y separa el BSP del rootfs, lo que facilita usar tu propia distro). Flasheo con SDK Manager o `flash.sh`; en producción se usan imágenes propias y **OTA updates con A/B rootfs** para no ladrillar un dron en el campo.

---

## 1.2 Deployment e inferencia

### P: Describe el flujo de llevar un modelo de entrenamiento a un Jetson.

**Corto:** PyTorch → export a **ONNX** → build de un **engine TensorRT en el propio dispositivo** (FP16 o INT8) → runtime en C++ con pre/post-proceso en CUDA.

**Detalle paso a paso:**
1. **Export ONNX**: fijar `opset`, decidir shapes estáticos vs dinámicos, simplificar el grafo (`onnxsim`). Verificar paridad numérica PyTorch vs ONNX Runtime antes de seguir.
2. **Build del engine**: `trtexec --onnx=m.onnx --saveEngine=m.plan --fp16` o con la API C++ (`IBuilder`, `INetworkDefinition`, `IBuilderConfig`). TensorRT hace *layer & tensor fusion*, elimina capas muertas, elige el kernel más rápido para tu GPU (*kernel autotuning*) y aplica la precisión pedida.
3. **El engine NO es portable**: está atado a la arquitectura GPU, versión de TensorRT y a veces al modelo exacto. Se compila **en el target** (o en un contenedor idéntico) y se versiona junto al firmware. Es un fallo clásico llevarse el `.plan` del portátil al dron.
4. **Runtime**: `IRuntime::deserializeCudaEngine` → `IExecutionContext` → bindings de entrada/salida en device memory → `enqueueV3(stream)` asíncrono.
5. **Warm-up**: las primeras inferencias son lentas (allocations, cachés). Haz 10–20 iteraciones antes de medir o de entrar en operación.

### P: FP32 vs FP16 vs INT8 — ¿qué usas y qué cuesta?

**Corto:** FP16 es la opción por defecto: ~2× de throughput y mitad de memoria con pérdida de precisión casi siempre despreciable. INT8 da otro ~2× pero requiere **calibración** y validación de mAP.

**Detalle:**
- **FP16**: los tensor cores lo ejecutan nativamente. Riesgo: overflow/underflow en capas con rangos grandes (a veces hay que mantener alguna capa en FP32 → *mixed precision*).
- **INT8**: TensorRT necesita conocer el rango dinámico de cada tensor. Dos vías:
  - **PTQ (post-training quantization)**: le das un *calibration dataset* de unas 500–1000 imágenes **representativas del dominio real** (misma cámara, misma altura, mismas condiciones de luz) y usa entropy calibration para elegir las escalas.
  - **QAT (quantization-aware training)**: simulas la cuantización durante el entrenamiento; más trabajo pero recupera casi toda la precisión en modelos sensibles.
- **Cómo lo defiendo en la entrevista:** "cuantizo, y luego mido mAP en un set de validación del dominio. Si la caída es <1 punto, me lo quedo; si no, miro qué capas son sensibles y las dejo en FP16."
- Ampere además soporta **structured sparsity 2:4** (los TOPS que anuncia NVIDIA suelen ser con sparsity); solo aplica si has entrenado el modelo podado con ese patrón.

### P: ¿Cómo mides el rendimiento de verdad?

**Corto:** Distingo **latencia** (end-to-end, p50/p95/p99) de **throughput** (FPS). En un dron manda la latencia y la cola, no la media.

**Detalle:**
- Instrumento el pipeline completo: captura → copia → preproceso → inferencia → post-proceso → salida. `cudaEvent` para tramos GPU, `std::chrono::steady_clock` para CPU, y **Nsight Systems** para ver el timeline y los huecos.
- `trtexec` te da la latencia del modelo aislado; nunca es la del sistema. La diferencia entre ambas es donde vive el problema.
- Métricas del sistema: `tegrastats` / `jtop` (uso de GPU, EMC = ancho de banda de memoria, temperatura, y si hay throttling).
- **Reporta percentiles**: "media 18 ms, p99 34 ms" dice mucho más que "55 FPS". Un p99 malo en un lazo de control de gimbal es un fallo aunque la media sea buena.

### P: Tienes un pipeline a 12 FPS y necesitas 30. ¿Qué haces?

**Corto:** Primero mido dónde se va el tiempo; no optimizo a ciegas. El orden típico de culpables es: preproceso en CPU, copias CPU↔GPU, el modelo, y el post-proceso (NMS).

**Detalle — checklist mental:**
1. **Perfilar** con Nsight Systems: ¿la GPU está al 30 % esperando? Entonces el cuello está en CPU o en I/O, no en el modelo.
2. **Preproceso**: resize + normalize + HWC→CHW en CPU con OpenCV es lentísimo a 4K. Muévelo a CUDA, a **VPI**, o al **VIC** (resize/format conversion gratis en términos de GPU).
3. **Copias**: eliminar `cudaMemcpy` usando memoria unificada/pinned (ver siguiente pregunta).
4. **Modelo**: FP16 → INT8; input más pequeño (de 1280 a 640 es 4× menos cómputo); backbone más ligero; mover una red al DLA.
5. **Solapamiento**: CUDA streams + `enqueueV3` asíncrono para que la captura del frame N+1 se solape con la inferencia del N. Doble/triple buffering.
6. **Batching**: solo si tienes varias cámaras. Con una sola cámara, batch>1 aumenta latencia y no ayuda.
7. **Algorítmico**: no inferir en todos los frames — detectar cada N frames y **trackear** en medio (IoU/KCF/NvDCF). Suele ser la mejora más grande y la más barata.
8. **Sistema**: `nvpmodel` al modo de máxima potencia si el presupuesto lo permite, `jetson_clocks` para fijar frecuencias. Comprobar que no hay thermal throttling.

**Frase de cierre:** "y vuelvo a medir después de cada cambio, porque el cuello se mueve."

### P: ¿Qué significa "zero-copy" en Jetson y cómo se consigue?

**Corto:** Como la RAM es física y compartida, se puede tener un buffer accesible por CPU y GPU sin copiarlo — pero **no ocurre automáticamente**: depende de cómo asignes la memoria.

**Detalle:**
- `cudaMalloc` → device-only, requiere `cudaMemcpy` desde host. Es lo que hace todo el mundo por costumbre y es innecesario en Tegra.
- `cudaHostAlloc(..., cudaHostAllocMapped)` → pinned + mapeada: la GPU lee directamente la memoria del host. Zero-copy real.
- `cudaMallocManaged` → unified memory; en Tegra es coherente y cómoda, aunque puede tener coste de sincronización.
- En pipelines de vídeo, los buffers viven en **NVMM** (`NvBufSurface`): el ISP, NVDEC, VIC, la GPU y NVENC se pasan el mismo buffer por handle sin que los píxeles bajen nunca a memoria de CPU. Eso es lo que hace que DeepStream escale a muchas cámaras.
- **Ojo con la caché**: con memoria mapeada hay que respetar la coherencia (sync de caché) o leerás datos rancios.

### P: ¿Qué es DeepStream y cuándo lo usarías?

**Corto:** Un framework sobre GStreamer con plugins NVIDIA (`nvv4l2decoder`, `nvstreammux`, `nvinfer`, `nvtracker`, `nvdsosd`) que mantiene los frames en NVMM de principio a fin.

**Cuándo sí:** varias cámaras/streams, necesitas decode → inferencia → tracking → encode/streaming con mínimo CPU. Te da batching multi-stream y tracking (IoU, NvDCF, DeepSORT) prácticamente gratis.

**Cuándo no:** un pipeline muy custom, con lógica algorítmica pesada entre etapas o integración fuerte con ROS2. GStreamer es rígido y depurar un pipeline complejo es doloroso. En ese caso: **VPI/CUDA a mano + TensorRT**, o **Isaac ROS**.

### P: ¿Qué es VPI?

**Corto:** *Vision Programming Interface*: librería de CV de NVIDIA con la misma API para varios backends — CPU, CUDA, **PVA**, **VIC**, **OFA** — de modo que puedes mover un remap, un pyramid LK optical flow o un stereo disparity al acelerador que esté libre.

**Por qué importa en un dron:** te permite descargar trabajo de la GPU (ocupada con la red) hacia bloques fijos que si no estarían ociosos. Ejemplo clásico: **lens distortion correction en el VIC** en lugar de `cv::remap` en CPU.

### P: Gestión de potencia y térmica.

- `nvpmodel -m <n>`: selecciona un *power mode* (número de cores activos, frecuencias máximas de CPU/GPU/EMC). `nvpmodel -q` para consultar.
- `jetson_clocks`: fija todos los relojes al máximo del modo actual y **desactiva el DVFS**. Elimina jitter de latencia — útil para medir y para lazos de control — a costa de consumo y calor.
- `tegrastats` / `jtop`: uso por bloque, temperaturas, y si estás en throttling.
- **En un dron esto no es teoría:** la potencia sale de la batería y sale del tiempo de vuelo. Y en altitud el aire es menos denso → un disipador pasivo enfría peor de lo que dice la hoja de datos. Diseño térmico (contacto con el chasis, airflow de las hélices) y **vigilar `THERMAL_THROTTLE`** en telemetría, porque el síntoma en campo es "el detector va lento solo después de 10 minutos de vuelo".

---

## 1.3 Cámara y vídeo en el dron

### P: ¿Cómo entra la imagen de la cámara al Jetson?

- **MIPI CSI-2**: la vía buena. Pasa por el **ISP** (debayer, AWB, exposición) y aterriza en NVMM. Se accede con **libargus** o con GStreamer `nvarguscamerasrc`. Requiere un driver del sensor en el kernel (el famoso "device tree").
- **GMSL/FPD-Link**: serializadores para cables largos y robustos (típico en vehículos y drones grandes).
- **USB/UVC**: `v4l2src`, fácil pero con latencia peor y coste de CPU; suele venir ya en MJPEG o H.264, lo que añade decode.
- **Ethernet/GigE**: cámaras industriales; buena para carga útil, ojo al ancho de banda y al jitter.

### P: Global shutter vs rolling shutter en un dron.

**Corto:** En un dron quieres **global shutter** para cualquier cosa geométrica.

**Por qué:** el rolling shutter expone las filas en instantes distintos; con vibración de motores y movimiento rápido produce sesgo/"jello". Eso destroza la triangulación en VIO/SLAM y la fotogrametría, y desplaza las bounding boxes. Para vídeo de operador puede valer; para navegación, no.

### P: ¿Cómo sincronizas cámara e IMU?

**Corto:** Con **trigger hardware** y timestamps de una sola fuente de reloj. El software timestamp del driver ya llega tarde y con jitter.

**Detalle:** El error de sincronización cámara-IMU es el enemigo número uno del VIO — unos pocos ms se traducen en drift. Opciones: trigger desde el flight controller (que también sella la IMU), **PTP** si hay Ethernet, o estimar el offset online (VINS-Mono y Kalibr lo hacen). En ROS2, ojo a la diferencia entre el `header.stamp` (tiempo de captura, el que vale) y el tiempo de recepción del mensaje.

### P: ¿Qué mandas por el radioenlace?

**Corto:** Metadatos, no vídeo crudo. Inferencia a bordo → mandar detecciones/tracks (bytes) y vídeo comprimido con bitrate adaptativo solo si el operador lo necesita.

**Detalle:** El enlace es el recurso más escaso y el que peor se degrada. H.265 vía NVENC, RTP/SRT, GOP corto para recuperación rápida ante pérdidas, y degradación elegante (baja resolución/framerate antes que cortar). El sistema debe seguir siendo funcional **con el enlace caído**: esa es la razón de ser del cómputo a bordo.

---

## 1.4 Preguntas de diseño típicas

### P: Diseña un sistema de detección y seguimiento de objetos a bordo de un dron con un Orin NX.

Estructura la respuesta así:

1. **Requisitos primero**: ¿latencia objetivo? ¿resolución? ¿tamaño mínimo del objeto en píxeles? ¿presupuesto de potencia? ¿qué se hace con la salida (mostrar al operador vs cerrar un lazo de gimbal)?
2. **Pipeline**: CSI camera → NVMM → (resize/undistort en VIC/VPI) → TensorRT INT8 (detector tipo YOLO) → NMS en GPU → tracker (IoU/Kalman/NvDCF) → salida (ROS2 topic + overlay + NVENC para downlink).
3. **Trucos de presupuesto**: detección cada N frames + tracking en medio; ROI/tiling solo si hay objetos pequeños; doble buffering con CUDA streams.
4. **Lo difícil de verdad**: objetos pequeños (un objeto a 100 m ocupa 10 px → el downscale a 640 lo mata; de ahí el tiling), cambio de escala brutal según la altura, motion blur, autoexposición cuando apuntas al cielo, y el hecho de que **la cámara se mueve** (el ego-motion rompe cualquier asociación basada solo en posición → compensa con homografía o con la actitud del gimbal/IMU).
5. **Validación**: dataset del dominio real, métricas por rango de distancia, y test en HIL/replay de logs antes de volar.

### P: ¿Cómo pasarías un prototipo de Python a producción en el dron?

Esta pregunta es literalmente la descripción del puesto. Respuesta:

- **Congelar la referencia**: el prototipo Python es la *golden reference*; guardo un set de entradas/salidas para comparar bit a bit (o dentro de tolerancia) contra el port en C++.
- **Portar por capas**: primero el modelo (ONNX → TensorRT) validando numéricamente, después el pre/post-proceso (aquí es donde aparecen los bugs de verdad: BGR/RGB, orden de normalización, resize con distinto tipo de interpolación, letterbox mal alineado).
- **Ingeniería**: C++17, RAII para los recursos CUDA/TensorRT, sin allocations en el hot loop (buffers preasignados), threading con colas acotadas y política de *drop* del frame viejo (nunca acumular latencia).
- **Producción**: tests unitarios + test de regresión sobre bags grabados, CI que compile para ARM64 (cross-compile o runner nativo), contenedores, logging estructurado, watchdog, y degradación segura si el modelo no responde.
- **Medir en el hardware real desde el día uno.** El portátil miente.

---

# PARTE 2 — ROS2

## 2.1 Fundamentos

### P: ¿Qué cambia en ROS2 respecto a ROS1?

**Corto:** No hay `roscore` (descubrimiento distribuido vía **DDS**), hay **QoS** configurable, **nodos con ciclo de vida**, composición en un mismo proceso con **intra-process zero-copy**, seguridad (SROS2) y un diseño pensado para tiempo real y sistemas multi-robot.

**Detalle:** ROS2 no habla un protocolo propio: se apoya en DDS a través de la capa **RMW** (Fast DDS por defecto en Humble, Cyclone DDS como alternativa muy usada en embebido). Eso elimina el punto único de fallo del master, pero introduce el mundo de la configuración DDS (discovery, multicast, buffers UDP), que es donde se va el tiempo de depuración.

### P: Topics vs services vs actions.

| | Uso | Semántica |
|---|---|---|
| **Topic** | Flujo de datos: imágenes, IMU, odometría | Pub/sub, asíncrono, N a N, sin garantía de que alguien escuche |
| **Service** | Consulta rápida: "dame el estado", "cambia de modo" | Request/response, bloqueante conceptualmente, 1 a 1 |
| **Action** | Tarea larga y cancelable: "vuela a este waypoint" | Goal + feedback periódico + result + cancel |

**Regla:** si tarda y quieres poder abortarlo, es una action. Nunca hagas una llamada a service síncrona dentro de un callback en un executor single-threaded → **deadlock** (clásico de entrevista).

### P: Explica QoS y por qué me importa en un dron.

**Corto:** QoS es el contrato entre publisher y subscriber. Si no son compatibles, **simplemente no se conectan y no hay error evidente** — es el fallo número uno de ROS2.

**Policies principales:**
- **Reliability**: `RELIABLE` (retransmite hasta confirmar) vs `BEST_EFFORT` (no reintenta). Para vídeo/IMU a alta frecuencia y sobre WiFi: best effort — un frame perdido no importa, un pipeline atascado sí.
- **Durability**: `VOLATILE` vs `TRANSIENT_LOCAL` (el que llega tarde recibe los últimos mensajes; el equivalente al *latched* de ROS1). Útil para mapas, `camera_info`, configuración estática.
- **History**: `KEEP_LAST(depth)` vs `KEEP_ALL`. Depth pequeño (1–5) en sensores: prefieres el frame más reciente antes que una cola de frames viejos.
- **Deadline / Liveliness / Lifespan**: detectar que un sensor dejó de publicar o descartar datos caducados. En un dron, *liveliness* es un mecanismo real de detección de fallo.

**Compatibilidad:** el subscriber no puede pedir más de lo que ofrece el publisher. Publisher `BEST_EFFORT` + subscriber `RELIABLE` = no hay conexión. Diagnóstico: `ros2 topic info -v /topic` muestra los QoS de cada extremo.

```cpp
auto qos = rclcpp::QoS(rclcpp::KeepLast(5)).best_effort().durability_volatile();
auto sub = create_subscription<sensor_msgs::msg::Image>("/cam/image_raw", qos, cb);
// o directamente el perfil predefinido:
auto qos2 = rclcpp::SensorDataQoS();   // best_effort + keep_last(5)
```

### P: ¿Qué son los executors y los callback groups?

**Corto:** El executor es quien saca los callbacks de la cola y los ejecuta. Single-threaded por defecto → **todos tus callbacks se serializan**, y un callback lento bloquea el resto.

**Detalle:**
- `MultiThreadedExecutor` + **callback groups**: `MutuallyExclusive` (los callbacks del grupo no se solapan entre sí) o `Reentrant` (pueden ejecutarse en paralelo, y tú te encargas de la sincronización).
- Patrón típico: la inferencia pesada en su propio grupo reentrante, el timer de control en un grupo aparte para que nunca se retrase.
- Regla de oro embebida: **el callback no hace trabajo pesado**. Copia/encola y devuelve; un worker thread procesa. Si no, se te llenan las colas DDS y la latencia crece sin techo.

### P: ¿Qué es un lifecycle node y por qué usarlo?

**Corto:** Un nodo con máquina de estados gestionada — `unconfigured → inactive → active → finalized` — con transiciones `configure/activate/deactivate/cleanup/shutdown`.

**Por qué en un dron:** puedes asignar recursos (abrir la cámara, cargar el engine TensorRT, que tarda segundos) en `on_configure` y **no empezar a publicar** hasta `on_activate`. Eso te da arranque determinista y ordenado, y la posibilidad de desactivar un subsistema en vuelo sin matar el proceso. Es una señal clara de que has hecho sistemas de verdad.

### P: Explica TF2.

**Corto:** El árbol de transformadas: cada nodo publica la transformada entre dos frames con timestamp, y cualquiera puede preguntar "¿dónde estaba el frame A respecto a B en el instante t?".

**Detalle:**
- Convenciones **REP-103** (ejes: x adelante, y izquierda, z arriba; unidades SI) y **REP-105** (cadena `map → odom → base_link`; `odom→base_link` es continua pero deriva, `map→odom` da el salto de la corrección global).
- `tf2_ros::TransformBroadcaster` (dinámicas) y `StaticTransformBroadcaster` (extrínsecos de la cámara, que no cambian: se publican una vez con QoS transient_local).
- Un frame **solo puede tener un padre**; el árbol no puede tener ciclos ni dos publishers de la misma transformada (síntoma: todo tiembla).
- `lookupTransform` con timeout y capturando `tf2::ExtrapolationException` — pasa constantemente cuando pides una transformada demasiado nueva.
- **Trampa de drones:** ROS usa **ENU** y los autopilotos (PX4/ArduPilot, aviación) usan **NED**. La conversión de frames y de convención de cuaterniones es fuente inagotable de bugs de signo.

### P: ¿Cómo publicas imágenes eficientemente?

**Corto:** Evitando copias y serialización: composición en un proceso + intra-process comms + publicar por `unique_ptr`, y `cv_bridge::toCvShare` en lectura.

```cpp
// Nodo componible con intra-process activado
rclcpp::NodeOptions opts;
opts.use_intra_process_comms(true);

// Publicar por unique_ptr => con intra-process se pasa el puntero, sin copia ni serialización
auto msg = std::make_unique<sensor_msgs::msg::Image>();
// ... rellenar ...
pub_->publish(std::move(msg));

// En el subscriber: toCvShare NO copia (te da un Mat const que apunta al mensaje)
void cb(const sensor_msgs::msg::Image::ConstSharedPtr& m) {
    cv_bridge::CvImageConstPtr cv = cv_bridge::toCvShare(m, "bgr8");
    const cv::Mat& img = cv->image;      // sin copia
    // toCvCopy() sí copia: úsalo solo si necesitas escribir
}
```

**Otras palancas:**
- **`image_transport`**: publica automáticamente variantes `compressed`/`theora`; ideal para el downlink, innecesario dentro del mismo host.
- **Loaned messages / zero-copy DDS**: con shared memory (Iceoryx en Cyclone, SHM transport en Fast DDS) puedes cruzar procesos sin copia si el mensaje es de tamaño fijo.
- **NITROS (Isaac ROS)**: negocia el tipo entre nodos vecinos para que los datos se queden en memoria GPU (NVMM) y nunca bajen a CPU. Es *la* respuesta correcta a "¿cómo evitas que ROS2 te mate el rendimiento en un Jetson?".

### P: Tienes que sincronizar cámara + IMU + GPS en un nodo. ¿Cómo?

**Corto:** `message_filters` con `ApproximateTime` (o `ExactTime` si comparten trigger), usando siempre `header.stamp`.

```cpp
message_filters::Subscriber<Image> img_sub(this, "/cam/image");
message_filters::Subscriber<Imu>   imu_sub(this, "/imu/data");
using Policy = message_filters::sync_policies::ApproximateTime<Image, Imu>;
message_filters::Synchronizer<Policy> sync(Policy(10), img_sub, imu_sub);
sync.registerCallback(&MyNode::onSynced, this);
```

**Matices:** el sincronizador introduce latencia (espera a la pareja) y descarta mensajes sin match; en un dron a veces es mejor un buffer circular propio de IMU e interpolar a la marca de tiempo de la imagen, que es lo que hace cualquier VIO serio.

### P: Herramientas de depuración que usas.

```bash
ros2 topic list / echo / hz / bw / info -v     # -v muestra QoS de cada extremo
ros2 node info /mi_nodo
ros2 param list|get|set /mi_nodo param
ros2 interface show sensor_msgs/msg/Image
ros2 bag record -a -s mcap  /  ros2 bag play  # replay determinista: oro puro
ros2 doctor                                   # problemas de red/entorno
rqt_graph, rviz2, PlotJuggler
colcon build --symlink-install --packages-select mi_pkg
```

**Lo que quieren oír:** "grabo bags en vuelo y reproduzco en tierra; el 90 % de la depuración de un dron es offline sobre logs, porque no puedes iterar en el aire."

---

## 2.2 ROS2 en el dron (integración real)

### P: ¿Cómo se conecta ROS2 con el flight controller?

**Corto:** El Jetson es el *companion computer*; habla con el autopiloto (PX4/ArduPilot) por UART o Ethernet.

- **MAVLink + MAVROS**: el clásico, funciona con ArduPilot y PX4, traduce MAVLink ↔ topics ROS.
- **uXRCE-DDS** (PX4 ≥ v1.14, sustituye al antiguo microRTPS): el autopiloto expone directamente sus topics uORB como topics DDS/ROS2. Menos latencia y sin capa de traducción.
- **micro-ROS**: ROS2 dentro de microcontroladores, para nodos en el propio hardware.

**Lo que se controla desde el companion:** modo *offboard* con setpoints de posición/velocidad/actitud, y el autopiloto sigue siendo responsable de la estabilización y de la seguridad (failsafes). **Nunca** pongas el lazo de estabilización en el Jetson: un Linux no determinista no vuela un dron.

### P: ¿ROS2 es apto para tiempo real?

**Corto:** ROS2 está *diseñado* para permitirlo, pero un stack ROS2 sobre Linux estándar **no es hard real-time**. En un dron el hard real-time vive en el autopiloto (NuttX/ChibiOS); en el Jetson corre el soft real-time: percepción y planificación.

**Si te presionan:** kernel `PREEMPT_RT`, hilos con `SCHED_FIFO` y prioridad, `mlockall` para evitar page faults, allocators sin `malloc` en el hot path, callbacks acotados en tiempo, y CPU pinning (aislar cores para el hilo crítico con `isolcpus`). Aun así, mides el jitter y lo documentas; no lo prometes.

### P: Arquitectura ROS2 típica de percepción en un dron.

```
[camera_node]--image(BEST_EFFORT, KeepLast1)-->[detector_node (TensorRT)]
       |                                              |
   camera_info                                  detections (vision_msgs)
       |                                              v
   [tf2 static: base_link->camera]           [tracker_node]-->tracks
                                                      v
                          [geolocation_node]  (rayo + actitud + DTM -> lat/lon)
                                                      v
                                      [mission/gimbal_node] --> MAVLink/uXRCE
```
Todos los nodos de percepción **en un solo proceso** (`rclcpp_components` + container) con intra-process activado, para que las imágenes nunca se serialicen.

### P: Errores/gotchas de ROS2 que hayas sufrido.

Ten 3-4 listos, suena a experiencia real:
1. **QoS incompatible** → el topic "existe" pero no llega nada, sin ningún error.
2. **Multicast en WiFi**: el discovery de DDS por multicast va fatal en enlaces inalámbricos; se arregla con lista de peers unicast o `ROS_LOCALHOST_ONLY` + un puente.
3. **Buffers UDP del kernel pequeños** → mensajes grandes (imágenes, PointCloud2) se fragmentan y se pierden; hay que subir `net.core.rmem_max`.
4. **Deadlock** llamando a un service de forma síncrona dentro de un callback con executor single-threaded.
5. **`use_sim_time`** mal puesto: los timestamps no cuadran y TF extrapola mal.
6. **ROS_DOMAIN_ID** compartido en el laboratorio: dos drones se ven entre sí y se mezclan los topics.

---

# PARTE 3 — Preguntas cortas de disparo rápido

| Pregunta | Respuesta de una línea |
|---|---|
| ¿Por qué TensorRT y no OpenCV DNN en Jetson? | TensorRT usa tensor cores, fusiona capas y hace autotuning para esa GPU concreta; OpenCV DNN no se acerca. |
| ¿Se puede copiar un engine TensorRT entre máquinas? | No: está atado a arquitectura GPU y versión de TensorRT. Se compila en el target. |
| ¿Qué es `nvpmodel`? | Selector de perfil de potencia (cores y frecuencias máximas). |
| ¿Qué hace `jetson_clocks`? | Fija los relojes al máximo del modo actual y desactiva DVFS. |
| ¿Diferencia entre latencia y throughput? | Throughput = frames/s; latencia = retardo de un frame concreto. Con batching sube el primero y empeora la segunda. |
| ¿Batch size en un dron con una cámara? | 1. Batching solo tiene sentido con varias cámaras. |
| ¿INT8 sin calibración? | No: sin rangos dinámicos la precisión se hunde. PTQ con datos del dominio o QAT. |
| ¿Dónde va el NMS? | En GPU (plugin de TensorRT / `EfficientNMS`), no en un bucle de CPU. |
| ¿Qué mides con `tegrastats`? | Uso de CPU/GPU/EMC, RAM, temperaturas y throttling. |
| ¿Por qué el Orin Nano puede no valer? | No tiene NVENC ni DLA. |
| ¿QoS por defecto de un sensor? | `SensorDataQoS`: best effort, keep_last(5). |
| ¿Cómo evitas copias de imagen en ROS2? | Composición + intra-process + publicar `unique_ptr` + `toCvShare`; o NITROS. |
| ¿Cuándo action y no service? | Cuando la tarea es larga, quieres feedback y poder cancelar. |
| ¿Un frame TF con dos padres? | Imposible: el árbol es un árbol; dos publishers de la misma TF es un bug. |
| ¿ENU o NED? | ROS: ENU. Autopilotos/aviación: NED. Convertir explícitamente. |
| ¿Qué es el ego-motion y por qué molesta? | La cámara se mueve; rompe la asociación de tracks por posición. Se compensa con homografía o con IMU/actitud del gimbal. |
| ¿Cómo pruebas sin volar? | Bags grabados + replay, simulación (Gazebo/Isaac Sim, PX4 SITL), y HIL. |

---

# PARTE 4 — Preguntas que hacer tú

Terminar preguntando bien vale tanto como responder bien:

- ¿Qué módulo Jetson usáis y cuál es el presupuesto real de potencia y térmico en la plataforma?
- ¿El pipeline de percepción está en ROS2 o es un runtime propio? ¿Usáis Isaac ROS/NITROS o DeepStream?
- ¿Cómo validáis un modelo antes de que vuele? ¿Tenéis replay sobre datos reales, HIL, simulación?
- ¿Cómo gestionáis las actualizaciones OTA y el versionado de modelos en la flota?
- ¿Dónde está hoy el cuello de botella: latencia, precisión de los modelos, o el proceso de llevar a producción?
- ¿Cómo se reparte el trabajo entre el equipo de investigación y el de despliegue embebido?
