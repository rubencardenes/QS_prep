# Resultado del test — Computer Vision (teoría y algoritmos)

- Fecha: 2026-08-06 10:35
- Nivel: media
- Puntuación: **65%** (3.25/5 puntos)
- Preguntas perfectas: 3/5

## Revisión pregunta a pregunta

### ❌ Pregunta 1 — Iluminación Lambertiana: modelo de reflectancia y sombras

Respecto al modelo de reflectancia Lambertiana (superficie mate ideal) usado para modelar la intensidad de imagen en función de la iluminación, ¿cuáles de las siguientes afirmaciones son correctas?

- [ ] **Una superficie Lambertiana refleja la luz con la misma radiancia en todas las direcciones de observación, por lo que su brillo aparente no depende de la posición de la cámara.** — _correcta_: Correcto: es la propiedad definitoria del modelo Lambertiano (reflectancia difusa perfecta); el brillo percibido solo depende de la geometría entre la normal y la fuente de luz, no del punto de vista.
- [ ] **Bajo iluminación Lambertiana con una única fuente de luz distante, el problema de 'shape from shading' busca recuperar la normal de la superficie en cada píxel a partir de su intensidad observada.** — _correcta_: Correcto: shape-from-shading explota precisamente la relación I ∝ N·L del modelo Lambertiano para inferir la orientación de la superficie (y de ahí su forma) a partir del patrón de sombreado en la imagen.
- [ ] **Las sombras propias (self-shadowing), donde N·L es negativo, se modelan directamente con valores de intensidad negativos en la ecuación de reflectancia.** — _incorrecta_: Falso: cuando N·L < 0 la superficie no recibe luz directa desde esa fuente, y la intensidad se trunca a cero (o se recorta con max(0, N·L)); no se generan intensidades negativas.
- [x] **El modelo Lambertiano puede reproducir con precisión los reflejos especulares (brillos puntuales) que aparecen en superficies metálicas o pulidas.** — _incorrecta_: Falso: el modelo Lambertiano solo captura reflexión difusa; los reflejos especulares requieren términos adicionales como en el modelo de Phong o Blinn-Phong, que dependen del ángulo de visión.
- [x] **Según el modelo Lambertiano, el brillo observado en un punto de la superficie es proporcional al coseno del ángulo entre la normal de la superficie y la dirección de la fuente de luz.** — _correcta_: Correcto: la ley del coseno de Lambert establece que la radiancia reflejada es proporcional a N·L (producto escalar entre la normal N y la dirección hacia la luz L), asumiendo reflectancia uniforme en todas direcciones.

> El modelo Lambertiano describe superficies mate ideales cuya intensidad reflejada depende únicamente del ángulo entre la normal de la superficie y la dirección de la luz (I ∝ N·L), siendo independiente del ángulo de observación; es la base de técnicas clásicas como shape-from-shading, pero no explica fenómenos especulares.
>
> Repasar: `Modelo de reflectancia Lambertiana / ley del coseno`

### ⚠️ Pregunta 2 — Descriptor HOG: orientaciones y normalización de bloques

Sobre el descriptor HOG (Histogram of Oriented Gradients), usado clásicamente para detección de peatones, ¿cuáles de las siguientes afirmaciones son correctas?

- [x] **La normalización por bloques (agrupando varias celdas) es imprescindible porque reduce la sensibilidad del descriptor a cambios de iluminación y contraste local.** — _correcta_: Correcto: tras concatenar los histogramas de celdas en un bloque, se normaliza (p. ej. L2-norm) para atenuar variaciones locales de iluminación y sombreado, mejorando la invarianza fotométrica.
- [ ] **Los bloques se solapan entre sí, de modo que una misma celda puede contribuir a la normalización de varios bloques distintos.** — _correcta_: Correcto: en la formulación original de Dalal y Triggs los bloques se desplazan con solape (stride menor que el tamaño del bloque), y cada celda participa en varios bloques, lo que mejora la robustez del descriptor final.
- [ ] **HOG es invariante a la rotación de la imagen porque el histograma de orientaciones absorbe cualquier giro del objeto.** — _incorrecta_: Falso: HOG no es invariante a rotación; las orientaciones se calculan respecto a un eje de referencia fijo de la imagen, por lo que rotar el objeto cambia sustancialmente el descriptor.
- [ ] **HOG divide la imagen en celdas pequeñas y, para cada una, calcula un histograma de orientaciones del gradiente ponderado por su magnitud.** — _correcta_: Correcto: en cada celda (típicamente 8x8 px) se acumula un histograma de orientaciones del gradiente, donde cada píxel vota con un peso proporcional a la magnitud del gradiente.
- [ ] **El histograma de cada celda se calcula típicamente sobre el rango de 0° a 180° (gradiente no dirigido) en lugar de 0° a 360°.** — _correcta_: Correcto: la variante 'unsigned' habitual en HOG para detección de peatones usa 0-180°, tratando gradientes opuestos como equivalentes, lo que suele dar mejor rendimiento empírico que usar 0-360°.

> HOG (Dalal & Triggs, 2005) captura la distribución local de orientaciones del gradiente en celdas, y normaliza por bloques solapados para lograr robustez frente a cambios de iluminación y contraste, aunque no es invariante a rotación ni a escala por sí mismo.
>
> Repasar: `HOG - Histogram of Oriented Gradients`

### ✅ Pregunta 3 — Detección de blobs con diferencia de Gaussianas (DoG) y espacio de escala

Sobre la detección de blobs mediante la diferencia de Gaussianas (DoG) como aproximación al Laplaciano de Gaussiano normalizado en escala, empleada por ejemplo en la etapa de detección de puntos clave de SIFT, ¿cuáles de las siguientes afirmaciones son correctas?

- [x] **Los extremos locales se buscan tanto en el plano espacial (x,y) como en la dimensión de escala σ, comparando cada punto con sus 26 vecinos (8 en su misma escala y 9 en cada una de las dos escalas adyacentes).** — _correcta_: Correcto: es el procedimiento estándar de SIFT para localizar extremos estables simultáneamente en posición y escala dentro de la pirámide DoG.
- [x] **La DoG se obtiene restando dos imágenes suavizadas con Gaussianas de distinto sigma, D(x,y,σ) = G(x,y,kσ)*I − G(x,y,σ)*I, y aproxima al LoG normalizado en escala (σ²∇²G) de forma computacionalmente más barata.** — _correcta_: Correcto: Lowe demostró que la diferencia de dos Gaussianas consecutivas en la pirámide de escala aproxima bien al LoG normalizado, evitando calcular explícitamente el laplaciano en cada escala.
- [ ] **Cuanto mayor es el valor de sigma (σ) usado en el suavizado Gaussiano, más se resaltan los blobs pequeños y de alta frecuencia, mientras que un σ pequeño resalta estructuras grandes de baja frecuencia.** — _incorrecta_: Incorrecto: es al contrario; un σ pequeño responde mejor a blobs pequeños/alta frecuencia, y un σ grande (más suavizado) responde a blobs de mayor tamaño y baja frecuencia, ya que el filtro actúa como paso-banda centrado en una escala proporcional a σ.
- [x] **Tras localizar los extremos en el espacio de escala DoG, SIFT aplica un criterio basado en la matriz Hessiana 2x2 para descartar puntos situados sobre bordes (mal localizados por baja curvatura en una dirección), de forma análoga al criterio empleado en el detector de Harris.** — _correcta_: Correcto: SIFT usa la razón entre autovalores de la Hessiana (equivalente en espíritu a la matriz de segundo momento de Harris) para rechazar puntos con respuesta fuerte en una sola dirección, típicos de bordes.
- [ ] **La pirámide de DoG requiere recalcular la convolución Gaussiana desde la imagen original para cada escala de forma independiente, sin poder reutilizar los resultados de convoluciones de escalas anteriores dentro de la misma octava.** — _incorrecta_: Incorrecto: en la práctica se aplica suavizado progresivo (cada imagen suavizada se obtiene convolucionando la anterior con un incremento de sigma), lo que evita recalcular desde la imagen original en cada escala y hace el proceso más eficiente.

> La DoG es una aproximación eficiente al Laplaciano de Gaussiano normalizado, usada para detectar blobs de forma multiescala: los extremos en el espacio (x,y,σ) señalan la presencia y el tamaño característico de una estructura tipo blob, y se filtran posteriormente los puntos de baja curvatura en una dirección (típicos de bordes) mediante un criterio tipo Hessiano/Harris.
>
> Repasar: `SIFT — pirámide de escala, Diferencia de Gaussianas (DoG), criterio de la Hessiana para rechazo de bordes`

### ✅ Pregunta 4 — Binarización adaptativa como alternativa a Otsu

Un ingeniero debe binarizar una imagen de un documento escaneado con iluminación desigual (sombra marcada en una esquina), donde el método de Otsu —que calcula un único umbral global a partir del histograma— produce resultados deficientes. Respecto al uso de la binarización adaptativa (p. ej. `cv2.adaptiveThreshold`) como alternativa, ¿cuál de las siguientes afirmaciones es correcta?

- [ ] **El tamaño de la ventana (`blockSize`) en `cv2.adaptiveThreshold` no afecta al resultado siempre que sea un número impar, por lo que puede fijarse de forma arbitraria sin considerar la escala de las estructuras a segmentar.** — _incorrecta_: Incorrecto: blockSize sí es crítico; debe ser mayor que las estructuras de interés (trazos de texto) pero lo bastante pequeño para capturar variaciones locales de iluminación, y un valor mal elegido degrada notablemente el resultado.
- [x] **Calcula un umbral local para cada píxel a partir de estadísticas de una ventana vecina (media aritmética o media ponderada gaussiana), lo que le permite adaptarse a variaciones locales de iluminación, a diferencia de Otsu, que asume un histograma global bimodal.** — _correcta_: Correcto: es precisamente la razón de ser del método; en lugar de un umbral global, cada píxel se compara con el promedio (simple o gaussiano) de su vecindario, lo que compensa gradientes de iluminación locales que rompen la hipótesis bimodal global de Otsu.
- [ ] **Sustituye por completo la necesidad de cualquier preprocesado, por lo que aplicar un suavizado previo (p. ej. Gaussiano) nunca mejora sus resultados.** — _incorrecta_: Incorrecto: un suavizado previo suele reducir ruido de alta frecuencia que de otro modo generaría falsos positivos/negativos en cada ventana local, mejorando el resultado en la práctica.
- [ ] **`cv2.adaptiveThreshold` calcula internamente un único umbral óptimo global minimizando la varianza intra-clase, igual que Otsu, pero lo aplica de forma iterativa por bloques.** — _incorrecta_: Incorrecto: esa descripción corresponde al procedimiento de Otsu (minimización de varianza intra-clase sobre el histograma), no al de la binarización adaptativa, que usa medias locales y no optimiza varianza de clases.
- [ ] **Al igual que Otsu, requiere que el histograma global de la imagen sea bimodal para funcionar correctamente, por lo que no aporta ninguna ventaja real ante iluminación irregular.** — _incorrecta_: Incorrecto: la binarización adaptativa no depende del histograma global en absoluto, sino de estadísticas locales por ventana; esa es justamente la ventaja que la hace útil cuando el histograma global deja de ser bimodal por la iluminación desigual.

> Otsu asume un histograma global bimodal (fondo/objeto) y falla cuando la iluminación varía espacialmente dentro de la imagen. La binarización adaptativa resuelve esto calculando, para cada píxel, un umbral derivado de las estadísticas de su vecindario local, adaptándose así a gradientes de iluminación que un umbral único no puede manejar.
>
> Repasar: `cv2.adaptiveThreshold (ADAPTIVE_THRESH_MEAN_C / ADAPTIVE_THRESH_GAUSSIAN_C) vs umbralización de Otsu`

### ✅ Pregunta 5 — Interpolación, kernels y aliasing en submuestreo

Sobre la interpolación en el redimensionado de imágenes (en particular al reducir el tamaño, *downsampling*) y el fenómeno de aliasing, ¿cuáles de las siguientes afirmaciones son correctas?

- [x] **Al reducir el tamaño de una imagen por un factor grande es necesario aplicar antes un filtro paso-bajo (p. ej. Gaussiano) para evitar aliasing, ya que la frecuencia de muestreo resultante puede violar el criterio de Nyquist.** — _correcta_: Correcto: si no se limita el contenido en alta frecuencia antes de submuestrear, las frecuencias por encima de la nueva frecuencia de Nyquist se pliegan (aliasing), generando patrones moiré o artefactos.
- [ ] **El aliasing solo puede ocurrir al aumentar el tamaño de la imagen (upsampling), nunca al reducirla, porque aumentar el número de píxeles nunca elimina información.** — _incorrecta_: Incorrecto: es justo al revés; el aliasing es un problema propio del submuestreo (downsampling), donde se pierde información de alta frecuencia si no se filtra antes.
- [x] **`cv2.resize` con `INTER_AREA` es adecuado para downsampling porque promedia los píxeles del área correspondiente, reduciendo el aliasing frente a `INTER_LINEAR` en factores de reducción grandes.** — _correcta_: Correcto: INTER_AREA realiza un promediado de área (equivalente a un filtrado paso-bajo local) antes de resamplear, lo que la OpenCV recomienda explícitamente para reducir tamaño de imagen.
- [x] **La interpolación bicúbica usa un kernel de soporte mayor que la bilineal, lo que puede producir resultados más suaves pero con posible overshoot (ringing) cerca de bordes de alto contraste.** — _correcta_: Correcto: el kernel cúbico (soporte de 4x4 píxeles frente a 2x2 del bilineal) puede generar overshoot/ringing en bordes marcados debido a sus lóbulos negativos, un efecto conocido y documentado.
- [ ] **La interpolación por vecino más próximo (nearest neighbor) actúa como filtro paso-bajo ideal y por tanto previene el aliasing al reducir la imagen.** — _incorrecta_: Incorrecto: nearest neighbor simplemente toma muestras sin promediar el entorno, por lo que no atenúa altas frecuencias y es de los métodos más propensos a aliasing y artefactos de bloque.

> El teorema de muestreo de Nyquist-Shannon exige limitar el contenido en frecuencia de una señal antes de reducir su tasa de muestreo; en imágenes esto se traduce en aplicar un filtro paso-bajo (o un método de interpolación que integre ese promediado, como INTER_AREA) antes de un downsampling agresivo, mientras que métodos como nearest neighbor no ofrecen esa protección.
>
> Repasar: `Aliasing, criterio de Nyquist, cv2.resize (INTER_AREA vs INTER_NEAREST vs INTER_CUBIC)`
