# Curso de refuerzo — NVIDIA Jetson, CUDA, TensorRT y ROS 2

Basado en tu test 04 (40%) y las preguntas 4 y 5 del test mixto 06 (ROS 2 y TensorRT). El test 10, dedicado enteramente a este tema, lo hiciste perfecto (100%): quantización FP16 vs. INT8, nvpmodel/jetson_clocks, compilación y serialización de engines TensorRT, diferencias entre módulos Jetson (Nano/NX/AGX/Orin) y configuración de cámaras CSI. Esos ya los dominas, no los repito en detalle aquí.

Este curso cubre lo que falló: memoria unificada y zero-copy, gestión térmica más allá de lo básico, calibración INT8 en profundidad, profiling de latencia de cola con Nsight, y un tema aparte pero relacionado con tu stack (ROS 2): deadlocks por llamadas síncronas dentro de callbacks.

## Índice

1. Memoria unificada Tegra y zero-copy
2. NVMM y pipelines DeepStream (repaso breve — lo tienes bien)
3. Gestión térmica: nvpmodel, jetson_clocks, tegrastats
4. Calibración INT8 en TensorRT, en profundidad
5. Profiling de latencia P99 con Nsight Systems
6. Deadlocks en ROS 2: executors y callback groups

---

## 1. Memoria unificada Tegra y zero-copy

### ¿Qué es y por qué es distinto a una GPU discreta?

En una GPU discreta (una RTX de escritorio, por ejemplo), la CPU tiene su RAM y la GPU tiene su propia VRAM, físicamente separadas, conectadas por PCIe. Copiar datos entre ambas requiere `cudaMemcpy`, con su coste de ancho de banda y latencia.

Los módulos Jetson son SoCs Tegra: CPU y GPU **comparten la misma memoria física** (no hay VRAM separada). Esto es una propiedad del **hardware**, no depende de qué versión de TensorRT o CUDA tengas instalada — es una confusión típica pensar que la memoria unificada "aparece" a partir de cierta versión de software; existe porque el chip está diseñado así.

### Qué habilita esto: zero-copy

Como no hay dos bancos de memoria físicamente separados, puedes usar memoria **"zero-copy"**: `cudaHostAlloc` con la flag `cudaHostAllocMapped` asigna memoria que tanto la CPU como la GPU pueden acceder **directamente a través del mismo puntero**, sin necesidad de ningún `cudaMemcpy` explícito entre "dos sitios". Es exactamente el patrón habitual en DeepStream/VPI para pipelines de captura de cámara: el frame capturado por la CSI queda accesible para la GPU sin copiarlo primero.

De forma relacionada, `cudaMallocManaged` en Jetson **no** migra páginas entre dos bancos separados (como sí hace en una GPU discreta): al no existir esa separación física, no hay nada que migrar en el sentido tradicional.

### El matiz que fallaste: zero-copy no siempre es más rápido

Es tentador pensar "zero-copy siempre gana, evita copias". Falso como regla absoluta: la memoria mapeada zero-copy suele ser **no cacheable** o con menor eficiencia de acceso repetido desde la GPU. Si un dato se va a **leer muchas veces** por la GPU (por ejemplo, pesos de un modelo reutilizados en cada inferencia), puede ser más rápido copiarlo **una vez** a memoria device-local (cacheable) que acceder repetidamente vía zero-copy. Zero-copy brilla quieres evitar el coste de una copia para datos que se usan **una vez** (como un frame de cámara que entra, se procesa y se descarta), no para datos reutilizados intensivamente.

### Memoria pinned para pipelines de captura

`cudaHostAlloc` (sin necesariamente mapear) asigna memoria *page-locked* (pinned), que permite a CPU y GPU acceder al mismo puntero sin necesidad de sincronización explícita de copia — el patrón habitual para evitar el coste de `cudaMemcpy` en cada frame capturado por CSI, reduciendo la latencia end-to-end del pipeline captura→inferencia.

### Ejercicio 1

Tienes dos escenarios en una Jetson: (a) un pipeline de cámara que captura un frame, lo pasa una vez por un preprocesado ligero en GPU y lo descarta; (b) un modelo de detección cuyos pesos (varios MB) se consultan en cada una de las miles de inferencias por segundo. ¿En cuál de los dos usarías memoria zero-copy y en cuál copiarías una vez a memoria device-local? Justifica con el criterio de "frecuencia de acceso" del módulo.

---

## 2. NVMM y pipelines DeepStream (repaso breve)

Esto lo acertaste — un recordatorio corto para que quede fijado.

En un pipeline GStreamer/DeepStream típico (`nvarguscamerasrc → nvvideoconvert → nvstreammux → nvinfer → nvtracker → salida`), todos los elementos operan sobre buffers en memoria **NVMM** en vez de convertir a buffers de sistema (RAM del host) entre etapas. La razón de la ganancia de rendimiento es exactamente la memoria unificada del módulo anterior: NVMM permite que el ISP (procesador de imagen), la GPU y los aceleradores de vídeo compartan los mismos buffers **sin `memcpy` explícitos** entre CPU y GPU, reduciendo drásticamente latencia y carga de CPU.

Dos matices para no confundir: NVMM **no** aumenta la resolución máxima soportada por el sensor CSI (eso lo determina el hardware del bus MIPI CSI-2, ajeno al tipo de memoria usado después de la captura), y `nvinfer` **no** exige NVMM por una limitación de formato de píxel — NV12 es válido tanto en NVMM como en memoria de sistema; el motivo real de usar NVMM es evitar copias, no un requisito de formato.

---

## 3. Gestión térmica: nvpmodel, jetson_clocks, tegrastats

### Los tres controles, y qué controla cada uno

- **`nvpmodel -m N`**: selecciona un **modo de potencia** predefinido (o personalizado), que limita el consumo máximo permitido del SoC combinando qué núcleos de CPU están activos y los techos de frecuencia de CPU/GPU.
- **`jetson_clocks`**: **fija** las frecuencias de CPU/GPU/EMC en su máximo permitido por el modo `nvpmodel` actual, eliminando la variabilidad del gobernador DVFS (que normalmente escala frecuencias dinámicamente según carga).
- **`tegrastats`**: herramienta de **monitorización** en tiempo real: expone temperaturas por zona térmica del SoC y las frecuencias *reales* aplicadas en cada momento.

### El error conceptual central: fijar frecuencias no impide el throttling térmico

`jetson_clocks` bloquea las frecuencias en su máximo configurado, pero **no impide** que el hardware las reduzca automáticamente si se supera el umbral térmico crítico del chip — el throttling térmico es una respuesta de protección del silicio ante temperatura excesiva, y ocurre **por encima** de cualquier configuración de software que hayas fijado. `jetson_clocks` "por sí solo" no garantiza nunca throttling cero.

Igualmente, la configuración de `jetson_clocks` **no es persistente** entre reinicios por defecto: se pierde salvo que la guardes explícitamente (`jetson_clocks --store`) y actives el servicio systemd correspondiente para reaplicarla en cada arranque.

### Qué sí ayuda a evitar throttling en un sistema con disipación limitada (ej. un dron)

1. **Disipación física adecuada**: un disipador/ventilador dimensionado para el consumo máximo del modo `nvpmodel` elegido reduce la probabilidad de throttling **sin necesidad de bajar frecuencias** — el throttling responde a temperatura, no solo a la frecuencia configurada; mejor disipación permite sostener frecuencias altas más tiempo antes de alcanzar el umbral.
2. **Elegir un modo `nvpmodel` acorde a la disipación disponible**, en vez de forzar siempre el modo de máximo rendimiento (MAXN). Un modo más conservador limita consumo y calor generado, evitando que el sistema entre en throttling tras unos segundos de carga alta — preferible a un pico de rendimiento breve seguido de degradación brusca y sostenida.
3. **Monitorización activa con `tegrastats`**: correlacionar caídas de FPS/rendimiento con eventos térmicos reales (temperatura y reducción de frecuencia observadas) te permite ajustar el modo de energía o mejorar la disipación con datos, no adivinando.

### Ejercicio 2

Un dron con Jetson Orin NX en modo MAXN sostiene 30 FPS de inferencia durante los primeros 45 segundos de vuelo, y luego cae progresivamente a 12 FPS y se mantiene ahí. `tegrastats` durante ese tramo muestra la temperatura del SoC subiendo hasta un valor cercano al límite y las frecuencias reales de GPU bajando bruscamente en el mismo momento en que cae el FPS. Diagnostica la causa más probable y propón dos cambios concretos (uno de configuración, uno físico) para sostener un rendimiento más estable, aunque sea algo menor que el pico inicial de 30 FPS.

---

## 4. Calibración INT8 en TensorRT, en profundidad

### Por qué INT8 necesita calibración y FP16 no

FP16 conserva un rango dinámico razonablemente cercano a FP32 (mismo número de bits de exponente, menos de mantisa), así que convertir de FP32 a FP16 no suele requerir ningún paso adicional de ajuste — TensorRT simplemente usa el flag de precisión FP16 al construir el engine.

INT8 es radicalmente distinto: solo tiene 256 valores representables por tensor (o por canal, según el esquema). Para mapear el rango real de valores que toma cada activación/peso de la red a ese rango discreto tan pequeño sin destruir la precisión del modelo, TensorRT necesita conocer los **rangos dinámicos reales** de cada tensor — y eso requiere **datos reales**, no se puede inferir sin más de la arquitectura del modelo.

### Cómo funciona la calibración (no es fine-tuning)

TensorRT usa un `IInt8Calibrator` (por ejemplo `IInt8EntropyCalibrator2`) que recorre un **conjunto de datos representativo** de calibración, ejecutando inferencia normal (forward pass) sobre esos datos y recopilando **estadísticas de activación** (histogramas) por capa. A partir de esos histogramas calcula los factores de escala que minimizan la pérdida de información al cuantizar.

El error conceptual que cometiste: la calibración **no** hace backpropagation ni reentrena/reajusta los pesos del modelo. Es un proceso de **post-entrenamiento**, puramente de recolección de estadísticas — los pesos originales del modelo no cambian en este paso (a diferencia de *quantization-aware training*, QAT, que sí modifica los pesos durante un reentrenamiento consciente de la cuantización).

### Portabilidad: nada de esto es transferible sin más

Dos cosas distintas que no son portables entre plataformas/versiones:

- El **calibration cache** (la tabla de escalas generada) está ligado a la versión de TensorRT y, en muchos casos, a la arquitectura/compute capability de la GPU sobre la que se generó — no se garantiza que un cache generado en una RTX 3090 de escritorio sea directamente reutilizable en una Jetson Orin sin regenerarlo.
- El **engine serializado** completo está optimizado para la arquitectura de GPU concreta (y versión de TensorRT/CUDA/cuDNN) sobre la que se construyó. Un engine construido en una Jetson Xavier (Volta) normalmente **no** es portable sin recompilar a una Jetson Orin (Ampere), aunque uses la misma versión de TensorRT — arquitecturas de GPU distintas requieren, en general, reconstruir el engine.

### INT8 no garantiza mejor accuracy que FP16

Es al revés de lo que podrías asumir por "menos bits = más eficiente = mejor": INT8 tiene menor resolución numérica que FP16, así que normalmente introduce **más** pérdida de accuracy, a cambio de ganar en throughput/latencia y menor uso de memoria. Siempre hay que validar la accuracy tras cuantizar, no darla por garantizada ni en un sentido ni en el otro.

### Ejercicio 3

Estás desplegando un detector de objetos en INT8 en una Jetson y notas una caída de accuracy notable respecto a la versión FP32 original. Lista, en orden de qué comprobarías primero, tres posibles causas relacionadas específicamente con el proceso de calibración (no con el modelo en sí), y para cada una indica qué cambiarías en el proceso de calibración para mitigarla.

---

## 5. Profiling de latencia P99 con Nsight Systems

### Por qué P99 y no la media

La latencia **media** puede ser excelente mientras la latencia de **cola** (percentil 99, el 1% de peores casos) es mala por picos esporádicos causados por contención de recursos, sincronización, o variabilidad de frecuencia. En sistemas en tiempo real (robótica, drones, conducción autónoma), lo que suele importar de verdad es que **ningún** frame tarde demasiado, no que el promedio sea bajo — por eso se perfila específicamente P99, no la media.

### Qué te da Nsight Systems

Una vista de **timeline unificada**: streams CUDA, llamadas a la API, actividad de CPU, todo simultáneamente y correlacionado en el tiempo. Esto permite identificar directamente si los picos de latencia P99 se deben a **serialización entre kernels** (kernels que deberían poder solaparse pero se ejecutan uno tras otro) o a **esperas de sincronización** (por ejemplo, un `cudaStreamSynchronize` bloqueante esperando innecesariamente).

Nsight Systems (junto con Nsight Compute y `tegrastats`) también puede mostrar métricas de **utilización de ancho de banda de memoria**, así que un cuello de botella causado por contención del bus LPDDR compartido entre CPU y GPU **sí es detectable** con estas herramientas — no hace falta recurrir a herramientas de terceros para eso.

### El paso previo indispensable: fijar el estado de energía antes de perfilar

Si no fijas las frecuencias con `nvpmodel -m 0` (máximo rendimiento) y `jetson_clocks` antes de perfilar, el gobernador DVFS puede escalar dinámicamente CPU/GPU/memoria durante la captura de la traza, generando **outliers de latencia que no reflejan el rendimiento sostenido real** del pipeline — confundirías variabilidad introducida por el propio escalado de energía con cuellos de botella genuinos del pipeline.

### Leer la señal más común: GPU idle mientras CPU trabaja

Si la traza muestra la GPU **inactiva** durante gran parte del pipeline mientras la CPU ejecuta preprocesamiento (por ejemplo, con OpenCV en CPU), esa es la señal clásica de un **cuello de botella de preprocesamiento en CPU**: la GPU está esperando datos que la CPU aún no ha terminado de preparar. La solución típica es trasladar ese preprocesamiento a GPU (VPI o CUDA) para solapar mejor el trabajo entre ambos procesadores en vez de serializarlo.

### Ejercicio 4

Capturas una traza con Nsight Systems de tu pipeline DeepStream en una Jetson AGX **sin** haber fijado `nvpmodel`/`jetson_clocks` de antemano, y observas picos de latencia P99 irregulares que no correlacionan con ningún patrón obvio del pipeline (ni con huecos de GPU idle, ni con serialización de kernels visible). ¿Cuál es el primer paso que deberías repetir antes de sacar ninguna conclusión sobre el pipeline en sí, y por qué?

---

## 6. Deadlocks en ROS 2: executors y callback groups

Esto es un antipatrón muy común en robótica con ROS 2, y probablemente relevante para tu trabajo si integras visión/percepción en un stack ROS 2.

### El código problemático

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

Ejecutado con `rclpy.spin(node)` estándar (que usa un `SingleThreadedExecutor`), este código se queda **colgado indefinidamente** en la primera llamada al servicio.

### Por qué ocurre exactamente

`Client.call()` **sí existe** en rclpy como variante bloqueante de `call_async()` — no lanza ningún error de atributo, y precisamente por ser tan fácil de usar es una trampa habitual. El problema es que un `SingleThreadedExecutor` solo puede ejecutar **un callback a la vez**. Mientras `cb()` está bloqueado esperando la respuesta del servicio (dentro de `client.call()`), el executor **no puede procesar ningún otro evento** — incluida la respuesta entrante del propio servicio que `cb()` está esperando. El programa espera indefinidamente algo que nunca podrá procesar, porque el único hilo disponible para procesarlo está ocupado esperándolo: deadlock clásico.

### Por qué los callback groups por sí solos NO lo resuelven aquí

Es tentador pensar "pongo el suscriptor y el cliente en distintos `MutuallyExclusiveCallbackGroup` y ya está". **No basta**: los callback groups solo determinan qué callbacks *pueden* ejecutarse en paralelo cuando el executor **tiene varios hilos**. Con un `SingleThreadedExecutor`, sigue habiendo un único hilo ejecutando un callback a la vez sin importar en qué grupo estén — el deadlock persiste igual.

Tampoco es una restricción de diseño de la API: los servicios en ROS 2 sí se pueden llamar desde dentro de un callback de suscripción. El problema no es "que no se pueda", es la falta de concurrencia del executor para procesar la respuesta mientras el callback origen sigue bloqueado.

### La solución real

Dos caminos válidos:

1. Usar un **`MultiThreadedExecutor`** con callback groups apropiados (ahora sí, con varios hilos disponibles, los callback groups sí determinan correctamente qué puede correr en paralelo — poniendo el callback de suscripción y el procesamiento de la respuesta del servicio en grupos que permitan ejecutarse simultáneamente).
2. Reestructurar para usar **`call_async()`** en vez de `call()`, devolviendo control al executor inmediatamente y procesando el resultado mediante un callback sobre el futuro devuelto (o `await` si usas el patrón asíncrono de rclpy), sin bloquear nunca el hilo del executor.

También conviene descartar de entrada una hipótesis tentadora pero incorrecta: una incompatibilidad de QoS entre cliente y servidor normalmente provocaría que el servidor **nunca aparezca disponible** (fallo visible antes de la primera llamada), no un colgado silencioso tras iniciarse la llamada — así que si el síntoma es exactamente "se cuelga en la primera llamada", QoS no es la explicación más probable.

### Ejercicio 5

Reescribe el método `cb()` del ejemplo usando `call_async()` en vez de `call()`, de forma que no bloquee el executor. Describe en una frase cómo y cuándo se procesaría la respuesta del servicio en este nuevo diseño.

---

## Soluciones

### Solución 1

(a) El frame de cámara procesado una vez y descartado es el caso ideal para **zero-copy**: se accede una única vez (o pocas veces) por la GPU, así que el coste de que la memoria mapeada sea no cacheable apenas importa, y te ahorras por completo el `cudaMemcpy` de cada frame — justo el patrón de captura CSI descrito en el módulo. (b) Los pesos del modelo, consultados miles de veces por segundo en cada inferencia, son el caso ideal para **copiar una vez a memoria device-local** (por ejemplo, cargarlos normalmente al construir el engine de TensorRT): al reutilizarse tan intensivamente, el acceso repetido cacheable en memoria device-local compensa de sobra el coste único de la copia inicial, evitando el overhead de accesos repetidos a memoria zero-copy no cacheable.

### Solución 2

*(Este módulo era repaso — no tiene ejercicio con solución separada; el contenido ya lo dominabas en el test 04, pregunta 2.)*

### Solución 3

Diagnóstico más probable: **throttling térmico**. El SoC alcanza temperatura crítica tras ~45 segundos de carga sostenida en modo MAXN, y el hardware reduce las frecuencias de GPU automáticamente para protegerse — el FPS cae en el mismo instante en que bajan las frecuencias reales observadas en `tegrastats`, confirmando la causa (no es, por ejemplo, un problema de software en el pipeline). Cambio de configuración: pasar a un modo `nvpmodel` más conservador que MAXN (limitando el consumo/calor máximo generado) para intentar sostener un rendimiento estable por debajo del pico, en vez de forzar el máximo y sufrir la caída posterior. Cambio físico: mejorar la disipación (disipador más grande, ventilador adicional, o mejorar el flujo de aire dentro del chasis del dron) dimensionada para el consumo del modo elegido, permitiendo sostener frecuencias más altas durante más tiempo antes de alcanzar el umbral térmico.

### Solución 4

El primer paso a repetir es fijar el estado de energía: ejecutar `nvpmodel -m 0` (o el modo de máximo rendimiento correspondiente) y `sudo jetson_clocks`, y **volver a capturar la traza** desde cero. Sin frecuencias fijas, el gobernador DVFS puede estar escalando dinámicamente CPU/GPU/memoria durante la captura, introduciendo variabilidad de latencia que no tiene nada que ver con el pipeline en sí — es exactamente el escenario descrito en el módulo: picos "irregulares sin patrón obvio" son la firma típica de ruido introducido por el escalado dinámico de energía, no de un cuello de botella real del pipeline. Sacar conclusiones sobre el pipeline antes de controlar esta variable llevaría a perseguir un problema que en realidad es de configuración del sistema, no del código.

### Solución 5

```python
class MyNode(Node):
    def __init__(self):
        super().__init__('my_node')
        self.client = self.create_client(Trigger, 'do_thing')
        self.sub = self.create_subscription(String, 'in', self.cb, 10)

    def cb(self, msg):
        req = Trigger.Request()
        future = self.client.call_async(req)
        future.add_done_callback(self.on_respuesta)

    def on_respuesta(self, future):
        resp = future.result()
        self.get_logger().info(f"respuesta: {resp}")
```

`cb()` ya no bloquea: dispara la llamada asíncrona y retorna inmediatamente, devolviendo el control al executor. La respuesta del servicio se procesa más tarde, de forma asíncrona, cuando el executor invoque `on_respuesta` como callback del `future` en cuanto la respuesta llegue — sin que ningún hilo se quede bloqueado esperándola, así que ni siquiera hace falta un `MultiThreadedExecutor` para este patrón concreto.
