# Resultado del test — NVIDIA Jetson / CUDA / TensorRT

- Fecha: 2026-08-04 15:36
- Nivel: media
- Puntuación: **40%** (2.00/5 puntos)
- Preguntas perfectas: 1/5

## Revisión pregunta a pregunta

### ❌ Pregunta 1 — Memoria unificada Tegra y CUDA zero-copy para pipelinado de datos

En un pipeline de inferencia embebida sobre un módulo Jetson (arquitectura Tegra con memoria unificada CPU-GPU), estás optimizando la transferencia de frames capturados por una cámara CSI hacia el motor de inferencia. ¿Cuáles de las siguientes afirmaciones sobre memoria unificada y zero-copy en Jetson son correctas?

- [ ] **En arquitecturas Tegra, la memoria unificada solo está disponible a partir de TensorRT 8, no es una característica del hardware.** — _incorrecta_: Incorrecto: la memoria unificada es una propiedad del SoC (arquitectura física compartida CPU-GPU), no depende de la versión de TensorRT instalada.
- [x] **En Jetson, CPU y GPU comparten la misma memoria física (SoC unificado), por lo que se puede usar memoria "zero-copy" (cudaHostAlloc con cudaHostAllocMapped) para evitar copias explícitas entre host y device.** — _correcta_: Correcto: al no existir memoria de GPU discreta separada, un puntero mapeado puede ser accedido por ambos procesadores sin cudaMemcpy, ahorrando tiempo y ancho de banda en el pipeline.
- [ ] **cudaMallocManaged en Jetson sigue realizando una copia física de datos entre dos bancos de memoria separados, igual que en GPUs discretas.** — _incorrecta_: Incorrecto: en GPUs discretas la memoria managed migra páginas entre VRAM y RAM del host, pero en Tegra, al ser memoria física unificada, no hay dos bancos separados que copiar.
- [x] **El uso de zero-copy siempre mejora el rendimiento frente a cudaMemcpy explícito, independientemente del patrón de acceso.** — _incorrecta_: Incorrecto: la memoria mapeada zero-copy suele ser no cacheable o con menor eficiencia de acceso repetido; para datos leídos muchas veces por la GPU puede ser más lento que copiar una vez a memoria device-local.
- [ ] **Usar memoria pinned (page-locked) con cudaHostAlloc permite que tanto la CPU como la GPU accedan al mismo puntero sin necesidad de sincronización explícita de copia, útil en pipelines de captura de cámara.** — _correcta_: Correcto: es precisamente el patrón habitual en DeepStream/VPI para evitar el coste de cudaMemcpy en cada frame capturado por CSI, reduciendo la latencia end-to-end del pipeline.

> Los Jetson usan una arquitectura SoC con memoria física compartida entre CPU y GPU, lo que habilita técnicas zero-copy (cudaHostAlloc/cudaHostAllocMapped) para eliminar copias redundantes en pipelines de captura-inferencia, aunque no siempre es la opción más rápida según el patrón de acceso.
>
> Repasar: `CUDA Unified Memory en Tegra / zero-copy (cudaHostAllocMapped)`

### ✅ Pregunta 2 — Sensor CSI y pipeline DeepStream: NVMM sin copia desde captura hasta inferencia

En un pipeline GStreamer/DeepStream típico en Jetson (`nvarguscamerasrc` → `nvvideoconvert` → `nvstreammux` → `nvinfer` → `nvtracker` → salida), todos los elementos operan sobre buffers en memoria NVMM en lugar de convertir a buffers de sistema (RAM del host) entre etapas. ¿Cuál es la razón principal de esta ventaja de rendimiento?

- [x] **Se evitan copias de memoria entre el motor de captura, la GPU y el motor de inferencia, ya que NVMM es memoria compartida/accesible directamente por todos los bloques de hardware, reduciendo latencia y carga de CPU.** — _correcta_: NVMM aprovecha la memoria unificada de Jetson para que ISP, GPU y aceleradores de vídeo compartan los mismos buffers sin memcpy explícitos entre CPU y GPU, lo que reduce drásticamente latencia y consumo de CPU en el pipeline.
- [ ] **Aumenta la resolución máxima soportada por el sensor CSI, ya que NVMM permite superar el límite de ancho de banda del bus MIPI CSI-2.** — _incorrecta_: El ancho de banda del bus MIPI CSI-2 lo determina el hardware del sensor y del receptor CSI, no el tipo de memoria usado después de la captura; NVMM no altera ese límite físico.
- [ ] **Permite que jetson_clocks aplique overclock automático a la GPU cuando detecta buffers NVMM en el pipeline.** — _incorrecta_: jetson_clocks no inspecciona el tipo de buffers del pipeline ni aplica overclock condicional; simplemente fija las frecuencias configuradas de forma estática, sin relación con NVMM.
- [ ] **Es obligatorio porque nvinfer no puede leer buffers en formato NV12, solo acepta memoria NVMM sin excepción, independientemente del backend de inferencia.** — _incorrecta_: Confunde formato de píxel con tipo de memoria: NV12 es un formato de color válido tanto en NVMM como en memoria de sistema; el motivo real de usar NVMM es evitar copias, no una limitación de formato de nvinfer.

> Mantener el flujo de vídeo en memoria NVMM de principio a fin (captura CSI, conversión de color/escala, inferencia y tracking) es la técnica clave de optimización 'zero-copy' en DeepStream: evita transferencias PCIe/memcpy redundantes entre CPU y GPU propias de arquitecturas con memoria separada, aprovechando la memoria unificada de Jetson.
>
> Repasar: `DeepStream, NVMM, nvarguscamerasrc, memoria unificada, zero-copy`

### ⚠️ Pregunta 3 — Modos nvpmodel y jetson_clocks: prevención de thermal throttling en drones

Estás integrando una Jetson Orin NX en un dron para inferencia en tiempo real (detección de obstáculos). El chasis tiene disipación limitada por peso y espacio. ¿Qué prácticas ayudan realmente a evitar el thermal throttling manteniendo un rendimiento sostenido y predecible? (selecciona todas las correctas)

- [ ] **jetson_clocks debe ejecutarse una sola vez al fabricar la imagen y sus efectos persisten automáticamente tras cada reinicio, sin necesidad de un servicio.** — _incorrecta_: La configuración de jetson_clocks no es persistente por defecto; se pierde en cada reinicio salvo que se guarde con `jetson_clocks --store` y se active mediante el servicio systemd correspondiente.
- [ ] **Ejecutar `sudo jetson_clocks` fija las frecuencias en su máximo y, por sí solo, garantiza que nunca se active el throttling térmico.** — _incorrecta_: jetson_clocks bloquea las frecuencias de CPU/GPU/EMC para eliminar la variabilidad del gobernador DVFS, pero no impide que el hardware reduzca clocks si se supera el umbral térmico crítico; el throttling térmico puede seguir activándose por encima de esa configuración.
- [ ] **Añadir un disipador/ventilador dimensionado para el consumo máximo del modo nvpmodel seleccionado reduce la probabilidad de throttling sin necesidad de bajar frecuencias.** — _correcta_: El throttling es una respuesta a la temperatura, no solo a la frecuencia configurada; mejorar la disipación física permite sostener frecuencias altas más tiempo antes de alcanzar el umbral térmico.
- [x] **Elegir un modo nvpmodel acorde a la disipación disponible en el chasis del dron (en vez de forzar siempre MAXN) ayuda a mantener un rendimiento sostenido sin picos térmicos.** — _correcta_: Un modo de potencia más conservador limita el consumo y el calor generado, evitando que el sistema entre en régimen de throttling tras unos segundos de carga alta, lo cual es preferible a un pico de rendimiento breve seguido de degradación.
- [x] **Monitorizar con `tegrastats` los campos de temperatura y el estado de reducción de frecuencia permite detectar el throttling térmico antes de que degrade la inferencia.** — _correcta_: tegrastats expone temperaturas por zona térmica y las frecuencias reales aplicadas, lo que permite correlacionar caídas de FPS con eventos térmicos y ajustar el modo de energía o la disipación en consecuencia.

> En sistemas embebidos con restricciones térmicas como drones, jetson_clocks y nvpmodel controlan las frecuencias objetivo, pero el throttling térmico real depende de la temperatura medida por los sensores del SoC. Prevenirlo requiere combinar un modo de energía adecuado, disipación suficiente y monitorización activa con tegrastats, no solo forzar el máximo rendimiento.
>
> Repasar: `nvpmodel, jetson_clocks, tegrastats, throttling térmico`

### ❌ Pregunta 4 — Compilación de engines TensorRT con INT8 y calibración de datasets

Estás compilando un engine TensorRT en precisión INT8 a partir de un modelo ONNX para desplegarlo en un Jetson Orin. ¿Cuál de las siguientes afirmaciones describe correctamente el proceso de calibración INT8?

- [x] **La calibración INT8 es opcional y TensorRT asigna automáticamente los rangos dinámicos óptimos sin necesidad de datos de entrada, igual que en FP16.** — _incorrecta_: Incorrecto: a diferencia de FP16 (que no requiere calibración porque conserva el rango exponencial de FP32), INT8 con calibración implícita necesita datos reales para estimar los rangos de activación por capa.
- [x] **La calibración INT8 en TensorRT se realiza mediante backpropagation sobre el dataset de calibración para reajustar los pesos del modelo cuantizado.** — _incorrecta_: Incorrecto: la calibración post-entrenamiento no reentrena ni ajusta pesos vía backprop; solo recopila estadísticas de activación (histogramas) para fijar los factores de escala de cuantización.
- [ ] **El calibration cache generado en una GPU de escritorio (p.ej. RTX 3090) es directamente compatible y se puede reutilizar en un Jetson Orin sin regenerarlo.** — _incorrecta_: Incorrecto: el cache de calibración está ligado a la versión de TensorRT y, en muchos casos, a la arquitectura/compute capability de la GPU, por lo que no se garantiza portabilidad entre plataformas distintas.
- [x] **La calibración INT8 requiere un conjunto representativo de datos de calibración para generar una tabla de escalas (calibration cache) que minimice la pérdida de precisión al cuantizar de FP32 a INT8.** — _correcta_: Correcto: TensorRT usa un IInt8Calibrator (p.ej. entropy calibration) que recorre un batch representativo del dataset para estimar los rangos dinámicos de activaciones por capa y generar los factores de escala.
- [ ] **Usar INT8 con calibración siempre produce mayor precisión (accuracy) del modelo que FP16, ya que reduce el ruido de cuantización.** — _incorrecta_: Incorrecto: es al revés; INT8 tiene menor resolución numérica que FP16, por lo que típicamente introduce más pérdida de accuracy, aunque gana en throughput y latencia.

> TensorRT en modo INT8 implícito necesita un calibrador que procese un subconjunto representativo del dataset de inferencia para estimar rangos dinámicos por capa y generar un calibration cache reutilizable en la misma combinación de versión de TensorRT y hardware.
>
> Repasar: `TensorRT IInt8EntropyCalibrator2 / calibration cache`

### ⚠️ Pregunta 5 — Profiling de latencia P99 con Nsight y análisis de bottlenecks sistémicos

Estás depurando picos intermitentes de latencia P99 en un pipeline DeepStream ejecutándose en un Jetson AGX. Usas Nsight Systems para capturar una traza del sistema completo (CPU, GPU, streams CUDA, DMA). ¿Cuáles de las siguientes afirmaciones son correctas respecto a este análisis?

- [x] **Nsight Systems permite visualizar la línea temporal de streams CUDA, llamadas a la API y actividad de la CPU simultáneamente, lo que ayuda a identificar si los picos de latencia P99 se deben a serialización entre kernels o a esperas de sincronización.** — _correcta_: Correcto: esa vista unificada de timeline es justo el propósito de Nsight Systems, permitiendo correlacionar huecos de inactividad de GPU con llamadas de sincronización o colas de streams saturadas.
- [ ] **Al medir latencia P99 en Jetson, es recomendable fijar el modo de energía máximo (nvpmodel -m 0) y ejecutar jetson_clocks antes de perfilar, ya que el DVFS dinámico puede introducir variabilidad y picos de latencia no representativos del rendimiento sostenido.** — _correcta_: Correcto: sin fijar las frecuencias, el gobernador de energía puede escalar dinámicamente CPU/GPU/memoria, generando outliers de latencia que confunden el análisis de bottlenecks reales del pipeline.
- [ ] **Un bottleneck causado por el bus de memoria compartido entre CPU y GPU (ancho de banda LPDDR) no es detectable con Nsight Systems, solo con herramientas de terceros.** — _incorrecta_: Incorrecto: Nsight Systems (junto con Nsight Compute y tegrastats) puede mostrar métricas de utilización de ancho de banda de memoria y contención, permitiendo detectar este tipo de cuello de botella.
- [ ] **Si Nsight Systems muestra que la GPU está inactiva (idle) durante gran parte del pipeline mientras la CPU ejecuta preprocesamiento con OpenCV, esto indica que el cuello de botella está en la etapa de preprocesamiento en CPU, candidata a moverse a GPU (p.ej. con VPI o CUDA).** — _correcta_: Correcto: huecos de inactividad de GPU alineados con actividad intensa de CPU son la señal clásica de un bottleneck de preprocesamiento, que se resuelve trasladando esas operaciones a GPU/VPI para solapar mejor el trabajo.
- [ ] **La métrica de latencia P99 es equivalente a la latencia media (mean) del pipeline, por lo que basta con optimizar el throughput medio para garantizar un buen P99.** — _incorrecta_: Incorrecto: P99 mide la cola de la distribución (el 1% de peores casos), que puede ser mala incluso con una media excelente si existen picos esporádicos causados, por ejemplo, por contención de recursos.

> El profiling de latencia de cola (P99) en Jetson combina el análisis de timeline de Nsight Systems con un entorno de energía estable (nvpmodel/jetson_clocks) para distinguir bottlenecks reales de CPU, GPU o ancho de banda de memoria frente a ruido introducido por el escalado dinámico de frecuencias.
>
> Repasar: `Nsight Systems timeline / jetson_clocks / latencia de cola (tail latency)`
