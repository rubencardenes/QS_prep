# Resultado del test — NVIDIA Jetson / CUDA / TensorRT

- Fecha: 2026-08-21 11:42
- Nivel: media
- Puntuación: **60%** (3.00/5 puntos)
- Preguntas perfectas: 2/5

## Revisión pregunta a pregunta

### ✅ Pregunta 1 — Batching de inferencias en nvinfer y gestión de queueing

Estás configurando `nvstreammux` y `nvinfer` en un pipeline DeepStream sobre Jetson con 4 fuentes de vídeo simultáneas. Necesitas ajustar el comportamiento de formación de batches y la frecuencia de inferencia para equilibrar throughput y latencia. ¿Cuáles de las siguientes afirmaciones sobre el batching y el queueing en `nvstreammux`/`nvinfer` son correctas?

- [x] **El parámetro `interval` de `nvinfer` permite ejecutar la inferencia cada N frames en lugar de en todos, útil para reducir carga computacional cuando no se necesita analizar cada fotograma.** — _correcta_: Correcto: `interval=N` hace que `nvinfer` solo procese uno de cada N+1 frames, reduciendo el coste de cómputo a cambio de menor frecuencia de detección/actualización.
- [x] **`batched-push-timeout` en `nvstreammux` define el tiempo máximo de espera para completar un batch antes de enviarlo aunque no esté lleno; valores bajos reducen la latencia pero pueden generar batches parciales con menor eficiencia de GPU.** — _correcta_: Correcto: este parámetro evita que `nvstreammux` bloquee indefinidamente esperando frames de todas las fuentes, a costa de posible infrautilización del batch si se reduce demasiado.
- [x] **El `batch-size` configurado en `nvinfer` debe coincidir con el batch estático del engine TensorRT si este se compiló sin perfil de optimización dinámico, o estar dentro del rango min/opt/max del perfil si se usó un perfil dinámico.** — _correcta_: Correcto: un engine con dimensiones estáticas fija el batch en tiempo de build; con perfiles de optimización dinámicos (`--minShapes`/`--optShapes`/`--maxShapes`), el batch en tiempo de ejecución debe caer dentro del rango permitido.
- [ ] **Aumentar el `batch-size` de `nvinfer` siempre reduce la latencia por frame, porque TensorRT paraleliza automáticamente la inferencia sin importar si hay suficientes frames disponibles en el instante de ejecución.** — _incorrecta_: Incorrecto: un batch mayor típicamente mejora el throughput agregado, pero puede aumentar la latencia individual, ya que el sistema debe esperar a acumular suficientes frames (o al timeout) antes de lanzar la inferencia.
- [ ] **`nvstreammux` siempre espera indefinidamente a que todas las fuentes entreguen un frame antes de formar un batch, sin ningún mecanismo de timeout configurable.** — _incorrecta_: Incorrecto: existe precisamente `batched-push-timeout` para evitar esa espera indefinida cuando alguna fuente está lenta o no entrega frame a tiempo.

> En DeepStream, `nvstreammux` agrupa frames de múltiples fuentes en un batch (controlado por `batch-size` y `batched-push-timeout`), y `nvinfer` consume ese batch respetando las restricciones del engine TensorRT compilado. El parámetro `interval` permite además reducir la frecuencia de inferencia. Ajustar mal estos parámetros produce cuellos de botella de latencia o infrautilización de GPU.
>
> Repasar: `nvstreammux / nvinfer batch-size, batched-push-timeout, interval`

### ✅ Pregunta 2 — Versionado de JetPack: compatibilidad CUDA, cuDNN y TensorRT

Vas a desplegar un modelo entrenado que requiere una versión concreta de TensorRT en una Jetson Orin. Sabes que JetPack es el meta-paquete que fija las versiones de L4T (BSP), CUDA, cuDNN y TensorRT que conviven en la imagen. ¿Qué afirmaciones son correctas sobre esta relación de versionado?

- [x] **Cada versión de JetPack fija una combinación específica y probada de CUDA, cuDNN y TensorRT; no se puede simplemente 'pip install' una versión arbitraria de TensorRT distinta a la que trae esa JetPack sin riesgo de incompatibilidad con el driver L4T.** — _correcta_: Correcto: JetPack empaqueta versiones certificadas conjuntamente (L4T + CUDA + cuDNN + TensorRT); mezclar versiones fuera de esa matriz de compatibilidad es una fuente común de fallos en Jetson.
- [ ] **cuDNN es opcional y no influye en TensorRT: TensorRT en Jetson no depende de cuDNN para ninguna de sus rutas de ejecución.** — _incorrecta_: Falso: TensorRT históricamente se apoya en cuDNN (y cuBLAS) para ciertas implementaciones de capas, y JetPack fija versiones compatibles de cuDNN junto con TensorRT precisamente por esa dependencia.
- [x] **Un engine TensorRT construido con la versión de TensorRT de una JetPack determinada no es necesariamente compatible con otra JetPack que traiga una versión de TensorRT distinta, por lo que suele haber que reconstruir el engine tras un upgrade de JetPack.** — _correcta_: Correcto: los engines de TensorRT están serializados para una versión concreta de TensorRT (y GPU/arquitectura); un cambio de versión de TensorRT al actualizar JetPack normalmente invalida engines previamente construidos.
- [ ] **Es seguro instalar cualquier versión de CUDA Toolkit x86 descargada de la web de NVIDIA sobre Jetson, ya que CUDA es binariamente compatible entre arquitectura ARM (Jetson) y x86 (servidor).** — _incorrecta_: Falso: Jetson usa ARM64 con un stack específico para Tegra (paquetes `l4t`/`tegra`); los paquetes CUDA x86 no son compatibles y deben instalarse los paquetes ARM/Jetson específicos, normalmente vía JetPack/SDK Manager o apt con los repos de Jetson.
- [ ] **JetPack es únicamente un instalador de aplicaciones de usuario; el kernel Linux y los drivers de GPU (L4T) son totalmente independientes y se actualizan por separado sin relación con la versión de JetPack.** — _incorrecta_: Falso: JetPack incluye L4T (Linux for Tegra), que contiene el kernel, bootloader y drivers de GPU; L4T y JetPack están estrechamente ligados, no son componentes independientes.

> JetPack actúa como una matriz de compatibilidad cerrada entre L4T (BSP/kernel/drivers), CUDA, cuDNN y TensorRT. Cambiar de versión de JetPack o intentar mezclar versiones fuera de esa matriz es una causa habitual de errores de despliegue en Jetson, y suele obligar a reconstruir los engines TensorRT existentes.
>
> Repasar: `Matriz de compatibilidad JetPack / L4T / TensorRT`

### ❌ Pregunta 3 — GStreamer debugging: identificar caps incompatibles y resolver links

Al lanzar un pipeline con `gst-launch-1.0` en una Jetson obtienes el error `Internal data stream error ... streaming stopped, reason not-negotiated (-4)` justo entre los elementos `videoconvert` y `nvinfer`. Con `GST_DEBUG=3` confirmas que `nvinfer` requiere buffers en memoria NVMM (`video/x-raw(memory:NVMM)`), mientras que `videoconvert` produce buffers en memoria de sistema estándar. ¿Cuál es la forma correcta de resolver este problema de negociación de caps?

- [ ] **Insertar un elemento `queue` entre `videoconvert` y `nvinfer` para desacoplar los hilos y resolver automáticamente la incompatibilidad de memoria.** — _incorrecta_: Incorrecto: `queue` solo desacopla hilos para buffering asíncrono, no realiza ninguna conversión de formato ni de tipo de memoria, por lo que el error de negociación persistiría.
- [x] **Sustituir `videoconvert` por `nvvideoconvert`, que sí produce y consume buffers en memoria NVMM, compatible con `nvinfer` y el resto de elementos acelerados de DeepStream.** — _correcta_: Correcto: `nvvideoconvert` es el elemento acelerado por hardware que opera con memoria NVMM; `videoconvert` es un elemento software que solo trabaja con memoria de sistema, por lo que nunca podrá satisfacer los caps de `nvinfer`.
- [ ] **El error `not-negotiated` no está relacionado con la memoria NVMM sino con el orden de carga de plugins en el registro de GStreamer; hay que reinstalar el plugin de `nvinfer`.** — _incorrecta_: Incorrecto: es un diagnóstico erróneo; el registro de plugins no afecta a la negociación de caps entre pads ya conectados, y el log de `GST_DEBUG` ya apunta claramente a la incompatibilidad de memoria.
- [x] **Forzar la negociación añadiendo un `capsfilter` con `video/x-raw(memory:NVMM)` justo después de `videoconvert`, ya que cualquier elemento puede emitir buffers NVMM si el capsfilter lo especifica.** — _incorrecta_: Incorrecto: un `capsfilter` solo restringe/filtra los caps negociables entre elementos vecinos, no transforma el tipo de memoria; `videoconvert` no sabe producir buffers NVMM independientemente del capsfilter usado.
- [ ] **Cambiar el formato de píxel de RGBA a I420 en un `capsfilter` previo a `nvinfer`, dado que ese es el único formato de color que TensorRT puede aceptar en Jetson.** — _incorrecta_: Incorrecto: el problema identificado en el log es el tipo de memoria (NVMM vs sistema), no el formato de píxel; además `nvinfer` puede trabajar con distintos formatos según la red, siempre que los buffers estén en NVMM.

> En pipelines DeepStream sobre Jetson, los elementos acelerados por hardware (`nvvideoconvert`, `nvstreammux`, `nvinfer`, etc.) operan sobre memoria NVMM, mientras que los elementos genéricos de GStreamer (`videoconvert`, `videoscale`) trabajan con memoria de sistema. Un error `not-negotiated` entre ambos tipos de elementos suele deberse a esta incompatibilidad de memoria, y se depura revisando los logs de negociación con `GST_DEBUG` y sustituyendo por la variante acelerada correspondiente.
>
> Repasar: `GStreamer caps negotiation, memory:NVMM, nvvideoconvert vs videoconvert`

### ⚠️ Pregunta 4 — Construcción de engines TensorRT con batch dinámico

Necesitas construir un engine TensorRT a partir de un modelo ONNX que debe aceptar tamaños de batch variables en tiempo de inferencia (por ejemplo, entre 1 y 8 imágenes según la carga del sistema). ¿Qué opción(es) describen correctamente cómo lograrlo con `trtexec`/el `Builder` de TensorRT?

- [ ] **Basta con exportar el ONNX con un batch fijo (por ejemplo batch=1) y luego, en tiempo de inferencia, TensorRT ajusta automáticamente el engine para aceptar cualquier batch sin necesidad de perfiles.** — _incorrecta_: Falso: si el ONNX y el engine se construyen con dimensión de batch fija, el engine solo acepta ese tamaño exacto; para tamaños variables el ONNX debe exportarse con eje dinámico (p.ej. `-1`) y el engine debe construirse con un perfil de optimización.
- [ ] **Si se definen varios rangos de batch muy distantes entre `kMIN` y `kMAX` (p. ej. de 1 a 8), TensorRT garantiza el mismo rendimiento óptimo en todos los tamaños intermedios, ya que el motor se recompila internamente en cada inferencia según el batch real.** — _incorrecta_: Falso: TensorRT optimiza principalmente en torno a la forma `kOPT`; el rendimiento en otros tamaños dentro del rango puede ser subóptimo, y no hay recompilación en tiempo de inferencia (el engine ya está serializado).
- [x] **Con `trtexec` esto se puede indicar con flags como `--minShapes=input:1x3x224x224 --optShapes=input:4x3x224x224 --maxShapes=input:8x3x224x224`.** — _correcta_: Correcto: `trtexec` expone exactamente estos flags para definir el perfil de optimización de forma dinámica sin escribir código C++/Python manualmente.
- [ ] **El batch dinámico solo es soportado en TensorRT si se usa precisión FP32; en FP16 o INT8 el batch debe ser necesariamente estático.** — _incorrecta_: Falso: los perfiles de optimización dinámica son independientes de la precisión elegida; se pueden combinar shapes dinámicos con FP16 o INT8 sin restricción de este tipo.
- [ ] **Hay que definir un `IOptimizationProfile` que especifique dimensiones mínima, óptima y máxima (`kMIN`, `kOPT`, `kMAX`) para el eje de batch del input, y asociarlo a la configuración del builder antes de construir el engine.** — _correcta_: Correcto: el batch dinámico en TensorRT se gestiona mediante perfiles de optimización que fijan rangos min/opt/max por dimensión; sin un perfil válido para una dimensión dinámica, el builder no puede construir el engine.

> El soporte de batch dinámico en TensorRT se implementa mediante 'optimization profiles' que definen rangos min/opt/max por dimensión de entrada, tanto en la API de builder como mediante los flags equivalentes de `trtexec`. Es un mecanismo distinto de la precisión (FP16/INT8) y no ofrece rendimiento garantizado uniforme en todo el rango, solo en torno al shape óptimo elegido.
>
> Repasar: `IOptimizationProfile / trtexec --minShapes --optShapes --maxShapes`

### ⚠️ Pregunta 5 — Arquitectura Tegra y jerarquía de memoria en Jetson Orin

Un SoC Jetson Orin integra CPU (clúster ARM Cortex-A78AE), GPU Ampere y aceleradores dedicados (DLA, PVA) sobre un mismo módulo con memoria LPDDR5 compartida. Respecto a la jerarquía de memoria y el modelo de acceso unificado en Jetson, ¿cuáles de las siguientes afirmaciones son correctas?

- [ ] **El DLA (Deep Learning Accelerator) de Jetson Orin tiene su propio banco de DRAM físicamente aislado del de la GPU, por lo que siempre requiere copia intermedia.** — _incorrecta_: Falso: el DLA también accede a la misma memoria del sistema (LPDDR5) que la GPU y la CPU; no dispone de una DRAM propia separada en el módulo.
- [ ] **Aun con memoria unificada, es obligatorio llamar a `cudaMemcpy` entre host y device en cada frame para que los datos capturados por la cámara sean visibles para el kernel CUDA.** — _incorrecta_: Falso: precisamente la ventaja de la memoria unificada en Jetson es evitar ese `cudaMemcpy`; con buffers correctamente asignados (unified/mapped/NVMM) el kernel puede acceder directamente sin copia explícita.
- [x] **La memoria unificada en Jetson implica que no existen nunca 'page faults' ni migraciones de páginas gestionadas por CUDA Unified Memory (`cudaMallocManaged`), porque todo el acceso es directo.** — _incorrecta_: Falso: aunque la DRAM física es compartida, si se usa `cudaMallocManaged` el runtime sigue gestionando páginas y puede haber coherencia/migraciones lógicas gestionadas por el driver, aunque el coste sea mucho menor que en un sistema con PCIe.
- [x] **CPU y GPU acceden al mismo banco físico de DRAM (LPDDR5), por lo que no existe una copia física separada entre 'memoria de host' y 'memoria de device' como en un sistema con GPU discreta y PCIe.** — _correcta_: Correcto: en Jetson (arquitectura SoC integrada) la memoria es física y físicamente unificada, a diferencia de un servidor con GPU dGPU conectada por PCIe donde host y device tienen DRAM separada.
- [x] **Usar memoria 'pinned' o zero-copy (`cudaHostAlloc` con `cudaHostAllocMapped`, o los buffers NVMM de DeepStream) evita una copia redundante en RAM, ya que CPU y GPU ya comparten el mismo espacio físico.** — _correcta_: Correcto: al no haber bus PCIe de por medio, apoyarse en memoria mapeada/zero-copy permite que GPU y CPU/ISP compartan el mismo buffer físico sin duplicarlo, que es justo la ventaja que explotan NVMM y `cudaHostAlloc` mapeado en Jetson.

> Jetson Orin es un SoC con memoria física unificada entre CPU, GPU y aceleradores (DLA/PVA), lo que elimina la necesidad de copias por PCIe típicas de sistemas con GPU discreta. Aprovechar esto mediante memoria mapeada/zero-copy o buffers NVMM es clave para optimizar pipelines de inferencia embebida, aunque el software (CUDA runtime) sigue teniendo su propio modelo de gestión de páginas.
>
> Repasar: `CUDA Unified Memory en SoC Tegra / zero-copy / NVMM`
