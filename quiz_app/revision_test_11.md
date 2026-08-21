# Resultado del test — Computer Vision (teoría y algoritmos)

- Fecha: 2026-08-05 13:37
- Nivel: media
- Puntuación: **100%** (5.00/5 puntos)
- Preguntas perfectas: 5/5

## Revisión pregunta a pregunta

### ✅ Pregunta 1 — Modelado de escenas dinámicas: sustracción de fondo y detección de movimiento

Sobre el modelado de escenas dinámicas mediante sustracción de fondo (background subtraction) para la detección de movimiento en secuencias de vídeo, ¿cuál de las siguientes afirmaciones es correcta?

- [ ] **La sustracción de fondo mediante un promedio acumulado de los primeros N fotogramas produce un modelo de fondo válido de forma permanente, sin necesidad de actualizarlo posteriormente, incluso ante cambios de iluminación o la incorporación de nuevos objetos estáticos al fondo.** — _incorrecta_: Incorrecto: un modelo de fondo estático se degrada rápidamente ante cambios de iluminación, sombras cambiantes u objetos que pasan a formar parte del fondo (p. ej. un coche aparcado); requiere actualización continua para seguir siendo útil.
- [x] **Los modelos de mezcla de gaussianas (MOG/MOG2) representan cada píxel mediante una combinación de varias distribuciones gaussianas actualizadas de forma adaptativa, lo que permite modelar fondos con variaciones periódicas (hojas moviéndose, parpadeo de luces) y marcar como primer plano los píxeles que no se ajustan bien a ninguna componente del modelo.** — _correcta_: Correcto: es la base de algoritmos como MOG2 (Zivkovic), ampliamente usados en OpenCV, donde cada píxel mantiene K distribuciones gaussianas ponderadas que se actualizan con cada fotograma para adaptarse a fondos dinámicos.
- [ ] **La sombra proyectada por un objeto en movimiento nunca se clasifica erróneamente como primer plano, ya que los algoritmos de sustracción de fondo distinguen intrínsecamente entre cambios de iluminación y cambios estructurales de la escena.** — _incorrecta_: Incorrecto: las sombras son una fuente clásica de falsos positivos en sustracción de fondo; distinguirlas requiere técnicas específicas de detección de sombras (p. ej. análisis de crominancia en HSV), no se resuelve de forma intrínseca por el modelo básico.
- [ ] **El problema del camuflaje (píxeles de un objeto en movimiento con color similar al del fondo) se resuelve automáticamente en cualquier método basado en diferencia de intensidad por umbral, sin necesitar información adicional como gradientes, textura o color en otros espacios.** — _incorrecta_: Incorrecto: el camuflaje sigue siendo una limitación conocida de la sustracción de fondo basada en intensidad; mitigarlo suele requerir señales adicionales (gradiente, textura, espacios de color como HSV) y no se resuelve 'automáticamente'.

> La sustracción de fondo busca separar los píxeles de primer plano (movimiento/objetos) de un modelo de fondo que debe adaptarse a lo largo del tiempo. Los métodos adaptativos como MOG2 o KNN mantienen modelos estadísticos por píxel que se actualizan continuamente, pero persisten retos conocidos como sombras, camuflaje, cambios bruscos de iluminación y objetos que se integran o abandonan el fondo ('ghosting').
>
> Repasar: `Sustracción de fondo, mezcla de gaussianas (MOG2), detección de sombras, camuflaje en detección de movimiento`

### ✅ Pregunta 2 — Análisis de texturas: LBP, Gabor y matrices de co-ocurrencia

Sobre el análisis de texturas mediante descriptores LBP (Local Binary Patterns), filtros de Gabor y matrices de co-ocurrencia de niveles de gris (GLCM), ¿cuáles de las siguientes afirmaciones son correctas?

- [ ] **El LBP uniforme descarta información relevante de bordes y esquinas, conservando únicamente los patrones correspondientes a regiones planas homogéneas.** — _incorrecta_: Incorrecto: los patrones uniformes (con a lo sumo dos transiciones bit a bit) son precisamente los que corresponden a estructuras como bordes, esquinas y puntos, no a regiones planas; se agrupan por ser los más frecuentes y discriminativos en texturas naturales.
- [ ] **Los filtros de Gabor operan exclusivamente en el dominio espacial y no guardan relación con el análisis en frecuencia, a diferencia de la Transformada de Fourier.** — _incorrecta_: Incorrecto: los filtros de Gabor son duales espacio-frecuencia; su respuesta en frecuencia es una gaussiana desplazada, por lo que están directamente emparentados con el análisis de Fourier localizado.
- [ ] **La matriz de co-ocurrencia (GLCM) solo puede calcularse para un desplazamiento fijo de un píxel y ángulo 0°, por lo que no permite capturar textura a distintas escalas ni orientaciones.** — _incorrecta_: Incorrecto: la GLCM se define para cualquier distancia y ángulo elegidos (p. ej. 1, 2, 3 píxeles y 0°, 45°, 90°, 135°), lo que precisamente permite analizar la textura en múltiples orientaciones y escalas.
- [x] **Los filtros de Gabor son sensibles a una orientación y frecuencia espacial concretas, por lo que un banco de filtros con distintas orientaciones y escalas permite capturar texturas direccionales y periódicas.** — _correcta_: Correcto: un filtro de Gabor es una sinusoide modulada por una gaussiana, ajustable en orientación y frecuencia, lo que lo hace idóneo para analizar texturas con estructura direccional a distintas escalas.
- [x] **El descriptor LBP codifica cada píxel comparando su intensidad con la de sus vecinos en un vecindario circular, generando un patrón binario que se transforma en un valor decimal; por construcción es invariante a cambios monótonos de iluminación.** — _correcta_: Correcto: al basarse solo en el signo de la diferencia entre el píxel central y sus vecinos, una transformación monótona de la escala de grises (p. ej. sumar una constante o multiplicar por un factor positivo) no altera el patrón resultante.

> LBP, Gabor y GLCM son tres enfoques clásicos de caracterización de textura con propiedades distintas: LBP es un descriptor local basado en comparaciones de intensidad e invariante a cambios monótonos de brillo; Gabor analiza contenido espacio-frecuencial orientado y escalado; GLCM cuantifica relaciones estadísticas de segundo orden entre pares de píxeles (características de Haralick como contraste, homogeneidad, energía y entropía), siendo configurable en distancia y ángulo.
>
> Repasar: `Local Binary Patterns, filtros de Gabor, matriz de co-ocurrencia (GLCM), características de Haralick`

### ✅ Pregunta 3 — Operaciones morfológicas: erosión, dilatación, apertura y cierre

Sobre las operaciones morfológicas básicas (erosión, dilatación, apertura y cierre) aplicadas a máscaras binarias con un elemento estructurante fijo, ¿cuáles de las siguientes afirmaciones son correctas?

- [ ] **El tamaño y la forma del elemento estructurante no influyen en el resultado final; solo el número de iteraciones de la operación determina el efecto sobre la máscara.** — _incorrecta_: Incorrecto: el elemento estructurante (su tamaño y forma, p. ej. disco, cruz o rectángulo) determina qué estructuras se eliminan o preservan; cambiar su forma altera el resultado incluso con el mismo número de iteraciones.
- [x] **El cierre (dilatación seguida de erosión) rellena pequeños huecos y conecta componentes próximos, tendiendo a preservar o aumentar ligeramente el tamaño aparente de los objetos.** — _correcta_: Correcto: la dilatación inicial cierra huecos y une regiones cercanas, y la erosión posterior recupera aproximadamente los bordes originales, pero los huecos rellenados no se recuperan.
- [x] **Tanto la apertura como el cierre son operaciones idempotentes: aplicar la misma operación por segunda vez sobre su propio resultado no produce cambios adicionales.** — _correcta_: Correcto: es una propiedad matemática conocida de la morfología matemática, opening(opening(A)) = opening(A) y lo mismo para closing, a diferencia de erosión y dilatación simples que sí siguen cambiando con más iteraciones.
- [x] **La apertura (erosión seguida de dilatación con el mismo elemento estructurante) elimina pequeños objetos y protuberancias finas ('ruido sal'), suavizando contornos sin alterar significativamente el tamaño de los objetos grandes.** — _correcta_: Correcto: la erosión inicial borra estructuras más pequeñas que el elemento estructurante, y la dilatación posterior recupera aproximadamente el tamaño original de los objetos que sobrevivieron.
- [ ] **La erosión de una máscara binaria se define como una operación de OR lógico entre el elemento estructurante y cada vecindad, lo que provoca que los objetos se expandan.** — _incorrecta_: Incorrecto: la erosión se basa en un AND lógico (mínimo local): un píxel sobrevive solo si todo el elemento estructurante encaja dentro del objeto, por lo que los objetos se contraen, no se expanden.

> La erosión y la dilatación son operaciones morfológicas duales basadas en mínimo/máximo local respecto a un elemento estructurante; la apertura y el cierre son combinaciones de ambas (erosión+dilatación y dilatación+erosión respectivamente) que resultan idempotentes y se usan típicamente para limpiar ruido o rellenar huecos en máscaras binarias, como en `cv2.morphologyEx` con `MORPH_OPEN`/`MORPH_CLOSE`.
>
> Repasar: `Morfología matemática: erosión, dilatación, apertura, cierre (cv2.morphologyEx)`

### ✅ Pregunta 4 — Análisis de contornos: extracción, descriptores de forma y propiedades

Sobre el análisis de contornos extraídos de una máscara binaria (por ejemplo con `cv2.findContours`) y el cálculo de descriptores de forma (momentos de Hu, circularidad, convex hull, jerarquía), ¿cuáles de las siguientes afirmaciones son correctas?

- [x] **La jerarquía devuelta por `cv2.findContours` (parámetro hierarchy) permite distinguir contornos externos de contornos internos (agujeros), información necesaria para calcular correctamente el área neta de un objeto con huecos.** — _correcta_: Correcto: la jerarquía codifica relaciones padre-hijo entre contornos (p. ej. con RETR_CCOMP o RETR_TREE), permitiendo identificar qué contornos son agujeros internos que deben restarse del área del contorno externo.
- [x] **La circularidad de un contorno, definida habitualmente como 4π·Área/Perímetro², vale 1 para un círculo perfecto y disminuye para formas alargadas o irregulares.** — _correcta_: Correcto: esta fórmula alcanza su máximo teórico (1) exactamente en el círculo, que minimiza el perímetro para un área dada, y toma valores menores para formas más alargadas o con bordes irregulares.
- [ ] **La envolvente convexa (convex hull) de un contorno siempre tiene un área menor o igual que la del contorno original, ya que elimina las partes cóncavas.** — _incorrecta_: Incorrecto: es al revés; el convex hull 'rellena' las concavidades del contorno, por lo que su área es siempre mayor o igual que la del contorno original, nunca menor.
- [ ] **El perímetro calculado con `cv2.arcLength` es independiente de si el contorno se aproxima previamente con `cv2.approxPolyDP`, dando siempre el mismo valor numérico.** — _incorrecta_: Incorrecto: `approxPolyDP` reduce el número de vértices del contorno sustituyendo tramos curvos por segmentos rectos más largos, lo que normalmente disminuye la longitud total medida por `arcLength` respecto al contorno original.
- [x] **Los momentos de Hu son un conjunto de 7 valores invariantes ante traslación, escala y rotación, derivados de los momentos centrales normalizados, y se usan habitualmente para comparar formas entre sí.** — _correcta_: Correcto: los 7 momentos de Hu se construyen combinando momentos centrales normalizados de forma que resultan invariantes a esas transformaciones, siendo una firma clásica de forma usada por ejemplo en `cv2.matchShapes`.

> El análisis de contornos combina la extracción de la frontera de regiones binarias con el cálculo de descriptores geométricos (área, perímetro, circularidad, convex hull, momentos de Hu) y topológicos (jerarquía de contornos internos/externos), que son la base de muchas tareas clásicas de reconocimiento de formas antes de recurrir a deep learning.
>
> Repasar: `cv2.findContours, cv2.moments (Hu moments), cv2.convexHull, jerarquía de contornos`

### ✅ Pregunta 5 — Transformada de Hough para detección de líneas y círculos

Sobre la transformada de Hough aplicada a la detección de líneas y círculos en imágenes de bordes binarizadas, ¿cuál de las siguientes afirmaciones es correcta?

- [x] **En la transformada de Hough para líneas, cada punto de borde (x,y) vota por todas las combinaciones (ρ,θ) de rectas que pasan por él, y las líneas detectadas corresponden a máximos locales de acumulación de votos en el espacio de parámetros (ρ,θ).** — _correcta_: Correcto: cada punto genera una curva sinusoidal en el espacio (ρ,θ); las intersecciones de muchas curvas en una celda del acumulador indican que muchos puntos son colineales, formando un máximo local.
- [ ] **Cuantos más puntos de borde ruidosos (outliers) haya en la imagen, menor será la robustez de Hough frente a un ajuste directo por mínimos cuadrados, ya que Hough es muy sensible a valores atípicos individuales.** — _incorrecta_: Incorrecto: es justo lo contrario; una de las ventajas principales de Hough es su robustez frente a outliers y bordes discontinuos, ya que cada punto atípico aislado rara vez genera un máximo significativo en el acumulador, mientras que mínimos cuadrados es muy sensible a ellos.
- [ ] **La detección de círculos mediante Hough solo necesita un espacio de parámetros 2D (a,b) para el centro, ya que el radio se determina automáticamente sin coste computacional adicional.** — _incorrecta_: Incorrecto: la Hough circular clásica requiere un espacio de parámetros 3D (a,b,r), lo que incrementa notablemente el coste computacional y de memoria respecto al caso de líneas.
- [ ] **La transformada de Hough generalizada solo puede aplicarse a formas descritas por ecuaciones analíticas simples, como rectas o círculos, y no a formas arbitrarias.** — _incorrecta_: Incorrecto: la transformada de Hough generalizada (GHT) fue diseñada precisamente para detectar formas arbitrarias sin ecuación analítica, usando una tabla-R construida a partir de una plantilla.
- [ ] **La parametrización (m,b) de y = mx + b se prefiere frente a (ρ,θ) porque maneja mejor las líneas verticales, evitando el problema de pendiente infinita.** — _incorrecta_: Incorrecto: es al revés. La parametrización (m,b) tiene el problema de que las líneas verticales requieren pendiente infinita, por eso se usa (ρ,θ), que representa cualquier línea con parámetros acotados.

> La transformada de Hough es un método de votación en el espacio de parámetros que permite detectar formas geométricas (líneas con (ρ,θ), círculos con (a,b,r), o formas arbitrarias con la versión generalizada) siendo robusta frente a ruido y oclusiones parciales, a costa de mayor coste computacional cuantos más parámetros tenga la forma buscada.
>
> Repasar: `cv2.HoughLines / cv2.HoughCircles, transformada de Hough generalizada`
