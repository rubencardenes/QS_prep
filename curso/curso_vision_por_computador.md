# Curso de refuerzo — Visión por Computador (teoría y algoritmos)

Basado en tus tests 03 (27%), 07 (68%) y 08 (27%, nivel senior). El test 11 lo hiciste perfecto (100%: sustracción de fondo, LBP/Gabor/GLCM, morfología matemática, contornos y transformada de Hough) — esos temas ya los dominas, no los repito aquí. Este curso se centra en los conceptos donde fallaste o fuiste parcial: geometría multivista (homografías, estéreo), tracking, detección de bordes clásica, aprendizaje de representaciones, óptica/distorsión, Viola-Jones, pirámides de escala, registro iterativo, normalización fotométrica en vídeo, segmentación por clustering, análisis en frecuencia y robustez adversarial.

Es material denso — varios de estos temas son de nivel senior. Tómate tu tiempo con los ejercicios, están pensados para consolidar la intuición, no solo la fórmula.

## Índice

1. Homografías: DLT y RANSAC
2. Visión estéreo: rectificación, disparidad y SGM
3. Tracking multiobjeto: SORT/DeepSORT
4. Detección de bordes: Sobel, Laplaciano y Canny
5. CNN vs. descriptores hechos a mano (SIFT/HOG)
6. Distorsión de lente: modelo de Brown-Conrady
7. Cascadas Haar y Viola-Jones
8. Pirámides Gaussianas/Laplacianas y espacio de escalas
9. Registro de imágenes: Lucas-Kanade, Gauss-Newton/LM, ICP
10. Normalización fotométrica en vídeo: CLAHE, homomórfico, flicker
11. Segmentación por clustering: K-means, mean shift, SLIC
12. Transformada de Fourier 2D y muestreo
13. Robustez adversarial de CNN

---

## 1. Homografías: DLT y RANSAC

### ¿Qué es una homografía?

Una homografía `H` es una matriz 3×3 que representa una transformación **proyectiva** entre dos planos en 2D (en coordenadas homogéneas). Es la transformación que relaciona dos fotografías del **mismo plano** tomado desde ángulos distintos, o dos vistas de una escena arbitraria cuando la cámara realiza una **rotación pura** alrededor de su propio centro óptico (sin traslación).

### El error conceptual más importante: cuándo NO aplica

Una homografía **solo** relaciona exactamente dos vistas cuando: (a) la escena fotografiada es plana, o (b) la cámara gira sobre su centro óptico sin desplazarse. Para una escena 3D con relieve real y una cámara que se traslada, aparece **paralaje** (objetos a distinta profundidad se desplazan de forma distinta entre las dos imágenes) — un efecto que una única homografía no puede modelar, sin importar que los centros ópticos de las cámaras sean distintos o no. Esa era la trampa del test: "centros ópticos distintos" no es la condición relevante; lo relevante es planaridad de la escena o rotación pura.

### Grados de libertad y estimación (DLT)

`H` está definida **hasta un factor de escala**: `H` y `λH` (para cualquier `λ ≠ 0`) representan la misma transformación. De los 9 elementos de la matriz, solo **8 son independientes**: 8 grados de libertad.

El algoritmo DLT (*Direct Linear Transform*) estima `H` a partir de correspondencias de puntos entre las dos imágenes. Cada correspondencia aporta 2 ecuaciones lineales; con 8 incógnitas necesitas mínimo **4 correspondencias de puntos no colineales** (en posición general) para resolver el sistema.

### RANSAC: por qué hace falta

Las correspondencias de puntos vienen típicamente de un emparejamiento de *features* (SIFT, ORB...), que siempre incluye errores — outliers, correspondencias falsas. RANSAC (*Random Sample Consensus*) estima `H` de forma robusta: prueba subconjuntos mínimos de correspondencias (4 puntos), calcula cuántas de las demás correspondencias son consistentes con la `H` resultante (inliers) dentro de un umbral de error, y se queda con el modelo que maximiza el número de inliers. No es que RANSAC sea "innecesario porque las homografías son exactas": es exactamente al revés, RANSAC es indispensable en la práctica porque los datos de entrada (correspondencias) nunca son perfectos.

### Aplicación práctica: rectificación

Rectificar una imagen mediante homografía significa aplicar la transformación inversa que "endereza" un plano fotografiado en ángulo (por ejemplo, un documento o una fachada) a una vista frontoparalela, como si la cámara hubiera estado perpendicular al plano.

### Ejercicio 1

Tienes dos fotos del mismo cartel publicitario plano, tomadas desde ángulos distintos con la misma cámara moviéndose lateralmente (no solo rotando). Detectas 30 correspondencias de puntos con SIFT, de las cuales 6 son erróneas. Describe el proceso completo, paso a paso, para obtener una homografía fiable que relacione ambas imágenes, y explica por qué el hecho de que la cámara se haya trasladado (no solo rotado) **no** invalida usar una homografía aquí, a diferencia del caso de una escena 3D con relieve.

---

## 2. Visión estéreo: rectificación, disparidad y SGM

### El pipeline completo

1. **Calibración**: se determinan los parámetros intrínsecos y extrínsecos de ambas cámaras.
2. **Rectificación estéreo**: se transforman ambas imágenes para que las líneas epipolares queden **alineadas horizontalmente**, coincidiendo con las filas de la imagen. Esto reduce la búsqueda de correspondencias de un problema 2D a una búsqueda **1D a lo largo de cada fila**.
3. **Emparejamiento (matching)**: para cada píxel de la imagen izquierda, se busca su correspondiente en la misma fila de la derecha, obteniendo la **disparidad** `d` (el desplazamiento horizontal en píxeles).
4. **Triangulación**: la profundidad se calcula como `Z = f·B/d`, donde `f` es la distancia focal y `B` la línea base (*baseline*) entre las cámaras. A mayor distancia, **menor** disparidad.

### Algoritmos de matching: local vs. global/semi-global

Los métodos puramente locales (SAD, SSD sobre ventanas) fallan en regiones con **textura homogénea o repetitiva**: ahí, la métrica de similitud tiene múltiples mínimos casi idénticos (ambigüedad), no un único mínimo global claro como podrías asumir ingenuamente. Programación Dinámica y **Semi-Global Matching (SGM)** resuelven esto añadiendo un término de **suavidad/regularización** que penaliza cambios bruscos de disparidad entre píxeles vecinos, combinándolo con el coste fotométrico local — mucho más robusto en zonas ambiguas.

### El trade-off de la línea base

Aumentar la línea base (`B`) mejora la precisión teórica en profundidad (mayor triangulación, menor error relativo), pero **no es una ventaja sin coste**: también reduce el solapamiento del campo de visión entre las dos cámaras, aumenta las oclusiones (partes visibles en una cámara y ocultas en la otra) y dificulta el emparejamiento por el mayor cambio de perspectiva entre ambas vistas. No es "cuanto más baseline, mejor sin más".

### Ejercicio 2

Diseñas un sistema estéreo para un dron que necesita detectar obstáculos cercanos (0.5–5 metros) en un pasillo con paredes lisas y poco texturizadas. Elige: (a) ¿línea base corta o larga?, (b) ¿matching local o SGM?, justificando ambas decisiones con lo aprendido sobre el trade-off de baseline y sobre regiones sin textura.

---

## 3. Tracking multiobjeto: SORT/DeepSORT

### El pipeline de asociación

En cada fotograma nuevo, hay que decidir qué detección corresponde a qué trayectoria (*track*) ya existente. El pipeline típico de SORT:

1. **Predicción**: un **filtro de Kalman** (con modelo de velocidad constante) predice dónde debería estar cada track en el fotograma actual, en base a su estado anterior.
2. **Coste**: se construye una matriz de costes entre detecciones nuevas y tracks predichos, típicamente basada en `1 - IoU` (Intersection over Union) entre cajas.
3. **Asignación óptima**: el **algoritmo húngaro** (Kuhn-Munkres) resuelve la asignación biunívoca de coste mínimo entre detecciones y tracks en tiempo polinómico — es el método estándar, no una heurística ad hoc.
4. **Gestión de tracks**: las detecciones no asignadas a ningún track existente **no se descartan** — inician una trayectoria tentativa, que se confirma si persiste en fotogramas sucesivos (así es como se detectan objetos nuevos entrando en escena). Los tracks sin detección asociada durante varios fotogramas se eliminan.

### Por qué hace falta predicción con Kalman, no solo IoU bruto

La IoU **no es invariante a la velocidad del objeto**: si comparas directamente las cajas del fotograma anterior contra las del actual sin ningún paso de predicción, objetos rápidos o con oclusiones breves producen solapamientos bajos o nulos entre cajas consecutivas, degradando la asociación. El filtro de Kalman anticipa el movimiento esperado, dando una posición predicha mucho más cercana a la real antes de calcular IoU.

### DeepSORT: qué añade sobre SORT

DeepSORT incorpora un **descriptor de apariencia** (embedding de re-identificación, entrenado para tareas tipo re-ID de personas/vehículos) que se combina con el coste de movimiento (distancia de Mahalanobis sobre el estado de Kalman) mediante distancia coseno. Esto reduce drásticamente los **cambios de identidad** (ID switches) durante oclusiones, porque incluso si la predicción geométrica es ambigua, la apariencia del objeto ayuda a mantener la identidad correcta.

### Ejercicio 3

Un peatón cruza detrás de una farola durante 4 fotogramas (oclusión total, sin detección) y luego reaparece 2 metros más adelante. Explica, paso a paso, qué mecanismos de SORT y de DeepSORT determinan si el sistema le asigna el mismo ID que tenía antes de la oclusión o le crea un ID nuevo, y en qué escenario cada uno tiene más probabilidad de fallar.

---

## 4. Detección de bordes: Sobel, Laplaciano y Canny

### Los operadores base y su diferencia fundamental

- **Sobel**: aproxima la **primera derivada** (gradiente) de la intensidad. Detecta bordes por **máximos de magnitud** del gradiente. No incluye ningún mecanismo de adelgazamiento por sí solo — produce bordes gruesos si no se combina con algo más.
- **Laplaciano**: operador de **segunda derivada**. Detecta bordes por **cruces por cero** (donde la segunda derivada cambia de signo). No es "lo mismo que Sobel aplicado tras un suavizado": son matemáticamente distintos (primera vs. segunda derivada), y no producen los mismos bordes.

Ninguno de los dos, por separado, resuelve el problema de detectar bordes "significativos" evitando ruido, bordes gruesos o discontinuos.

### Canny: la combinación completa

El algoritmo de Canny combina tres pasos:

1. Calcula el **gradiente** (magnitud y dirección), típicamente vía Sobel tras un suavizado gaussiano previo (para reducir sensibilidad al ruido).
2. Aplica **supresión de no máximos** (NMS): en la dirección perpendicular al borde, solo conserva el píxel con magnitud máxima local, adelgazando el borde a un único píxel de ancho.
3. Aplica **umbralización por histéresis con dos umbrales** (alto y bajo): los píxeles con magnitud por encima del umbral alto se aceptan como borde con seguridad; los de magnitud intermedia (entre el umbral bajo y el alto) solo se aceptan si están **conectados** a un píxel ya aceptado por encima del umbral alto. Los que están por debajo del umbral bajo se descartan directamente.

### La trampa sobre histéresis que fallaste

Subir el **umbral bajo** hace el criterio de aceptación de píxeles débiles **más estricto** (hace falta más magnitud para que un píxel intermedio cuente como candidato a conectar), así que **menos** píxeles se conectan a los bordes fuertes: los bordes tienden a **fragmentarse más**, no a hacerse más largos y continuos. Es fácil confundir la dirección del efecto — memorízalo al revés de la intuición ingenua: umbral bajo más alto = bordes más discontinuos, no más conectados.

Y Canny, en su formulación clásica, **requiere fijar manualmente** ambos umbrales (o su razón); existen variantes que los estiman automáticamente (p. ej. con Otsu), pero no es una propiedad garantizada del algoritmo base.

### Ejercicio 4

Aplicas Canny a una imagen con ruido moderado y obtienes bordes muy fragmentados en zonas de contorno real (el borde de un objeto se rompe en segmentos cortos). Tienes dos umbrales actuales: alto=150, bajo=100. Propón un ajuste concreto de ambos umbrales para reducir la fragmentación, y explica el riesgo que corres si te pasas ajustándolos en esa dirección.

---

## 5. CNN vs. descriptores hechos a mano (SIFT/HOG)

### La diferencia central

SIFT, HOG y similares son descriptores **diseñados a mano**: un ingeniero decidió explícitamente qué filtros aplicar y qué reglas seguir para extraer características (gradientes orientados, escalas, etc.), basándose en conocimiento previo del dominio. Una CNN, en cambio, **aprende automáticamente** sus filtros mediante descenso de gradiente y retropropagación, a partir de datos etiquetados — nadie diseña a mano qué debe detectar cada kernel.

### La trampa sobre datos: menos datos, no más

Es tentador pensar que, como las CNN "aprenden solas", necesitan *menos* supervisión. Es justo lo contrario: las CNN entrenadas desde cero típicamente requieren **grandes volúmenes de datos etiquetados** para converger a representaciones útiles. En regímenes de **muy pocos datos**, descriptores hechos a mano como SIFT pueden ser más robustos o competitivos, precisamente porque ya incorporan conocimiento previo (invariancias geométricas, etc.) que una CNN tendría que aprender desde datos que no tiene.

### Inicialización de los kernels

Los kernels convolucionales **no** se inicializan imitando filtros de Gabor ni ningún filtro predefinido tipo SIFT. Se inicializan con esquemas aleatorios estándar (He, Xavier/Glorot) y se aprenden por completo mediante retropropagación desde cero.

### Jerarquía de representaciones (esto sí es un resultado ampliamente observado)

Las primeras capas convolucionales de una CNN entrenada para clasificación tienden a aprender filtros similares a **detectores de bordes y gradientes de color** (parecido, mecánicamente, a lo que hace Sobel — pero aprendido, no diseñado). Las capas más profundas capturan progresivamente patrones **semánticos** más abstractos y específicos de la tarea (partes de objetos, texturas complejas, clases enteras). Esto se ha verificado repetidamente mediante visualización de filtros y mapas de activación.

### Campo receptivo

El campo receptivo de una neurona en una capa profunda **no depende solo del kernel de esa capa**: se acumula a través de todas las capas anteriores (tamaño de kernel, stride, dilatación de cada una). Una neurona en una capa profunda puede "ver" efectivamente una región mucho mayor de la imagen de entrada que el tamaño de su propio kernel local, precisamente por ese efecto acumulativo capa a capa.

### Ejercicio 5

Te piden un sistema de reconocimiento de un tipo específico de pieza industrial, con solo 40 imágenes etiquetadas disponibles (dataset muy pequeño) y sin posibilidad de conseguir más a corto plazo. Argumenta, con lo aprendido en este módulo, por qué entrenar una CNN desde cero sería probablemente una mala decisión aquí, y menciona dos alternativas razonables (una basada en descriptores clásicos, otra basada en aprovechar redes ya entrenadas).

---

## 6. Distorsión de lente: modelo de Brown-Conrady

### ¿Qué es?

Ninguna lente real proyecta la escena perfectamente según el modelo de cámara pinhole ideal. El modelo de **Brown-Conrady** describe la desviación entre la posición ideal (pinhole) y la posición real observada de un punto en la imagen, mediante dos componentes:

- **Distorsión radial**: la más notoria. Las líneas rectas que no pasan por el centro óptico aparecen curvadas — hacia afuera (*barrel/barril*, típico de gran angular) o hacia adentro (*pincushion/cojín*, típico de teleobjetivos). Se modela con un polinomio en potencias pares de la distancia radial al centro (`k1, k2, k3, ...`).
- **Distorsión tangencial**: causada por un desalineamiento físico entre la lente y el plano del sensor (no son perfectamente paralelos). Se modela con coeficientes adicionales (`p1, p2`).

### Corrección

La calibración de cámara (por ejemplo con el método de Zhang, usando un patrón de tablero de ajedrez fotografiado desde varios ángulos) estima estos coeficientes junto con los parámetros intrínsecos (focal, punto principal). Con ellos, se puede **corregir** la distorsión, remapeando cada píxel de la imagen distorsionada a su posición "ideal" pinhole.

### Ejercicio 6

Fotografías con un gran angular muestran las líneas de un edificio (que en la realidad son rectas y verticales) curvándose visiblemente hacia afuera cerca de los bordes de la imagen, pero permanecen prácticamente rectas cerca del centro. ¿Qué tipo de distorsión es (radial o tangencial), y por qué el efecto es más pronunciado en los bordes que en el centro de la imagen? (Pista: piensa en qué variable del modelo determina la magnitud de la corrección.)

---

## 7. Cascadas Haar y Viola-Jones

### ¿Qué es?

Viola-Jones (2001) es un algoritmo de detección de objetos (clásicamente, caras) basado en tres ideas combinadas:

1. **Características tipo Haar**: rectángulos simples (diferencias de sumas de intensidad entre regiones adyacentes) que capturan patrones básicos como bordes o líneas.
2. **Imagen integral**: una estructura de datos precomputada que permite calcular la suma de intensidades de cualquier región rectangular en **tiempo constante**, sin importar el tamaño del rectángulo — esto es lo que hace viable evaluar miles de características Haar rápidamente.
3. **AdaBoost en cascada**: se entrena una secuencia de clasificadores débiles cada vez más selectivos, organizados en **etapas en cascada**. Cada etapa descarta rápidamente la inmensa mayoría de ventanas que claramente no contienen el objeto (por ejemplo, fondo), y solo las ventanas que pasan todas las etapas anteriores llegan a las etapas finales, más costosas y precisas. Esto hace el algoritmo muy rápido en la práctica, porque el trabajo pesado se concentra solo en las regiones prometedoras.

### Ejercicio 7

Explica en tus propias palabras por qué organizar los clasificadores en **cascada** (en vez de aplicar directamente el clasificador más preciso y costoso a cada ventana de la imagen) es clave para que Viola-Jones funcione en tiempo real, relacionándolo con el hecho de que la mayoría de ventanas evaluadas en una imagen típica no contienen el objeto buscado.

---

## 8. Pirámides Gaussianas/Laplacianas y espacio de escalas

### Pirámide Gaussiana

Se construye aplicando suavizado gaussiano y **submuestreo** (reducir la resolución, típicamente a la mitad) de forma repetida, generando una secuencia de imágenes cada vez más pequeñas y suaves. Sirve como base para procesamiento multiescala: muchos algoritmos (registro, flujo óptico, detección) se benefician de operar primero a baja resolución (para capturar estructura grande y desplazamientos grandes) y refinar progresivamente en niveles de mayor resolución.

### Pirámide Laplaciana

Se construye a partir de la diferencia entre un nivel de la pirámide Gaussiana y una versión "expandida" (interpolada de vuelta a su tamaño) del nivel siguiente, más pequeño. Cada nivel de la pirámide Laplaciana captura, esencialmente, el detalle de alta frecuencia que se pierde al pasar de un nivel Gaussiano al siguiente más reducido — es una forma de descomponer la imagen en bandas de frecuencia.

### Espacio de escalas y DoG (Difference of Gaussians)

SIFT construye un **espacio de escalas** aplicando gaussianas con desviaciones estándar (`σ`) crecientes, y calcula la diferencia entre gaussianas consecutivas (**DoG**, una aproximación computacionalmente barata del Laplaciano de Gaussiano, LoG) para detectar puntos clave (*keypoints*) que son extremos locales tanto en espacio como en escala — esto es lo que da a SIFT su característica **invariancia a escala**: el mismo punto físico se detecta como keypoint independientemente de a qué distancia/zoom se fotografíe.

### Ejercicio 8

Explica la relación entre la pirámide Gaussiana (submuestreo progresivo) y el espacio de escalas de SIFT (gaussianas de `σ` creciente sin submuestreo dentro de cada octava): ¿por qué SIFT necesita ambas cosas — submuestrear entre octavas y suavizar progresivamente dentro de cada octava — para lograr invariancia a escala real?

---

## 9. Registro de imágenes: Lucas-Kanade, Gauss-Newton/LM, ICP

Este es probablemente el módulo más denso del curso — fallaste esta pregunta en un test de nivel senior, así que vamos a fondo.

### El problema general

Registro de imágenes (o de nubes de puntos, en el caso de ICP) es encontrar la transformación que mejor alinea dos conjuntos de datos, minimizando algún error (fotométrico, de distancia entre puntos correspondientes). La mayoría de métodos prácticos son **iterativos**: parten de una estimación inicial y la refinan paso a paso mediante **linealización local** del problema (Gauss-Newton) alrededor de la estimación actual.

### La linealización solo es válida localmente

Lucas-Kanade estándar (formulación Gauss-Newton) **linealiza** el término de intensidad de primer orden (aproximación de Taylor). Esa aproximación **solo es válida para desplazamientos pequeños** entre las dos imágenes. Ante movimientos grandes, la linealización deja de representar bien el problema real, y el algoritmo puede **divergir o quedar atrapado en un mínimo local** del error fotométrico — no converge "siempre al mínimo global independientemente de la magnitud del desplazamiento inicial", como podrías asumir ingenuamente.

### La solución: pirámides multiescala

Un enfoque grueso-a-fino (usando la pirámide Gaussiana del módulo anterior) estima primero el desplazamiento a baja resolución, donde el mismo movimiento en píxeles es proporcionalmente **menor** (cumple mejor la hipótesis de linealización), y usa esa estimación grosera como inicialización al refinar en el siguiente nivel, más fino. Esto **amplía la cuenca de convergencia** del algoritmo — puede manejar desplazamientos iniciales mucho mayores de los que la formulación de un solo nivel toleraría.

### El problema de apertura y la singularidad de la matriz Hessiana

En regiones con gradiente dominante en una única dirección (por ejemplo, un borde recto sin textura perpendicular a él), la matriz de segundo momento (la Hessiana aproximada de Gauss-Newton) se vuelve **singular o mal condicionada**: tiene un autovalor cercano a cero en la dirección paralela al borde. Esto es exactamente el **problema de apertura**: el desplazamiento a lo largo del borde queda indeterminado, porque no hay suficiente información de gradiente en esa dirección para restringirlo.

### Levenberg-Marquardt: el amortiguamiento

Sumar un múltiplo de la identidad al Hessiano (`H + λI`) — la idea central de Levenberg-Marquardt — mejora el condicionamiento cuando la matriz está cerca de ser singular, comportándose más como un descenso de gradiente simple en esas direcciones mal determinadas. Esto da **robustez** frente a direcciones sin información suficiente, a costa de **ralentizar** la convergencia cuadrática típica de Gauss-Newton puro cerca del óptimo (cuando ya no hace falta tanto amortiguamiento).

### ICP: converge, pero no necesariamente al óptimo global

ICP (*Iterative Closest Point*) alterna entre (a) encontrar, para cada punto de una nube, su vecino más cercano en la otra nube, y (b) recalcular la transformación rígida que minimiza el error de esas correspondencias. Esto converge **monótonamente** (el error nunca aumenta de una iteración a la siguiente) hacia un **mínimo local**, pero ese mínimo **no tiene por qué ser el óptimo global**. Con una inicialización pobre, ICP puede converger a un alineamiento incorrecto — por ejemplo, si la escena tiene simetrías, o si el solapamiento entre las dos nubes es insuficiente.

### Ejercicio 9

Estás alineando dos escaneos LIDAR consecutivos de un pasillo largo y simétrico (paredes paralelas casi idénticas a ambos lados) usando ICP con una inicialización basada solo en la odometría del robot (que tiene cierto margen de error). Explica dos riesgos concretos de este escenario relacionados con lo aprendido (uno relacionado con mínimos locales/simetría, otro relacionado con el problema de apertura si usaras un método basado en gradiente de intensidad en vez de ICP puro), y propón una mitigación para cada uno.

---

## 10. Normalización fotométrica en vídeo: CLAHE, homomórfico, flicker

### El problema específico de vídeo (no de imágenes aisladas)

Cualquier técnica de normalización fotométrica (ecualización de histograma, CLAHE, gamma, homomórfico) que **recalcule sus parámetros de forma completamente independiente en cada fotograma**, sin ninguna memoria temporal, introduce riesgo de **parpadeo (flicker)**: pequeñas variaciones de contenido o ruido de un fotograma a otro alteran ligeramente el histograma local, y por tanto el mapeo de intensidades resultante cambia, generando saltos de brillo/contraste **visibles** entre fotogramas consecutivos, aunque cada fotograma individual se vea "correcto" en aislamiento.

### CLAHE no resuelve el flicker por sí solo

El recorte de contraste (*clip limit*) de CLAHE reduce la sobreamplificación de **ruido dentro de un mismo fotograma** (evita que zonas casi uniformes con poco ruido se amplifiquen agresivamente), pero **no introduce ninguna coherencia entre fotogramas**. Si aplicas CLAHE de forma independiente a cada fotograma de un vídeo, el flicker temporal sigue siendo perfectamente posible.

### Filtrado homomórfico

Modela la imagen como `I(x,y) = L(x,y)·R(x,y)` (iluminación por reflectancia). Tomando logaritmos, el producto se convierte en una suma, que se puede separar en el dominio de la frecuencia: la componente de iluminación varía **lentamente** (baja frecuencia), mientras la reflectancia (textura, bordes) varía **rápidamente** (alta frecuencia). Un filtro paso-alto en frecuencia atenúa la iluminación conservando el detalle de reflectancia.

### La corrección gamma fija no basta

Estimar un `γ` fijo en el primer fotograma y aplicarlo durante toda la secuencia asume que la relación entre irradiancia y valor de píxel es invariante en el tiempo. En la práctica no lo es: exposición automática, ganancia AGC de la cámara o cambios reales de iluminación de la escena hacen que esa relación **cambie dinámicamente**, así que un `γ` fijo del primer fotograma deja de ser adecuado a medida que avanza la secuencia.

### La solución robusta: coherencia temporal sobre los parámetros

En vez de recalcular los parámetros de corrección (histograma acumulado, gamma, ganancia) de forma independiente cada fotograma, se suavizan/filtran con paso bajo **a lo largo de una ventana temporal** de fotogramas anteriores. Esto reduce la variación brusca de un fotograma a otro (mitigando el flicker) sin perder la capacidad de adaptarse a cambios reales y progresivos de iluminación.

### Ejercicio 10

Estás procesando vídeo de una cámara de seguridad de exterior donde pasan nubes rápidas causando cambios de iluminación bruscos pero reales (no ruido). Propón, en términos generales (sin código), una estrategia de normalización fotométrica que distinga entre "cambio real de iluminación que hay que seguir" y "flicker artificial que hay que suprimir", usando lo aprendido sobre suavizado temporal de parámetros.

---

## 11. Segmentación por clustering: K-means, mean shift, SLIC

### K-means: asume clústeres convexos

K-means minimiza la varianza intra-clúster mediante distancia euclídea al centroide. Esto **asume implícitamente** que los clústeres tienen forma aproximadamente esférica/convexa en el espacio de características. Consecuencia práctica: puede **fallar** al segmentar un mismo objeto bajo **iluminación no uniforme**, porque sus píxeles forman un clúster **alargado** en el espacio RGB (de zonas oscuras a zonas claras del mismo objeto) — K-means tiende a partir ese clúster alargado en varios trozos, o a mezclarlo incorrectamente con otro objeto de color parecido en algún extremo del gradiente de iluminación.

Añadir coordenadas espaciales `(x,y)` al vector de características **favorece** cierta coherencia espacial, pero **no la garantiza**: K-means sigue asignando por distancia mínima en el espacio conjunto sin ninguna restricción topológica explícita, así que pueden seguir apareciendo clústeres con píxeles no contiguos.

### Mean shift: no paramétrico, pero muy sensible al bandwidth

Mean shift no requiere fijar de antemano el número de clústeres — estos **emergen** como modos (máximos locales) de la densidad estimada en el espacio de características. Pero el **ancho de banda** (*bandwidth*) del kernel usado para estimar esa densidad es crítico: un bandwidth pequeño produce **sobre-segmentación** (muchos modos detectados), uno grande produce **infra-segmentación** (pocos modos). No es un parámetro que "solo afecte a la velocidad de convergencia" — cambia drásticamente el resultado. Además, mean shift suele ser considerablemente **más lento** que K-means, al requerir búsquedas de vecinos por cada punto en cada iteración.

### SLIC: color + posición, con búsqueda local acotada

Los superpíxeles SLIC combinan distancia de color en el espacio **Lab** con distancia **espacial** `(x,y)`, ponderadas por un parámetro de compacidad `m`, y restringen la búsqueda a una **ventana local** alrededor de cada centro candidato. Esto es lo que garantiza que los superpíxeles resultantes sean espacialmente **compactos y conexos** — a diferencia de K-means con `(x,y,color)`, que no impone ninguna restricción de búsqueda local y por tanto no da esa garantía de conectividad.

### Ejercicio 11

Necesitas segmentar imágenes de hojas de plantas con enfermedades (manchas de color irregular sobre un fondo verde con iluminación desigual del follaje), donde el número de manchas por hoja es desconocido y variable. Argumenta cuál de los tres métodos (K-means, mean shift, SLIC) es el punto de partida más razonable, y qué limitación concreta de ese método tendrías que mitigar aparte (por ejemplo, combinándolo con otro paso de procesamiento).

---

## 12. Transformada de Fourier 2D y muestreo

### El teorema de convolución: cuándo conviene usar FFT

Convolucionar una imagen con un kernel en el dominio espacial cuesta `O(N·k²)` (N = número de píxeles, k = tamaño del kernel). El teorema de convolución permite hacer lo mismo en el dominio de frecuencia: FFT de la imagen, FFT del kernel, multiplicación punto a punto, FFT inversa — coste `O(N log N)`, independiente del tamaño del kernel. Para kernels **grandes**, esto es mucho más eficiente. Pero para kernels **pequeños** (3×3, 5×5), la convolución espacial directa suele ser **más rápida**: el coste fijo de las dos FFT (ida y vuelta) no compensa frente a un kernel reducido. No es que el enfoque frecuencial sea "siempre más eficiente independientemente del tamaño del kernel" — depende del tamaño.

### Zero-padding: no es solo estético

Sin suficiente zero-padding antes de la FFT, multiplicar en frecuencia calcula una **convolución circular**, no la convolución lineal que normalmente quieres. El resultado en los bordes de la imagen difiere del de la convolución lineal correcta, por el efecto de *wrap-around* (los bordes "se contaminan" con información del extremo opuesto de la imagen, como si fuera cíclica). No es una cuestión de mejorar la resolución visual del espectro mostrado — afecta directamente al resultado numérico.

### Nyquist y aliasing

Si la frecuencia de muestreo de una señal (o imagen) es inferior al **doble** de la frecuencia máxima presente en ella (frecuencia de Nyquist), las réplicas periódicas del espectro se **solapan**, produciendo **aliasing**: se manifiesta visualmente como patrones **moiré** o como estructuras de alta frecuencia mal representadas que aparecen como frecuencias más bajas espurias.

### Fase vs. magnitud

Un resultado clásico (Oppenheim & Lim): la **fase** de la Transformada de Fourier de una imagen natural conserva la mayor parte de la información **estructural** perceptualmente relevante (bordes, formas reconocibles). Reconstruir usando **solo la magnitud** (con fase aleatoria) produce una imagen que parece ruido, sin estructura reconocible — contraintuitivo si asocias "magnitud" con "la energía/el contenido importante", pero es la fase la que codifica dónde están las cosas.

### Ejercicio 12

Vas a aplicar un filtro de suavizado con un kernel gaussiano de 51×51 píxeles a una imagen de 4K. Justifica si conviene implementarlo vía FFT (teorema de convolución) o vía convolución espacial directa, mencionando explícitamente el zero-padding necesario si eliges FFT.

---

## 13. Robustez adversarial de CNN

### El patrón general en esta literatura

Muchas defensas que "parecen funcionar" empíricamente fallan frente a atacantes más fuertes o adaptativos. Solo el entrenamiento adversarial iterativo (PGD) mantiene robustez empírica sostenida, con costes claros.

### Gradient masking / obfuscated gradients: falsa sensación de seguridad

Técnicas que dificultan el cálculo del gradiente (para que ataques basados en gradiente parezcan fallar) **no hacen al modelo genuinamente más robusto**. Athalye et al. (2018) mostraron que la mayoría de estas defensas son rotas por **ataques adaptativos** (como BPDA), que sortean la ofuscación sin necesitar el gradiente exacto del modelo defendido. Ofuscar el gradiente dificulta el ataque ingenuo, pero no elimina la vulnerabilidad subyacente.

### Adversarial training: robustece, pero con trade-offs reales

El entrenamiento adversarial con ejemplos generados iterativamente (PGD, Madry et al.) sí mejora la robustez empírica frente a ataques de ese tipo, pero:

- Típicamente **reduce la precisión sobre ejemplos limpios** (*clean accuracy*): hay un trade-off robustez/precisión ampliamente documentado.
- **Aumenta considerablemente el coste computacional** del entrenamiento (varios forward/backward extra por cada paso de PGD, en cada iteración de entrenamiento).

Ojo con una variante peligrosa: entrenar solo con **FGSM de un solo paso** (más barato que PGD) sufre "catastrophic overfitting" y produce una falsa sensación de robustez (un gradiente enmascarado alrededor del punto FGSM específico), fallando frente a ataques multi-paso más fuertes como PGD — no está "garantizado como robusto frente a ataques iterativos" por el hecho de haber visto ejemplos adversariales durante el entrenamiento.

### Transferibilidad: la base real de los ataques de caja negra

Las perturbaciones generadas contra un modelo sustituto (entrenado por el propio atacante) **sí transfieren** frecuentemente a otros modelos con arquitecturas distintas — está bien documentado y es precisamente la base de los ataques prácticos de caja negra, que no requieren acceso a los gradientes del modelo objetivo real.

### Destilación defensiva: no es robustez certificada

Fue rota empíricamente por Carlini & Wagner y no ofrece ninguna garantía matemática certificada. No confundas esto con **randomized smoothing**, que sí proporciona garantías certificadas (bajo supuestos concretos) frente a perturbaciones acotadas — son mecanismos completamente distintos, no equivalentes.

### Ejercicio 13

Un colega propone defender un modelo de clasificación de imágenes médicas simplemente aplicando una transformación no diferenciable (por ejemplo, una cuantización agresiva de píxeles) antes de pasar la imagen al modelo, argumentando que "así el atacante no puede calcular el gradiente para generar el ataque". Evalúa esta propuesta con lo aprendido sobre gradient masking y ataques adaptativos: ¿es una defensa genuina? ¿Qué tipo de ataque esperarías que la rompiera?

---

## Soluciones

### Solución 1

Proceso: (1) detectar y describir puntos de interés en ambas imágenes (SIFT); (2) emparejar descriptores entre las dos imágenes, obteniendo ~30 correspondencias candidatas, con 6 erróneas entre ellas; (3) aplicar RANSAC: muestrear repetidamente subconjuntos de 4 correspondencias no colineales, calcular `H` con DLT para cada subconjunto, contar cuántas de las 30 correspondencias son consistentes (inliers) con esa `H` dentro de un umbral de error de reproyección; (4) quedarte con la `H` que maximiza los inliers (debería excluir las 6 erróneas) y, opcionalmente, refinar `H` con un ajuste no lineal (mínimos cuadrados) usando solo los inliers finales. El hecho de que la cámara se haya trasladado lateralmente no invalida la homografía porque el **cartel es un plano** (condición (a) del módulo): una homografía relaciona exactamente dos vistas de cualquier plano, independientemente de si la cámara roto o se trasladó, siempre que todo lo fotografiado esté sobre ese único plano — el paralaje solo aparece con relieve 3D real, que aquí no existe (el cartel es plano).

### Solución 2

(a) **Línea base corta**: en distancias cortas (0.5–5 m) una baseline corta ya da suficiente disparidad para triangular con precisión razonable, y minimiza oclusiones y cambios de perspectiva entre cámaras — importante en un pasillo estrecho donde el solapamiento de campo de visión es limitado. (b) **SGM (semi-global)**: las paredes lisas y poco texturizadas son exactamente el escenario donde el matching puramente local (SAD/SSD) sufre ambigüedad por falta de textura distintiva; el término de suavidad/regularización de SGM propaga información desde regiones con textura hacia las regiones ambiguas vecinas, dando resultados mucho más robustos que un matching local puro en paredes lisas.

### Solución 3

**SORT** por sí solo probablemente le asignaría un **ID nuevo**: tras 4 fotogramas sin detección asociada, el track original probablemente ya fue eliminado por el mecanismo de gestión de tracks (o, si sigue vivo, la predicción de Kalman pura basada en velocidad constante puede haberse desviado bastante de la posición real tras una oclusión larga, dando IoU bajo con la nueva detección tras reaparecer 2 metros más adelante). **DeepSORT** tiene más probabilidad de recuperar el **mismo ID**, porque el descriptor de apariencia (embedding de re-identificación) del peatón que reaparece puede compararse por similitud coseno contra los descriptores de tracks recientemente perdidos, incluso si la posición geométrica predicha ya no coincide bien — es exactamente el escenario de oclusión para el que DeepSORT fue diseñado. SORT fallaría más en oclusiones largas con movimiento impredecible; DeepSORT fallaría más si hay otro peatón con apariencia muy similar cerca en ese momento (ambigüedad de apariencia).

### Solución 4

Ajuste razonable: **bajar el umbral bajo** (por ejemplo, de 100 a 70) manteniendo el umbral alto en 150, para que más píxeles de magnitud intermedia puedan conectarse a los segmentos fuertes ya detectados, reduciendo la fragmentación. El riesgo de pasarse: si bajas demasiado el umbral bajo, empiezas a aceptar como "conectados" píxeles que en realidad son ruido cerca de bordes reales, generando bordes más largos pero también más **falsos positivos** y ramificaciones espurias alrededor del contorno real — un trade-off clásico entre continuidad y limpieza del resultado.

### Solución 5

Con solo 40 imágenes, una CNN entrenada desde cero muy probablemente no tendría suficientes datos para aprender filtros útiles por sí misma y sobreajustaría severamente (memorizaría las 40 imágenes sin generalizar). Alternativas razonables: (1) usar descriptores clásicos como SIFT/HOG combinados con un clasificador simple (SVM, k-NN) sobre esas características — no requieren aprender representaciones desde datos, ya incorporan invariancias útiles de fábrica; (2) usar **transfer learning**: tomar una CNN preentrenada en un dataset grande (ImageNet, etc.) y hacer *fine-tuning* solo de las últimas capas (o usarla como extractor de características fijo) con tus 40 imágenes — aprovechas la jerarquía de bordes/texturas/semántica ya aprendida en un dominio grande, adaptando solo la parte final específica de tu tarea.

### Solución 6

Es distorsión **radial** (de tipo barril, dado que se curva hacia afuera — típico de gran angular). Es más pronunciada en los bordes porque el modelo de Brown-Conrady expresa la corrección radial como un polinomio en potencias de la **distancia al centro óptico** (`r = √(x²+y²)`, con términos `k1·r², k2·r⁴, ...`): cerca del centro, `r` es pequeño y el efecto de esos términos es casi despreciable; lejos del centro (bordes de la imagen), `r` crece y el polinomio amplifica la distorsión considerablemente — de ahí que las líneas casi no se noten curvadas cerca del centro pero sí notablemente cerca de los bordes.

### Solución 7

La inmensa mayoría de ventanas evaluadas en una imagen típica (recorriendo todas las posiciones y escalas posibles) **no** contienen el objeto buscado — son fondo. Si aplicaras directamente el clasificador final más preciso (y más costoso computacionalmente) a cada una de esas ventanas, malgastarías la mayor parte del cómputo evaluando exhaustivamente ventanas que un criterio mucho más barato ya podría descartar con alta confianza. La cascada resuelve esto poniendo primero etapas muy rápidas y baratas que descartan la mayoría de ventanas de fondo casi instantáneamente (con una o dos características Haar evaluadas vía imagen integral), dejando que solo una pequeña fracción de ventanas "prometedoras" lleguen a las etapas más tardías, más selectivas y costosas — el trabajo caro se concentra donde realmente aporta, no en todas partes.

### Solución 8

El submuestreo entre octavas (pirámide Gaussiana) reduce la resolución de la imagen, lo que simula el efecto de "alejarse" o fotografiar el mismo objeto desde más lejos — necesario para detectar el mismo keypoint físico cuando aparece a **tamaños muy distintos** en la imagen (invariancia a escalas grandes, de un orden de magnitud o más entre octavas). Dentro de cada octava, el suavizado progresivo con `σ` creciente (sin submuestrear todavía) permite explorar **escalas intermedias, finas**, entre un nivel de octava y el siguiente, calculando el DoG entre gaussianas consecutivas para localizar el `σ` exacto donde cada keypoint concreto es más estable. Ambos mecanismos juntos cubren el rango completo de escalas: submuestreo para saltos grandes (entre octavas), suavizado gaussiano fino para el ajuste preciso dentro de cada octava.

### Solución 9

Riesgo 1 (mínimos locales/simetría): en un pasillo largo con paredes prácticamente idénticas a ambos lados, ICP puede encontrar fácilmente correspondencias "vecino más cercano" que son geométricamente plausibles pero corresponden a un desplazamiento incorrecto a lo largo del eje del pasillo (por ejemplo, desplazado exactamente la distancia entre dos features repetidas de la pared) — un mínimo local de apariencia casi idéntica al correcto. Mitigación: usar la odometría como inicialización de alta confianza y limitar la búsqueda de correspondencias a una vecindad razonable alrededor de esa predicción, en vez de buscar el vecino más cercano global sin restricción. Riesgo 2 (problema de apertura, si usaras gradiente de intensidad en vez de ICP puro sobre nubes de puntos): las paredes lisas y paralelas tienen gradiente dominante perpendicular a su superficie pero casi nulo a lo largo de la dirección del pasillo, así que el desplazamiento a lo largo de ese eje quedaría mal determinado (matriz Hessiana casi singular en esa dirección) — es literalmente el problema de apertura aplicado a esta geometría. Mitigación: incorporar información adicional no ambigua en esa dirección (por ejemplo, características puntuales discretas del entorno, o fusionar con odometría/IMU) en vez de depender solo del gradiente de intensidad a lo largo del pasillo.

### Solución 10

Estrategia: en vez de recalcular los parámetros de corrección de forma totalmente independiente cada fotograma (lo que confundiría el cambio real de las nubes con ruido de fotograma a fotograma), se suavizan esos parámetros (por ejemplo, el histograma acumulado o la ganancia estimada) con un filtro paso-bajo temporal de **ventana relativamente corta** — lo bastante corta para seguir cambios reales de iluminación en la escala de tiempo en que pasan las nubes (segundos), pero lo bastante larga para promediar el ruido fotograma a fotograma (decenas de milisegundos). La clave conceptual es que el suavizado temporal no elimina el cambio real, solo el componente de variación mucho más rápida que el fenómeno real que quieres seguir — ajustar la ventana temporal al orden de magnitud del fenómeno que sí quieres conservar es lo que separa "señal real" de "flicker".

### Solución 11

**SLIC** es el punto de partida más razonable: da superpíxeles compactos y coherentes espacialmente incluso con iluminación desigual sobre la hoja (porque incorpora también la posición espacial con ventana local acotada, mitigando parcialmente el problema de K-means con clústeres alargados por iluminación), y no requiere fijar de antemano el número de manchas. Limitación a mitigar aparte: SLIC agrupa en superpíxeles homogéneos, pero **no clasifica** por sí solo qué superpíxeles corresponden a "mancha enferma" vs. "hoja sana" — necesitarías un paso posterior (por ejemplo, un clasificador simple sobre el color/textura promedio de cada superpíxel, o agrupar superpíxeles similares con otro nivel de clustering) para decidir qué regiones son realmente patológicas.

### Solución 12

Conviene usar **FFT / teorema de convolución**: un kernel de 51×51 es grande (2601 posiciones por píxel en convolución directa), y el coste `O(N·k²)` de la convolución espacial directa sobre una imagen 4K sería considerable comparado con el `O(N log N)` de la vía FFT. Es necesario aplicar **zero-padding** tanto a la imagen como al kernel antes de las FFT (típicamente hasta un tamaño de al menos `tamaño_imagen + tamaño_kernel - 1` en cada dimensión) para que la multiplicación en frecuencia calcule la convolución **lineal** deseada y no una convolución circular con artefactos de wrap-around en los bordes.

### Solución 13

No es una defensa genuina: es un caso de **gradient masking** (la cuantización agresiva no es diferenciable, así que el gradiente exacto respecto a la entrada original no se puede calcular directamente a través de ella). Según Athalye et al., este tipo de defensas suele ofrecer solo una **falsa sensación de seguridad**: un atacante puede usar un ataque adaptativo tipo **BPDA** (*Backward Pass Differentiable Approximation*), que aproxima el gradiente de la transformación no diferenciable con una función sustituta diferenciable (por ejemplo, la función identidad, ya que la cuantización se parece a "casi no hacer nada" en la pasada hacia atrás) para seguir optimizando la perturbación adversarial de extremo a extremo, sorteando la ofuscación. La recomendación correcta sería evaluar la defensa específicamente contra ataques adaptativos (no solo contra ataques estándar de caja blanca que asumen gradiente directo) antes de considerarla robusta, y preferir entrenamiento adversarial (PGD) como línea base con robustez empíricamente sostenida.
