# Resultado del test — Computer Vision (teoría y algoritmos)

- Fecha: 2026-08-04 15:17
- Nivel: media
- Puntuación: **27%** (1.33/5 puntos)
- Preguntas perfectas: 0/5

## Revisión pregunta a pregunta

### ⚠️ Pregunta 1 — Homografías: transformaciones proyectivas 2D y rectificación de imágenes

Sobre las homografías (matriz H de 3x3 que relaciona planos mediante una transformación proyectiva) y su uso en rectificación de imágenes y mosaicos, ¿cuáles de las siguientes afirmaciones son correctas?

- [ ] **Una homografía puede relacionar exactamente dos vistas de una escena 3D arbitraria con relieve, siempre que las cámaras no compartan el mismo centro óptico.** — _incorrecta_: Incorrecto: una homografía solo relaciona exactamente dos vistas cuando la escena es plana o cuando la cámara realiza una rotación pura alrededor de su centro óptico; para escenas con relieve y traslación de cámara aparece paralaje que la homografía no modela.
- [x] **RANSAC no es aplicable a la estimación de homografías porque estas son transformaciones lineales exactas que no requieren rechazo de outliers.** — _incorrecta_: Incorrecto: RANSAC se usa precisamente para estimar homografías de forma robusta frente a correspondencias erróneas (outliers) generadas por el emparejamiento de features.
- [x] **La rectificación de una imagen mediante homografía se usa para eliminar la distorsión de perspectiva y convertir un plano fotografiado oblicuamente en una vista frontal.** — _correcta_: Correcto: es una aplicación clásica, por ejemplo para 'enderezar' un documento o una fachada fotografiada en ángulo, mapeando el plano a coordenadas frontoparalelas.
- [x] **Para estimar una homografía con el algoritmo DLT (Direct Linear Transform) se necesitan al menos 4 correspondencias de puntos no colineales entre las dos imágenes.** — _correcta_: Correcto: cada correspondencia aporta 2 ecuaciones y hay 8 incógnitas, por lo que se requieren mínimo 4 puntos en posición general (no colineales).
- [ ] **Una homografía tiene 8 grados de libertad, ya que la matriz H está definida hasta un factor de escala y solo 8 de sus 9 elementos son independientes.** — _correcta_: Correcto: H es homogénea (H y λH representan la misma transformación), por lo que solo hay 8 parámetros libres, no 9.

> La homografía es la transformación proyectiva 2D que relaciona planos entre dos imágenes; es fundamental entender sus grados de libertad, los requisitos mínimos de estimación (DLT + RANSAC) y sus limitaciones frente a escenas no planas, así como su uso práctico en rectificación y mosaicos.
>
> Repasar: `Homografía / DLT / RANSAC / rectificación planar`

### ⚠️ Pregunta 2 — Visión estéreo: emparejamiento y reconstrucción tridimensional de escenas

Sobre la visión estéreo con un par de cámaras calibradas (emparejamiento de puntos correspondientes y reconstrucción 3D por triangulación), ¿cuáles de las siguientes afirmaciones son correctas?

- [x] **Algoritmos como Programación Dinámica o Semi-Global Matching (SGM) minimizan una función de coste que combina similitud fotométrica local con un término de suavidad o regularización entre píxeles vecinos.** — _correcta_: Correcto: estos métodos globales/semi-globales incorporan restricciones de suavidad para penalizar cambios bruscos de disparidad entre píxeles adyacentes, mejorando la robustez frente al matching puramente local.
- [ ] **La rectificación estéreo transforma las imágenes para que las líneas epipolares queden alineadas horizontalmente, reduciendo la búsqueda de correspondencias a una búsqueda 1D a lo largo de las filas.** — _correcta_: Correcto: tras la rectificación, las líneas epipolares coinciden con las filas de la imagen, lo que simplifica enormemente el algoritmo de emparejamiento (búsqueda solo en la misma fila).
- [ ] **Aumentar la línea base (baseline) entre las dos cámaras siempre mejora la precisión de la reconstrucción 3D sin ningún efecto negativo sobre el emparejamiento de puntos.** — _incorrecta_: Incorrecto: aunque una línea base mayor mejora la precisión teórica en profundidad, también reduce el solapamiento entre imágenes, aumenta las oclusiones y dificulta el emparejamiento por los mayores cambios de perspectiva.
- [ ] **El problema de correspondencia estéreo es trivial en regiones con textura homogénea o repetitiva, ya que medidas como SAD o SSD convergen siempre a un único mínimo global.** — _incorrecta_: Incorrecto: precisamente las regiones homogéneas o con patrones repetitivos son las más problemáticas para el emparejamiento, porque generan múltiples mínimos locales ambiguos (problema de las 'áreas sin textura').
- [ ] **La profundidad Z de un punto es inversamente proporcional a la disparidad d, siguiendo Z = f·B/d (f: distancia focal, B: línea base), por lo que puntos más lejanos producen disparidades menores.** — _correcta_: Correcto: es la relación fundamental de la triangulación estéreo tras rectificación; a mayor distancia, menor disparidad entre las proyecciones en ambas imágenes.

> La visión estéreo combina rectificación epipolar, la relación geométrica disparidad-profundidad y algoritmos de emparejamiento (locales y globales/semi-globales) para reconstruir la geometría 3D de la escena; también hay que entender las limitaciones prácticas del matching en zonas ambiguas y el compromiso de la línea base.
>
> Repasar: `Rectificación estéreo / disparidad / SGM`

### ⚠️ Pregunta 3 — Tracking multiobjeto: asociación de detecciones entre fotogramas (SORT/DeepSORT)

En un sistema de seguimiento multiobjeto (MOT) tipo SORT/DeepSORT, para asociar las detecciones del fotograma actual con las trayectorias existentes, ¿cuáles de las siguientes afirmaciones son correctas?

- [x] **La métrica IoU es invariante a la velocidad del objeto, por lo que basta con comparar las posiciones brutas del fotograma anterior sin ningún paso de predicción, en cualquier escenario.** — _incorrecta_: Incorrecto: sin predicción de movimiento, objetos rápidos u oclusiones breves provocan solapamientos bajos o nulos entre cajas consecutivas, degradando la asociación por IoU; por eso se combina con predicción de estado (Kalman).
- [x] **El algoritmo húngaro resuelve el problema de asignación óptima minimizando el coste total (por ejemplo, basado en 1-IoU o distancia de apariencia) entre detecciones y trayectorias predichas.** — _correcta_: Correcto: el algoritmo húngaro (Kuhn-Munkres) encuentra la asignación biunívoca de coste mínimo en la matriz detección-trayectoria en tiempo polinómico, siendo el método estándar en SORT/DeepSORT.
- [x] **El filtro de Kalman se emplea para predecir la posición esperada de cada trayectoria en el fotograma actual antes de calcular la matriz de costes con las nuevas detecciones.** — _correcta_: Correcto: SORT usa un filtro de Kalman con modelo de velocidad constante para predecir el estado (posición/tamaño) de cada track y así compararlo con las detecciones observadas.
- [ ] **Cualquier detección que no se asigne a una trayectoria existente debe descartarse inmediatamente, ya que nunca puede dar lugar a un nuevo objeto seguido.** — _incorrecta_: Incorrecto: las detecciones no asignadas suelen iniciar una nueva trayectoria tentativa, que se confirma si persiste en fotogramas sucesivos; descartarlas impediría detectar objetos que entran en la escena.
- [x] **DeepSORT mejora a SORT incorporando un descriptor de apariencia (embedding de re-identificación) que se combina con el coste de movimiento, reduciendo los cambios de identidad durante oclusiones.** — _correcta_: Correcto: DeepSORT añade una rama de re-identificación (distancia coseno sobre embeddings de apariencia) junto a la distancia de Mahalanobis del filtro de Kalman, mejorando la robustez frente a oclusiones respecto a SORT.

> La asociación de detecciones entre fotogramas en tracking multiobjeto combina predicción de movimiento (filtro de Kalman), una métrica de coste (IoU y/o apariencia) y un algoritmo de asignación óptima (húngaro) para mantener identidades consistentes a lo largo del tiempo, gestionando además la creación y eliminación de trayectorias.
>
> Repasar: `SORT / DeepSORT, algoritmo húngaro, filtro de Kalman`

### ❌ Pregunta 4 — Sobel, Laplaciano y detección automática de bordes significativos

Un ingeniero necesita detectar bordes 'significativos' de forma automática, evitando bordes gruesos, discontinuos o espurios por ruido, algo que Sobel y Laplaciano por separado no resuelven bien. ¿Cuál de las siguientes afirmaciones describe correctamente la relación entre estos operadores y el algoritmo adecuado para este objetivo?

- [x] **Aumentar el umbral bajo de histéresis en Canny, sin modificar el umbral alto, tiende a producir bordes más largos y continuos porque se conectan más píxeles débiles a los bordes fuertes.** — _incorrecta_: Incorrecto: subir el umbral bajo hace más estricto el criterio de aceptación de píxeles débiles, por lo que se conectan menos píxeles y los bordes tienden a fragmentarse más, no al revés.
- [ ] **El operador Laplaciano de Gaussiano (LoG) es matemáticamente idéntico a Sobel, solo que aplicado tras un suavizado gaussiano, por lo que ambos producen exactamente los mismos bordes.** — _incorrecta_: Incorrecto: Sobel aproxima la primera derivada (gradiente) y detecta bordes por máximos de magnitud, mientras que el Laplaciano es un operador de segunda derivada que detecta bordes por cruces por cero; no son equivalentes.
- [ ] **El operador Sobel por sí solo, al ser un filtro de segunda derivada, ya incluye supresión de no máximos y por eso genera bordes de un solo píxel de ancho.** — _incorrecta_: Incorrecto: Sobel es un operador de primera derivada (gradiente) y no incluye ningún mecanismo de adelgazamiento; produce bordes gruesos si no se combina con NMS.
- [x] **El algoritmo de Canny calcula el gradiente (magnitud y dirección, típicamente vía Sobel tras suavizado gaussiano), aplica supresión de no máximos y umbralización por histéresis con dos umbrales, de modo que los píxeles con magnitud intermedia solo se consideran borde si están conectados a un píxel por encima del umbral alto.** — _correcta_: Correcto: esta es la descripción estándar del detector de Canny, que combina el gradiente tipo Sobel con adelgazamiento (NMS) y conectividad por histéresis para obtener bordes finos y continuos.
- [ ] **Canny elige automáticamente ambos umbrales de histéresis a partir del histograma del gradiente en todos los casos, por lo que nunca requiere ajuste manual de parámetros.** — _incorrecta_: Incorrecto: en su formulación clásica Canny requiere fijar manualmente el umbral alto y bajo (o su razón); aunque existen variantes que estiman umbrales automáticamente (p. ej. con Otsu), no es una propiedad garantizada 'en todos los casos'.

> Sobel y Laplaciano son operadores de derivada básicos (primera y segunda derivada respectivamente) sensibles al ruido y sin mecanismo propio de selección de bordes 'significativos'. Canny resuelve esto combinando gradiente, supresión de no máximos y umbralización por histéresis con dos umbrales.
>
> Repasar: `Detector de Canny / supresión de no máximos / histéresis`

### ❌ Pregunta 5 — Convoluciones profundas: aprendizaje automático de características visuales

Respecto al aprendizaje automático de características visuales mediante redes convolucionales profundas (CNN), en contraste con descriptores diseñados a mano como SIFT o HOG, ¿cuál de las siguientes afirmaciones es correcta?

- [x] **Como las CNN aprenden las características automáticamente vía retropropagación, no necesitan grandes volúmenes de datos etiquetados y siempre superan a SIFT, incluso en dominios con muy pocas muestras.** — _incorrecta_: Incorrecto: precisamente lo contrario suele ser cierto; las CNN entrenadas desde cero típicamente requieren grandes conjuntos de datos etiquetados, y en regímenes de muy pocos datos los descriptores hechos a mano como SIFT pueden ser más robustos o competitivos.
- [ ] **Los pesos de los kernels convolucionales deben inicializarse manualmente imitando filtros de Gabor, igual que en SIFT, para que la red converja durante el entrenamiento.** — _incorrecta_: Incorrecto: los kernels de una CNN se inicializan habitualmente con esquemas aleatorios (p. ej. He o Xavier) y se aprenden por completo mediante retropropagación; no requieren imitar filtros predefinidos como los de Gabor usados en SIFT.
- [ ] **El uso de capas de pooling (max o average) es imprescindible en cualquier arquitectura CNN moderna, ya que sin ellas no es posible retropropagar el gradiente a través de las capas convolucionales.** — _incorrecta_: Incorrecto: el pooling es opcional; muchas arquitecturas modernas (p. ej. con convoluciones con stride) prescinden de él, y el gradiente se retropropaga correctamente a través de capas puramente convolucionales sin necesidad de pooling.
- [x] **Las primeras capas convolucionales de una CNN entrenada para clasificación tienden a aprender filtros similares a detectores de bordes y gradientes de color, mientras que las capas más profundas capturan patrones semánticos progresivamente más abstractos y específicos de la tarea.** — _correcta_: Correcto: es un resultado ampliamente observado (visualización de filtros y mapas de activación) que la jerarquía convolucional aprende representaciones de bajo nivel (bordes, texturas) en capas iniciales y conceptos de alto nivel (partes de objetos, clases) en capas profundas, sin diseño manual.
- [ ] **El campo receptivo de una neurona en una capa profunda depende únicamente del tamaño del kernel de esa capa concreta, no de las capas anteriores.** — _incorrecta_: Incorrecto: el campo receptivo se acumula a través de todas las capas previas (tamaño de kernel, stride y dilatación de cada una), por lo que una neurona profunda puede tener un campo receptivo mucho mayor que el kernel local de su propia capa.

> A diferencia de SIFT/HOG, donde los filtros y reglas de extracción se diseñan manualmente, en una CNN los pesos de los kernels se aprenden end-to-end mediante descenso de gradiente y retropropagación, dando lugar de forma automática a una jerarquía de características que va de bordes simples a conceptos semánticos complejos.
>
> Repasar: `Aprendizaje de representaciones (representation learning), retropropagación, campo receptivo`
