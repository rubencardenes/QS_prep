# Resultado del test — NVIDIA Jetson / CUDA / TensorRT

- Fecha: 2026-08-05 13:01
- Nivel: media
- Puntuación: **100%** (5.00/5 puntos)
- Preguntas perfectas: 5/5

## Revisión pregunta a pregunta

### ✅ Pregunta 1 — Quantización en TensorRT: precisión FP16 versus INT8 y trade-offs

Estás optimizando un modelo de detección de objetos con TensorRT para desplegarlo en una Jetson Orin y dudas entre construir el engine en FP16 o en INT8. ¿Cuáles de las siguientes afirmaciones sobre el trade-off FP16 vs INT8 son correctas?

- [ ] **Usar INT8 elimina la necesidad de validar la exactitud del modelo tras la cuantización, ya que TensorRT garantiza equivalencia numérica con FP32.** — _incorrecta_: Incorrecto: TensorRT no garantiza equivalencia numérica en INT8; siempre hay que validar métricas (mAP, accuracy, etc.) sobre un conjunto de validación tras generar el engine cuantizado.
- [x] **FP16 reduce el rango dinámico respecto a FP32 pero suele mantener suficiente precisión para la mayoría de redes convolucionales sin pérdida notable de exactitud.** — _correcta_: Correcto: FP16 conserva 10 bits de mantisa y en la práctica la mayoría de CNNs toleran bien la conversión directa, con caídas de accuracy típicamente marginales.
- [x] **INT8 requiere un paso de calibración (con un dataset representativo) o entrenamiento consciente de la cuantización (QAT) para minimizar la pérdida de precisión, mientras que FP16 normalmente puede aplicarse sin ese paso adicional.** — _correcta_: Correcto: TensorRT necesita estadísticas de rango dinámico por tensor (calibración con IInt8EntropyCalibrator2 u otro) o pesos ya cuantizados vía QAT para INT8; FP16 solo requiere marcar el flag de precisión, sin calibración.
- [ ] **INT8 siempre ofrece mayor throughput que FP16 en cualquier capa de la red, independientemente de si esa capa tiene kernels INT8 optimizados disponibles.** — _incorrecta_: Incorrecto: si una capa no tiene implementación INT8 eficiente, TensorRT puede recurrir a FP32/FP16 para esa capa (con reformateos adicionales), lo que puede anular o incluso invertir la ganancia esperada.
- [x] **En los Tensor Cores de Jetson (Xavier/Orin), INT8 puede llegar a duplicar aproximadamente el throughput respecto a FP16 en capas compatibles, a costa de mayor riesgo de degradación de precisión si la calibración es pobre.** — _correcta_: Correcto: los Tensor Cores procesan operaciones INT8 con mayor densidad que FP16, típicamente ~2x throughput teórico en capas soportadas, pero la cuantización agresiva puede degradar la exactitud si el dataset de calibración no es representativo.

> FP16 es casi 'gratis' en precisión pero con menor ganancia de rendimiento que INT8; INT8 exige calibración o QAT y validación posterior, y su beneficio de throughput depende de que las capas tengan kernels INT8 soportados por el hardware.
>
> Repasar: `TensorRT INT8 calibration (IInt8EntropyCalibrator2) vs FP16 precision flags`

### ✅ Pregunta 2 — Gestión de modos de potencia: nvpmodel y jetson_clocks

En una Jetson en producción necesitas maximizar el rendimiento sostenido de inferencia y evitar variabilidad de latencia causada por el escalado dinámico de frecuencias (DVFS). Ejecutas lo siguiente:
```bash
sudo nvpmodel -m 0
sudo jetson_clocks
```
¿Qué afirmaciones son correctas sobre este procedimiento?

- [ ] **Aplicar `jetson_clocks` es seguro para operación continua 24/7 sin ninguna consideración térmica adicional, ya que Jetson gestiona automáticamente el throttling térmico de forma transparente para el usuario.** — _incorrecta_: Falso: aunque existe protección por throttling térmico a nivel hardware/firmware, mantener los relojes al máximo de forma sostenida sin disipación adecuada puede provocar throttling no deseado, reduciendo el rendimiento real por debajo del esperado.
- [x] **`nvpmodel -q` permite consultar el modo de energía actualmente activo y el listado de modos disponibles definidos para ese módulo Jetson.** — _correcta_: Correcto: `nvpmodel -q` (o `nvpmodel -q --verbose`) muestra el modo activo y, en modo verboso, todos los perfiles configurados en nvpmodel.conf.
- [x] **`nvpmodel -m 0` selecciona un perfil de energía (normalmente el de máximo rendimiento, aunque el número de modo depende del módulo concreto), definiendo el número máximo de núcleos activos y los techos de frecuencia permitidos para CPU/GPU/EMC.** — _correcta_: Correcto: nvpmodel gestiona perfiles predefinidos en /etc/nvpmodel.conf que limitan núcleos activos y frecuencias máximas; el modo 0 suele ser el de mayor rendimiento pero esto varía según el módulo Jetson.
- [x] **`jetson_clocks` fija las frecuencias de CPU, GPU y EMC a su valor máximo permitido por el perfil nvpmodel activo, eliminando el escalado dinámico (DVFS) y por tanto reduciendo la variabilidad de latencia.** — _correcta_: Correcto: jetson_clocks bloquea los relojes al máximo dentro de los límites del modo nvpmodel activo, útil para benchmarking o inferencia con latencia predecible, a costa de mayor consumo y temperatura.
- [ ] **El orden de ejecución es indiferente: `jetson_clocks` sobrescribe permanentemente la configuración de `nvpmodel`, por lo que ejecutar `nvpmodel` después no tiene ningún efecto.** — _incorrecta_: Falso: el orden importa. jetson_clocks aplica los máximos permitidos por el perfil nvpmodel vigente en ese momento; si cambias de modo con nvpmodel después, los límites cambian y conviene volver a ejecutar jetson_clocks.

> nvpmodel controla perfiles de energía (número de núcleos activos y techos de frecuencia) mientras jetson_clocks fuerza las frecuencias al máximo permitido por el perfil activo, eliminando el DVFS para maximizar rendimiento sostenido y reducir jitter, aunque a costa de mayor consumo/temperatura que debe gestionarse con disipación adecuada.
>
> Repasar: `nvpmodel / jetson_clocks / DVFS en Jetson`

### ✅ Pregunta 3 — Engines TensorRT: compilación, optimización de grafos y serialización binaria

Compilas un modelo ONNX a un engine TensorRT en una Jetson AGX Orin usando `trtexec` y guardas el resultado con `--saveEngine=model.engine`. Más adelante intentas cargar ese mismo archivo `.engine` en otra Jetson Xavier NX sin recompilar. ¿Qué afirmaciones son correctas sobre el proceso de construcción y portabilidad de engines TensorRT?

- [x] **Durante la construcción del engine, TensorRT aplica optimizaciones de grafo como fusión de capas (por ejemplo, convolución + bias + activación) y selecciona los kernels más eficientes disponibles para la GPU objetivo mediante autotuning.** — _correcta_: Correcto: el builder de TensorRT realiza fusiones de capas (layer fusion), eliminación de nodos redundantes y un proceso de autotuning que perfila varios kernels/tácticas candidatas para elegir la implementación más rápida en el hardware detectado.
- [x] **Por buena práctica, para desplegar en la Xavier NX se debería reconstruir el engine en (o para) esa plataforma específica, en lugar de reutilizar el binario generado para Orin.** — _correcta_: Correcto: dado que el engine está optimizado para una arquitectura de GPU y versión de TensorRT concretas, la práctica recomendada es regenerar el engine en/para el hardware de destino para garantizar compatibilidad y aprovechar el autotuning específico de esa GPU.
- [ ] **El archivo `.engine` serializado es portable entre cualquier GPU con CUDA, incluyendo GPUs de escritorio y distintos módulos Jetson, siempre que se use la misma versión de TensorRT.** — _incorrecta_: Falso: un engine serializado está optimizado y generalmente ligado a la arquitectura de GPU específica (y a la versión de TensorRT/CUDA) con la que se compiló; cargarlo en un Orin construido para Xavier NX (u otra arquitectura) puede fallar o requerir recompilación.
- [ ] **Cargar el engine en la Xavier NX funcionará sin problemas siempre que ambas Jetson tengan instalado JetPack, independientemente de la versión de TensorRT o la arquitectura de GPU de cada módulo.** — _incorrecta_: Falso: la compatibilidad de un engine depende de la versión exacta de TensorRT (y CUDA/cuDNN) usada al construirlo, así como de la arquitectura de GPU objetivo; JetPack instalado no garantiza compatibilidad binaria del engine entre módulos distintos.

> El proceso de build de TensorRT combina optimización de grafo (fusión de capas, eliminación de nodos) con autotuning de kernels específico de la GPU objetivo, generando un engine serializado que no es portable entre arquitecturas de GPU o versiones de TensorRT distintas; por ello, desplegar en otro módulo Jetson requiere reconstruir el engine para esa plataforma.
>
> Repasar: `TensorRT engine build, layer fusion, autotuning y portabilidad de engines serializados`

### ✅ Pregunta 4 — Diferencias de arquitectura entre módulos Jetson: Nano, NX, AGX y Orin

Estás eligiendo entre varios módulos Jetson (Nano, Xavier NX, AGX Xavier, AGX Orin) para un proyecto de visión embebida que requiere ejecutar varios modelos de deep learning simultáneamente con buen rendimiento en INT8. ¿Qué afirmaciones sobre las diferencias de arquitectura entre estos módulos son correctas?

- [ ] **Todos los módulos Jetson, incluido el Nano, comparten exactamente la misma cantidad de núcleos DLA y la misma capacidad de memoria unificada, variando únicamente la frecuencia de reloj de la CPU.** — _incorrecta_: Falso: Nano no tiene DLA en absoluto, y la capacidad de memoria unificada (LPDDR) varía considerablemente entre módulos (desde 2-4 GB en Nano hasta 32-64 GB en AGX Orin), no solo la frecuencia de CPU.
- [x] **Los módulos Xavier (NX y AGX) y Orin incluyen DLA (Deep Learning Accelerator), un motor de inferencia separado de la GPU que puede ejecutar ciertas capas de red en paralelo para liberar carga de la GPU.** — _correcta_: Correcto: tanto la familia Xavier como Orin incorporan uno o dos núcleos DLA, utilizables vía TensorRT para descargar capas soportadas de la GPU, aumentando el throughput agregado en cargas concurrentes.
- [x] **Jetson Nano usa una GPU Maxwell sin núcleos Tensor Core dedicados, por lo que no se beneficia de la aceleración especializada de INT8/FP16 que sí ofrecen las GPUs Volta (Xavier) y Ampere (Orin).** — _correcta_: Correcto: la GPU Maxwell de Nano carece de Tensor Cores; la aceleración de precisión reducida en Nano depende más de operaciones CUDA genéricas, mientras que Xavier (Volta) y Orin (Ampere) sí incluyen Tensor Cores dedicados.
- [ ] **Xavier NX y AGX Xavier usan exactamente el mismo número de núcleos CPU, GPU y DLA, diferenciándose únicamente en el formato físico del módulo (tamaño del conector).** — _incorrecta_: Falso: aunque comparten la misma generación de SoC (Xavier), AGX Xavier tiene más núcleos GPU/CPU activados y mayor TDP configurable que Xavier NX, además de diferir en formato físico.
- [x] **Jetson AGX Orin utiliza una arquitectura de GPU Ampere con soporte para tipos de datos INT8 y FP16, y en algunas variantes también soporte de esparsidad estructurada, ofreciendo mayor TOPS que Xavier a paridad de consumo.** — _correcta_: Correcto: Orin usa GPU Ampere con Tensor Cores de tercera generación (soporte de esparsidad en ciertos tipos de dato) y ofrece un salto notable en TOPS/W respecto a Xavier, gracias también a proceso de fabricación más avanzado.

> La familia Jetson abarca generaciones de SoC distintas: Nano (Maxwell, sin DLA), Xavier NX/AGX (Volta con Tensor Cores + DLA) y Orin (Ampere con Tensor Cores de 3ª gen, posible esparsidad, mayor TOPS/W). Elegir el módulo correcto depende de los requisitos de throughput, precisión y presupuesto energético.
>
> Repasar: `Comparativa Jetson Nano/NX/AGX/Orin (Maxwell vs Volta vs Ampere, DLA)`

### ✅ Pregunta 5 — Configuración de cámaras CSI: resolución, frame rate y formato de pixeles

Tienes una cámara CSI IMX219 conectada a una Jetson y quieres capturar con `nvarguscamerasrc` a 1920x1080 y 60 fps en formato NV12 antes de pasarlo a `nvinfer`. Al lanzar el pipeline, GStreamer falla indicando que no encuentra un 'sensor mode' que soporte esa combinación. ¿Cuál es la causa más probable y la solución correcta?

- [x] **El sensor CSI expone un conjunto fijo de modos (resolución + frame rate + formato) definidos en el driver del sensor; hay que fijar explícitamente un `sensor-mode` (o ajustar resolución/fps) a uno de los modos válidos, ya que no cualquier combinación arbitraria está soportada.** — _correcta_: Correcto: los drivers de sensores CSI (p. ej. vía device tree) publican un catálogo limitado de modos; 1080p a 60 fps puede no existir como modo nativo en el IMX219 (que sí soporta, por ejemplo, 1080p a 30 fps u otras combinaciones), así que hay que elegir un `sensor-mode` compatible.
- [ ] **GStreamer soporta cualquier combinación arbitraria de resolución y frame rate para cámaras CSI; el fallo se debe a un bug en `nvvideoconvert` que hay que solucionar recompilando el plugin.** — _incorrecta_: Incorrecto: la limitación no viene de `nvvideoconvert` sino de las capacidades físicas/de driver del propio sensor CSI, que solo admite ciertos modos discretos de captura.
- [ ] **Hay que sustituir el driver CSI por un driver v4l2 genérico de cámara USB, ya que las cámaras CSI no permiten configurar resolución ni frame rate.** — _incorrecta_: Incorrecto: las cámaras CSI sí permiten configurar resolución y frame rate, pero dentro de los modos discretos que expone el driver del sensor, no mediante un driver USB genérico que no aplica a interfaces CSI.
- [ ] **El formato NV12 no es compatible con cámaras CSI en Jetson; hay que forzar RGBA como formato de captura obligatorio en `nvarguscamerasrc`.** — _incorrecta_: Incorrecto: NV12 es precisamente el formato nativo típico de salida en memoria NVMM para `nvarguscamerasrc`/ISP en Jetson, ampliamente usado en pipelines DeepStream.

> Las cámaras CSI en Jetson no aceptan combinaciones arbitrarias de resolución, frame rate y formato: el driver del sensor define 'sensor modes' fijos, y hay que seleccionar (o dejar que se autoseleccione) uno compatible con lo solicitado en el pipeline.
>
> Repasar: `nvarguscamerasrc sensor-mode y modos soportados por el driver del sensor CSI`
