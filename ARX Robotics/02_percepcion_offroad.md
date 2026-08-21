# Dossier 1 — Percepción off-road

*Material autocontenido. Enlaces al final de cada sección para profundizar.*

---

## 1. El cambio de paradigma: de detección a transitabilidad

En carretera, la percepción responde a *"¿qué objetos hay y dónde van?"*. El mundo está pre-estructurado: hay carriles, un mapa HD, y el suelo se asume plano y transitable por definición.

Off-road nada de eso se sostiene. **El suelo deja de ser un supuesto y pasa a ser el objeto principal de la percepción.** La pregunta cambia a: *"¿puedo poner las orugas ahí, y salir de ahí?"*. Eso es **traversability estimation** (estimación de transitabilidad), y es la representación central de todo el stack.

Consecuencias que debes poder enunciar:

- **La geometría es ambigua.** Una mata de hierba de 60 cm y una roca de 60 cm producen prácticamente la misma firma en una nube de puntos. Una se atropella, la otra te rompe la transmisión. Sin semántica o sin propiedades físicas, no puedes distinguirlas — y si tratas toda la vegetación alta como obstáculo, el robot se paraliza en un prado.
- **Existen obstáculos negativos.** Zanjas, socavones, cornisas, cráteres. Un LiDAR montado bajo los ve como *ausencia de retorno*, no como presencia de puntos. Detectar la ausencia es un problema distinto y peor condicionado que detectar la presencia.
- **El terreno tiene propiedades no visibles.** Barro, arena suelta, nieve, hielo, hierba mojada. Dos superficies visualmente idénticas pueden tener coeficientes de tracción radicalmente distintos. Esto no se resuelve con visión sola: se resuelve con propiocepción.
- **No hay clase "conocida".** En terreno no estructurado, lo *out-of-distribution* es la norma, no la excepción. Un sistema que asume que su ontología es completa fallará silenciosamente.
- **La verdad de terreno es cara.** No hay flotas de millones de kilómetros. Por eso la anotación propia, los datos sintéticos y el aprendizaje auto-supervisado dejan de ser optimizaciones y pasan a ser la estrategia.

📚 [Autonomous Driving in Unstructured Environments: How Far Have We Come? (arXiv:2410.07701)](https://arxiv.org/abs/2410.07701) — el survey general más completo, +250 papers.

---

## 2. Representación del entorno

### 2.1 Mapas de elevación (2.5D) — el caballo de batalla

La representación estándar en robótica de campo es un **grid map multicapa robot-céntrico**: una rejilla en el plano XY donde cada celda almacena varias capas — elevación, varianza de la elevación, pendiente, rugosidad, step height, clase semántica, coste.

Ideas clave:

- **Robot-céntrico y con incertidumbre explícita.** El mapa se construye alrededor del vehículo y cada celda propaga la incertidumbre de la estimación de pose. Esto importa mucho: en terreno accidentado la deriva de pose contamina el mapa, y un mapa que no modela su propia incertidumbre miente.
- **Métricas derivadas** (las que alimentan el coste): pendiente local (ajuste de plano), rugosidad (desviación estándar de la elevación en una ventana), *step height* (salto máximo entre celdas vecinas), curvatura. Cada una tiene un umbral ligado a la física del vehículo — y aquí está el enlace con GEREON vs HECTOR: **los mismos datos, umbrales distintos**.
- **Celdas no observadas ≠ celdas libres.** El error clásico y peligroso. Un mapa de elevación tiene huecos por oclusión y por sombra de rango. Tratarlos como transitables mete al vehículo en una zanja; tratarlos como obstáculo lo paraliza. La respuesta correcta es **una tercera categoría — desconocido — que la capa de comportamiento trate con una política explícita** (reducir velocidad, aproximarse para observar, o rodear).

Implementación de referencia: `grid_map` (ETH/ANYbotics) para la estructura multicapa y `elevation_mapping_cupy` para el mapping acelerado por GPU con capa semántica integrada.

📚 [grid_map](https://github.com/ANYbotics/grid_map) · [elevation_mapping_cupy](https://github.com/leggedrobotics/elevation_mapping_cupy) (usa esta, la versión CPU original ya no se mantiene)

### 2.2 Cuándo hace falta 3D real

2.5D falla cuando hay estructura vertical superpuesta: dosel arbóreo (puedes pasar por debajo), puentes, túneles, salientes rocosos. Ahí se necesita representación volumétrica: **TSDF/ESDF** (`nvblox` si tienes GPU NVIDIA, `Voxblox` como clásico) u **octrees** (`OctoMap`). El ESDF es especialmente útil porque da directamente distancia al obstáculo más cercano, que es lo que quiere un planificador.

Compromiso práctico: 2.5D + una capa de "altura libre" suele bastar y cuesta mucho menos.

📚 [nvblox](https://github.com/nvidia-isaac/nvblox) · [OctoMap](https://github.com/OctoMap/octomap)

### 2.3 BEV aprendido — la dirección moderna

En vez de fusionar a mano geometría y semántica, se aprenden directamente *features* en vista de pájaro a partir de las imágenes y el LiDAR, y se predicen conjuntamente elevación y coste. **TerrainNet** y **RoadRunner** (ETH RSL) son las referencias off-road.

Ventaja: capta correlaciones que las reglas no capturan (la apariencia predice la tracción). Desventaja: necesita datos, y es una caja más opaca — argumento débil en defensa, donde la explicabilidad importa. **Postura recomendada en entrevista:** buena dirección a medio plazo, pero no es por donde empiezas si el cliente aún no tiene dataset.

📚 [TerrainNet (arXiv:2303.15771)](https://arxiv.org/abs/2303.15771) · [RoadRunner (arXiv:2402.19341)](https://arxiv.org/abs/2402.19341)

---

## 3. Las tres familias de traversability (esto es el núcleo)

### Familia 1 — Geométrica pura
Reglas sobre el mapa de elevación: si pendiente > X o step > Y o rugosidad > Z, entonces no transitable.

**A favor:** funciona el primer día, cero datos, totalmente interpretable, fácil de certificar y de explicar a un operador militar.
**En contra:** ciega ante vegetación (paraliza el robot en hierba alta), ciega ante terreno blando (te mete en el barro), ciega ante agua.

**Es siempre tu punto de partida y tu red de seguridad.** Nunca lo elimines: mantenlo como capa de veto por debajo de lo aprendido.

### Familia 2 — Semántica supervisada
Segmentar imagen y/o nube en clases (hierba, barro, grava, asfalto, agua, arbusto, tronco, roca, alambrada...) y mapear clase → coste.

**A favor:** resuelve la ambigüedad geométrica, es inspeccionable, se depura bien.
**En contra:** requiere anotación — cara, lenta y con una ontología que hay que acertar a la primera. Y generaliza mal a estaciones, biomas o iluminaciones no vistas.

**Punto de diseño crítico:** las clases deben corresponder a **diferencias de coste de navegación**, no a categorías botánicas. No necesitas distinguir roble de haya; necesitas distinguir "vegetación atravesable" de "vegetación que oculta un obstáculo rígido".

### Familia 3 — Auto-supervisada / propioceptiva ⭐
El robot genera sus propias etiquetas: conduce, mide qué le pasó (vibración del IMU, consumo de los motores, deslizamiento de orugas, si la trayectoria comandada se ejecutó o no) y **proyecta esa señal hacia atrás sobre lo que veía antes de pisar**. Resultado: un modelo que predice, a partir de la imagen/nube, qué tracción y qué vibración va a encontrar.

**Por qué es el argumento estrella para ARX:** tienen cientos de vehículos teleoperados operando en condiciones reales. Cada hora de teleoperación produce etiquetas gratis, y sin ningún cambio en la operación. No hay que esperar a una campaña de anotación de seis meses.

Trabajos que debes poder nombrar:
- **BADGR** (2020, Berkeley) — el fundacional: navegación aprendida desde la experiencia propia, sin mapas ni etiquetas.
- **WayFAST** (2022) — traversabilidad predictiva desde RGB-D supervisada por el seguimiento del propio controlador. Muy práctico.
- **Wild Visual Navigation** (2023, ETH+Oxford) — aprendizaje **online en pocos minutos de campo** usando features de modelos preentrenados. El más impresionante operativamente.
- **V-STRONG** (2024) — modelos fundacionales de visión + aprendizaje contrastivo.
- **Follow the Footprints** (2024) — supervisión a partir de las huellas dejadas por el propio vehículo.

📚 [BADGR](https://arxiv.org/abs/2002.05700) · [WayFAST](https://arxiv.org/abs/2203.12071) · [Wild Visual Navigation](https://arxiv.org/abs/2305.08510) · [V-STRONG](https://arxiv.org/abs/2312.16016)

### Familia 4 (bonus) — Aprender el coste de las demostraciones humanas
**Inverse Reinforcement Learning** sobre trayectorias teleoperadas: en vez de definir el coste a mano, se infiere qué coste hace que las trayectorias del operador humano sean óptimas. El trabajo de referencia reporta −57% de intervenciones frente a baselines geométricos.

De nuevo: ARX tiene exactamente ese dato. Es el segundo argumento que casi nadie les llevará.

📚 [Learning Risk-Aware Costmaps via IRL for Off-Road Navigation (arXiv:2302.00134)](https://arxiv.org/abs/2302.00134)

### La respuesta correcta en entrevista
No es elegir una familia: es **estratificarlas**. Geometría como veto duro y arranque inmediato → semántica supervisada para desambiguar vegetación y agua → propiocepción/IRL para calibrar el coste con la física real del vehículo y adaptarse a terreno nuevo. Con incertidumbre propagada en todas las capas.

---

## 4. Incertidumbre y OOD — donde se demuestra la senioridad

Si solo puedes destacar en una cosa, que sea esta: **poca gente lleva preparado el enlace entre incertidumbre de percepción y comportamiento**.

Herramientas conceptuales:
- **Incertidumbre aleatoria vs epistémica.** La primera es ruido irreducible del sensor; la segunda es ignorancia del modelo (nunca vi esto). Sólo la segunda se reduce con más datos, y sólo la segunda te dice "cuidado, esto es nuevo".
- **Métodos:** ensembles profundos (caro pero fiable), MC-dropout (barato, peor calibrado), **deep evidential learning** (predice los parámetros de una distribución sobre la predicción, en una sola pasada — el más adecuado para embarcado).
- **Calibración:** un modelo con 90% de confianza debe acertar el 90% de las veces. Se mide con reliability diagrams y ECE, y se corrige con temperature scaling.
- **Referencia canónica off-road: EVORA** (MIT ACL, T-RO) — aprende modelos de **tracción con incertidumbre evidencial** y planifica con conciencia de riesgo. Y **STEP** (JPL, equipo NeBula de DARPA SubT) — evaluación estocástica con medidas de riesgo tipo **CVaR** (Conditional Value at Risk), es decir, optimizar contra el peor 10% de los escenarios en vez de contra la media.

**La frase que debes decir:** *"La salida de la percepción no debería ser un coste, sino una distribución sobre el coste. Y el planificador debe optimizar contra un cuantil de esa distribución, no contra la media — porque el coste de equivocarse es asimétrico: un falso positivo te frena, un falso negativo te vuelca."*

📚 [EVORA](https://xiaoyi-cai.github.io/evora/) · [STEP (arXiv:2103.02828)](https://arxiv.org/abs/2103.02828)

---

## 5. Sensores: lo que hay que saber decir de cada uno

| Sensor | Fuerte | Débil off-road | Nota para ARX |
|---|---|---|---|
| **Cámara** | Semántica rica, barata, alta resolución angular | Iluminación, deslumbramiento, polvo, noche; sin escala métrica | Térmica (que GEREON lleva) resuelve noche y detecta personas/motores |
| **LiDAR** | Geometría métrica precisa, funciona de noche | Polvo/lluvia/nieve generan retornos espurios; hierba genera falsos obstáculos; caro; sombra de rango tras un montículo | **Múltiples ecos** (multi-return) es lo que permite ver *a través* de vegetación fina: el primer eco es la hoja, el último el suelo |
| **Radar (4D)** | Atraviesa polvo, humo, niebla y lluvia; da velocidad Doppler directa | Baja resolución angular, mucho clutter en terreno, multipath | Lo piden explícitamente en sus vacantes. En Ucrania (polvo, humo) es decisivo |
| **IMU** | Alta frecuencia, imprescindible para deskewing y para LIO | Deriva | Es también un *sensor de terreno*: el espectro de vibración clasifica superficie |
| **GNSS/RTK** | Referencia global absoluta | **Jamming y spoofing** — asumir que no lo tendrás | Sus vacantes dicen GPS-denied literalmente |
| **Odometría de ruedas/orugas** | Barata, alta frecuencia | Deslizamiento masivo en orugas sobre terreno suelto | Su error *es información*: el slip mide la tracción del terreno |

### Lo que separa a quien ha tocado hardware
- **Calibración extrínseca e intrínseca.** LiDAR↔cámara con método *targetless* (`direct_visual_lidar_calibration` de Koide es la primera opción a probar; las herramientas de TIER IV/Autoware como alternativa completa). En un vehículo de orugas la calibración **se degrada por vibración**: hay que monitorizar la deriva y considerar autocalibración online.
- **Sincronización temporal.** PTP o trigger hardware. Distingue entre el timestamp del sensor, el de recepción del driver y el de publicación en DDS — confundirlos produce errores de fusión que parecen errores de modelo.
- **Motion compensation / deskewing.** Un LiDAR rotativo tarda ~100 ms en un barrido. A 15 km/h el vehículo se mueve ~40 cm en ese tiempo, y en terreno accidentado además cabecea. Sin deskewing usando la IMU, la nube sale distorsionada y todo lo de arriba se contamina. **Es una de las preguntas técnicas más discriminantes que te pueden hacer.**

📚 [direct_visual_lidar_calibration](https://github.com/koide3/direct_visual_lidar_calibration)

---

## 6. Estimación de estado y GPS-denied

ARX lo pide explícitamente (EKF, UKF, filtros de partículas, **SLAM con factor graphs**, VIO, navegación inercial). Repasa:

- **Filtrado vs smoothing.** EKF/UKF (`robot_localization`) mantienen un estado y son baratos; los **factor graphs** (GTSAM) optimizan sobre una ventana o el historial completo y son más precisos y más robustos a outliers. Que ARX pida factor graphs indica que están en el segundo campo — repásalo bien: variables, factores, marginalización, iSAM2 para actualización incremental.
- **Preintegración de IMU** — el truco que hace viable meter IMU a 200 Hz en un factor graph sin re-integrar en cada iteración.
- **LiDAR-inertial odometry:** **FAST-LIO2** (eficiente, ikd-Tree, muy usado), **LIO-SAM** (factor graph con GTSAM e **integración de GPS como factor** — muy adecuado para campo abierto donde el GNSS va y viene), **KISS-ICP** (sin tuning, excelente como baseline y sanity check).
- **Degeneración geométrica:** en un campo abierto y plano o en un pasillo forestal uniforme, el LiDAR no tiene restricciones suficientes en alguna dirección y la odometría deriva sin avisar. Saber **detectar la degeneración** (número de condición de la matriz de información) y degradar con elegancia es material de senior.
- **GNSS-denied:** detección de spoofing (inconsistencia entre GNSS y odometría), operación en deriva acotada, relocalización contra mapa previo, y decidir *cuándo* dejar de confiar en el GNSS — que es una decisión de arquitectura, no de algoritmo.

📚 [FAST-LIO](https://github.com/hku-mars/FAST_LIO) · [LIO-SAM](https://github.com/TixiaoShan/LIO-SAM) · [KISS-ICP](https://github.com/PRBonn/kiss-icp) · [robot_localization](https://github.com/cra-ros-pkg/robot_localization)

---

## 7. Modelos: qué usarías realmente en un Jetson

- **Segmentación 2D:** SegFormer o DeepLabv3+ como caballos de batalla; **SAM 2 / SAM 3** para pre-etiquetado, no para producción (demasiado pesados y no dan tus clases).
- **Segmentación de nubes:** **SalsaNext** (tiempo real + incertidumbre bayesiana integrada — muy buena elección para embarcado), **RandLA-Net** (eficiente a gran escala), **Cylinder3D** (más preciso, más caro). SPVNAS está archivado: úsalo vía MMDetection3D.
- **Detección 3D:** PointPillars y CenterPoint siguen siendo los desplegables. `OpenPCDet` y `MMDetection3D` como toolboxes.
- **Despliegue:** PyTorch → ONNX → **TensorRT**, cuantización INT8 con calibración, medición de latencia p99 (no la media), y presupuesto de latencia end-to-end. ARX pide TensorRT explícitamente.

---

## 8. Datasets que debes conocer por nombre

- **GOOSE / GOOSE-Ex** ⭐ — *German Outdoor and Offroad Semantic Segmentation*, del **Fraunhofer IOSB y la UniBw München**, contexto Bundeswehr. 10.000 pares imagen+nube etiquetados, **64 clases en 11 grupos**, con **labeling policy publicada**. Es el dataset más cercano al problema exacto de ARX y su ontología se está convirtiendo en estándar de facto en Europa. **Si lees un solo documento de esta lista, que sea su labeling policy** — te da munición directa para la parte de anotación.
- **ORAD-3D** (ICRA 2026) — el mayor dataset off-road actual (~350 GB), con cinco tareas incluidas ocupación 3D y world models. El estado del arte en datos.
- **STONE** (mar-2026) — multimodal **surround-view con radar** y anotación automatizada para traversabilidad 3D. Lo más nuevo, y el único con radar.
- **RELLIS-3D** — el estándar de facto anterior para segmentación 3D off-road (20 clases, contexto militar, Texas A&M).
- **TartanDrive / 2.0** (CMU AirLab) — ~200.000 interacciones de conducción; orientado a aprender **dinámica**, no semántica. Complementario.
- **RUGD**, **Freiburg Forest**, **ORFD**, **CaT** (etiquetado por transitabilidad *según tipo de vehículo* — concepto interesante), **Yamaha-CMU**.

📚 [GOOSE](https://goose-dataset.de/) · [**Labeling policy (PDF)**](https://goose-dataset.de/docs/resources/labeling_policy.pdf) · [Ontología de clases](https://goose-dataset.de/docs/class-definitions/) · [ORAD-3D](https://arxiv.org/abs/2510.16500) · [RELLIS-3D](https://github.com/unmannedlab/RELLIS-3D) · [TartanDrive 2.0](https://theairlab.org/TartanDrive2/)

---

## 9. Autoevaluación (respóndelas en voz alta antes de pasar al Día 3)

1. ¿Por qué un mapa de elevación necesita una capa de varianza y no solo de altura?
2. ¿Qué haces con las celdas no observadas y por qué las dos opciones obvias están mal?
3. Explica cómo generarías etiquetas de transitabilidad sin ningún anotador humano.
4. Un LiDAR de 10 Hz en un vehículo a 15 km/h en terreno accidentado: ¿qué corrección aplicas a la nube y con qué sensor?
5. ¿Cómo detectas que tu odometría LiDAR está degenerando antes de que se note en el mapa?
6. ¿Por qué la incertidumbre epistémica importa más que la aleatoria en terreno no estructurado?
7. Tu robot se para constantemente ante hierba alta. Da tres causas posibles y cómo distinguirlas con datos.
8. ¿Qué le pides al radar que no te pueden dar cámara y LiDAR?
