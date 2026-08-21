# Resultado del test — Computer Vision (teoría y algoritmos)

- Fecha: 2026-08-04 16:26
- Nivel: media
- Puntuación: **68%** (3.42/5 puntos)
- Preguntas perfectas: 2/5

## Revisión pregunta a pregunta

### ⚠️ Pregunta 1 — Formación óptica, distorsiones radiales y corrección de lentes

Respecto a la formación de imagen a través de una lente real y los modelos de distorsión óptica (radial y tangencial) empleados para corregirla en visión por computador, ¿cuáles de las siguientes afirmaciones son correctas?

- [x] **`cv2.undistort()` solo necesita la matriz intrínseca K, sin los coeficientes de distorsión, para corregir la imagen** — _incorrecta_: Incorrecto. La función necesita tanto K como el vector de coeficientes de distorsión (k1, k2, p1, p2, k3...); sin estos últimos no puede compensar la deformación óptica.
- [ ] **Los coeficientes de distorsión tangencial (p1, p2) modelan el desalineamiento entre el plano del sensor y el eje óptico de la lente** — _correcta_: Correcto. La distorsión tangencial surge cuando la lente no está perfectamente paralela al plano del sensor (descentrado), y se modela con p1 y p2, distinto de los coeficientes radiales k1, k2, k3.
- [ ] **La distorsión radial puede corregirse completamente con una transformación afín global, sin necesidad de un modelo polinómico** — _incorrecta_: Incorrecto. Una transformación afín es lineal y global, mientras que la distorsión radial es no lineal y depende de la distancia al centro óptico; requiere un modelo polinómico (radial) para corregirse adecuadamente.
- [x] **La distorsión en cojín ('pincushion') es común en teleobjetivos y hace que las líneas rectas se curven hacia el centro de la imagen** — _correcta_: Correcto. Aquí la magnificación aumenta con la distancia al centro, lo contrario de la distorsión de barril, y suele aparecer en objetivos de focal larga.
- [x] **La distorsión de barril ('barrel') hace que las líneas rectas se curven hacia afuera del centro de la imagen, y es típica de lentes gran angular** — _correcta_: Correcto. En la distorsión de barril la magnificación disminuye con la distancia al centro óptico, curvando las líneas rectas hacia afuera; es habitual en objetivos de focal corta o gran angular.

> El modelo de lente delgada ideal no existe en la práctica: las lentes reales introducen distorsión radial (barril/cojín) y tangencial (por desalineamiento), que se estiman durante la calibración de cámara (p. ej. con el método de Zhang) y se corrigen aplicando el modelo polinómico inverso, típicamente con `cv2.undistort` o `cv2.initUndistortRectifyMap`.
>
> Repasar: `Distorsión radial y tangencial de lente (modelo de Brown-Conrady)`

### ✅ Pregunta 2 — Augmentación de datos y regularización en redes profundas para visión

Un ingeniero entrena una CNN para clasificación de imágenes con un conjunto de entrenamiento limitado y observa sobreajuste (buena precisión en entrenamiento, mala en validación). Decide aplicar técnicas de augmentación de datos y regularización. ¿Cuáles de las siguientes afirmaciones son correctas?

- [x] **La regularización L2 (weight decay) añade un término a la función de pérdida proporcional al cuadrado de la norma de los pesos, penalizando pesos grandes y favoreciendo soluciones más suaves.** — _correcta_: Correcto. El weight decay añade λ‖W‖² a la pérdida, lo que empuja los pesos hacia valores menores durante la optimización, reduciendo la complejidad efectiva del modelo y mitigando el sobreajuste.
- [x] **Aplicar volteo horizontal (horizontal flip) como augmentación es apropiado para clasificar razas de perros, pero puede ser problemático para tareas donde la orientación es semánticamente relevante, como reconocer texto o dígitos.** — _correcta_: Correcto. El volteo horizontal introduce una invariancia deseable cuando la clase no depende de la orientación (p. ej. animales), pero puede generar ejemplos inválidos o etiquetas incorrectas en tareas sensibles a la orientación, como OCR o distinguir '6' de '9'.
- [x] **La augmentación de datos mediante recortes aleatorios (random cropping), rotaciones pequeñas y jitter de color aumenta la variedad efectiva del conjunto de entrenamiento sin necesidad de recolectar nuevas imágenes, ayudando a reducir el sobreajuste.** — _correcta_: Correcto. Estas transformaciones generan variantes plausibles de las imágenes originales, exponiendo a la red a mayor variabilidad de escala, encuadre e iluminación, lo que mejora la generalización sin coste adicional de etiquetado.
- [ ] **Usar batch normalization elimina por completo la necesidad de cualquier otra técnica de regularización, ya que por sí sola garantiza que el modelo no sobreajuste el conjunto de entrenamiento.** — _incorrecta_: Incorrecto. Aunque batch normalization tiene un efecto regularizador leve (al introducir ruido dependiente del minibatch) y acelera/estabiliza el entrenamiento, no elimina el sobreajuste por sí sola; en la práctica se combina con dropout, weight decay o augmentación según el caso.
- [x] **Dropout, aplicado durante entrenamiento a las activaciones de capas totalmente conectadas, desactiva aleatoriamente un subconjunto de neuronas en cada paso, forzando a la red a no depender excesivamente de neuronas individuales.** — _correcta_: Correcto. Dropout (Srivastava et al., 2014) pone a cero activaciones con probabilidad p en cada forward pass durante el entrenamiento, actuando como regularizador al evitar la coadaptación excesiva de neuronas, y se desactiva (o se reescala) en inferencia.

> Frente al sobreajuste en visión por computador se combinan típicamente augmentación de datos (flips, crops, rotaciones, color jitter, cutout/mixup) para incrementar la diversidad efectiva de entrenamiento, y técnicas de regularización explícitas (dropout, weight decay, early stopping) que limitan la capacidad efectiva del modelo. Es importante elegir augmentaciones coherentes con las invariancias reales de la tarea, ya que transformaciones inadecuadas (como el flip en OCR) pueden introducir ruido de etiquetado.
>
> Repasar: `Data augmentation, dropout, weight decay (L2)`

### ✅ Pregunta 3 — Flujo óptico denso: movimiento 2D entre fotogramas consecutivos

¿Cuál de las siguientes afirmaciones sobre el flujo óptico denso (estimación del vector de movimiento en cada píxel entre dos fotogramas consecutivos) es correcta?

- [x] **El flujo óptico denso calcula el vector de movimiento (u, v) para cada píxel de la imagen, a diferencia de Lucas-Kanade disperso, que solo lo hace en puntos de interés seleccionados** — _correcta_: Correcto. Esa es precisamente la distinción: los métodos densos (Farneback, Horn-Schunck, redes tipo FlowNet/RAFT) estiman flujo en todo el campo de la imagen, mientras que Lucas-Kanade disperso solo lo hace en esquinas o puntos rastreables previamente detectados.
- [ ] **El algoritmo de Farneback asume que el brillo de un píxel se conserva entre fotogramas y no requiere ninguna suposición sobre suavidad del movimiento** — _incorrecta_: Incorrecto. Farneback sí parte de la constancia de brillo, pero además aproxima los vecindarios mediante polinomios y regulariza asumiendo variación suave del flujo entre píxeles vecinos; sin esa suposición el problema queda indeterminado.
- [ ] **El flujo óptico denso es invariante a cambios de iluminación entre fotogramas gracias al término It** — _incorrecta_: Incorrecto. Todo lo contrario: la hipótesis de constancia de brillo (base de It) se viola precisamente cuando hay cambios de iluminación, sombras o reflejos, degradando la estimación.
- [ ] **El flujo óptico denso solo puede aplicarse a pares de imágenes estéreo rectificadas, no a fotogramas consecutivos de vídeo** — _incorrecta_: Incorrecto. Es justo al revés: el flujo óptico se calcula típicamente entre fotogramas consecutivos de una secuencia temporal; la búsqueda restringida a líneas epipolares horizontales es propia del emparejamiento estéreo, no del flujo óptico.
- [ ] **La ecuación de restricción del flujo óptico (Ix·u + Iy·v + It = 0) permite por sí sola resolver de forma única u y v en cada píxel, sin necesitar restricciones adicionales** — _incorrecta_: Incorrecto. Es una única ecuación con dos incógnitas por píxel (problema de apertura); se necesita una restricción adicional, como suavidad global (Horn-Schunck) o asumir un vecindario con movimiento constante (Lucas-Kanade).

> El flujo óptico denso estima, para cada píxel, el desplazamiento 2D aparente entre dos fotogramas consecutivos asumiendo constancia de brillo local. Como esa ecuación es indeterminada por sí sola (problema de apertura), los métodos densos añaden una restricción adicional (suavidad global, polinomios locales, o aprendizaje profundo) para producir un campo de flujo completo, a diferencia de los métodos dispersos que solo lo calculan en puntos característicos.
>
> Repasar: `Flujo óptico denso (Horn-Schunck, Farneback, problema de apertura)`

### ⚠️ Pregunta 4 — Cascadas Haar: detección de objetos con características integrales

Sobre el detector de objetos basado en cascadas Haar (Viola-Jones), que combina características Haar calculadas mediante la imagen integral con un clasificador en cascada de etapas AdaBoost, ¿cuáles de las siguientes afirmaciones son correctas?

- [ ] **El detector Viola-Jones es intrínsecamente invariante a rotaciones del objeto en el plano de la imagen, por lo que no requiere entrenar cascadas específicas para distintas orientaciones.** — _incorrecta_: Incorrecto. Las características Haar son sensibles a la orientación (patrones de bordes horizontales/verticales/diagonales alineados con los ejes); rotaciones significativas degradan mucho el rendimiento, por lo que en la práctica se entrenan cascadas separadas o se usa detección multi-orientación.
- [ ] **Cada clasificador débil de AdaBoost utilizado en una etapa de la cascada corresponde típicamente a un umbral sobre el valor de una única característica Haar (rectangular).** — _correcta_: Correcto. AdaBoost selecciona, en cada ronda, la característica Haar individual que mejor separa positivos y negativos y construye un clasificador débil basado en un umbral simple sobre esa característica.
- [x] **La imagen integral permite calcular la suma de píxeles de cualquier región rectangular en tiempo constante (O(1)), independientemente del tamaño del rectángulo.** — _correcta_: Correcto. La imagen integral precalcula sumas acumuladas, de modo que la suma de cualquier rectángulo se obtiene con solo 4 accesos y 3 operaciones aritméticas, sin depender de su área.
- [x] **Si una subventana es rechazada por una etapa intermedia de la cascada, no se evalúan las etapas siguientes para esa subventana, lo que constituye la base de su eficiencia en tiempo real.** — _correcta_: Correcto. El rechazo temprano ('early rejection') es exactamente el mecanismo que evita evaluar las etapas restantes en la mayoría de subventanas, permitiendo procesamiento en tiempo real como en la detección facial clásica de OpenCV.
- [x] **La estructura en cascada acelera la detección porque las primeras etapas, simples y rápidas, descartan la mayoría de subventanas negativas, dejando que solo una fracción pequeña llegue a las etapas posteriores más costosas.** — _correcta_: Correcto. Este es el principio clave de Viola-Jones: etapas tempranas con pocos clasificadores débiles rechazan rápidamente la mayoría del fondo, concentrando el coste computacional solo en regiones prometedoras.

> El algoritmo Viola-Jones (2001) introdujo tres ideas combinadas: características Haar rectangulares, la imagen integral para evaluarlas en O(1), y un clasificador en cascada entrenado con AdaBoost donde etapas tempranas de bajo coste descartan la mayor parte del fondo. No es invariante a rotación ni a cambios de escala arbitrarios sin ajustes (se usa una pirámide de escalas), y su robustez ante rotaciones en el plano es limitada salvo que se entrenen modelos específicos.
>
> Repasar: `Viola-Jones, imagen integral, AdaBoost en cascada`

### ⚠️ Pregunta 5 — Pirámides Gaussianas: submuestreo progresivo y procesamiento multiescala

Sobre la construcción y el uso de pirámides Gaussianas (y su relación con las pirámides Laplacianas) para el procesamiento multiescala de imágenes, ¿cuáles de las siguientes afirmaciones son correctas?

- [ ] **Al aumentar el número de niveles de una pirámide Gaussiana, la resolución espacial de cada nivel superior aumenta progresivamente respecto al nivel base** — _incorrecta_: Incorrecto. Es al contrario: cada nivel superior de la pirámide tiene menor resolución (típicamente la mitad en cada dimensión) que el nivel inferior, ya que se va submuestreando progresivamente.
- [ ] **La pirámide Laplaciana se construye como la diferencia entre un nivel de la pirámide Gaussiana y la versión expandida (upsampled) del siguiente nivel más grueso, y se usa para reconstrucción o compresión** — _correcta_: Correcto. Cada nivel Laplaciano captura los detalles perdidos al pasar de un nivel Gaussiano al siguiente más grueso, permitiendo reconstruir la imagen original sumando estos residuos y siendo útil en compresión y mezcla (blending) de imágenes.
- [x] **El espacio de escalas (scale space) que usa SIFT para detectar puntos clave invariantes a escala se construye mediante diferencias de Gaussianas (DoG) calculadas dentro de octavas de una pirámide Gaussiana** — _correcta_: Correcto. SIFT genera varias imágenes suavizadas con Gaussianas de sigma creciente dentro de cada octava y resta pares consecutivos (DoG) como aproximación eficiente del Laplaciano de Gauss, buscando extremos locales en escala y espacio.
- [x] **Submuestrear una imagen sin aplicar previamente un filtro de suavizado no genera artefactos de aliasing siempre que el factor de submuestreo sea un número entero** — _incorrecta_: Incorrecto. El aliasing depende del contenido frecuencial de la imagen respecto a la nueva frecuencia de muestreo, no de si el factor es entero; sin un filtro paso-bajo previo aparecerán artefactos siempre que existan frecuencias por encima del nuevo límite de Nyquist.
- [x] **Cada nivel de la pirámide Gaussiana se obtiene aplicando un filtro de suavizado (típicamente Gaussiano) antes de submuestrear la imagen a la mitad de su resolución, lo que ayuda a evitar aliasing** — _correcta_: Correcto. El suavizado previo actúa como filtro antialiasing (limita el contenido de alta frecuencia) antes de reducir la tasa de muestreo espacial, cumpliendo aproximadamente el criterio de Nyquist en cada nivel.

> La pirámide Gaussiana representa la imagen en múltiples escalas mediante suavizado y submuestreo sucesivos, sirviendo de base para técnicas multiescala como la detección de características invariantes a escala (SIFT), el flujo óptico piramidal (Lucas-Kanade multiescala) o la fusión de imágenes. La pirámide Laplaciana, derivada de ella, almacena los detalles de alta frecuencia perdidos entre niveles y permite reconstrucción exacta.
>
> Repasar: `Pirámides Gaussiana y Laplaciana; espacio de escalas (DoG) en SIFT`
