# Plan de preparación — Senior ML/Autonomy Engineer (Perception & Behavior/Control)

**Contexto:** freelance, 9–12 meses, remoto + 1 día/semana en Múnich, robots móviles autónomos en terreno no estructurado (offroad), ámbito defensa/seguridad.
**Plazo asumido:** menos de 1 semana → plan intensivo de 7 días, ~3–4 h/día.
**Supuesto:** como no indicaste tu punto de partida, cada tema lleva una etiqueta:
`[REFRESCAR]` = probablemente ya lo sabes, repásalo para hablarlo con fluidez · `[PONERSE AL DÍA]` = tecnología concreta que conviene poder nombrar y comparar · `[PROFUNDIZAR]` = aquí es donde se gana o se pierde la entrevista.

Si un bloque ya lo dominas, sáltatelo y reinvierte esas horas en el Día 6 (práctica) y Día 7 (simulacro).

---

## 0. Lectura estratégica de la oferta (léela antes que nada)

Lo que la oferta **dice** y lo que realmente **significa**:

| Frase de la oferta | Lo que están comprando de verdad |
|---|---|
| "Aktuell überwiegend ferngesteuert … sollen deutlich mehr autonome Funktionen erhalten" | No parten de cero pero casi: hay teleoperación funcionando y quieren dar el salto a autonomía. Tu valor está en **el camino de teleop → autonomía asistida → autonomía supervisada**, no en un stack perfecto. |
| "Anders als klassisches autonomes Fahren auf Straßen" | Te van a preguntar explícitamente **por qué no sirve el playbook de coche autónomo**. Ten la respuesta preparada (sección 2). |
| "nicht nur umsetzt, sondern das Team fachlich voranbringt" | Es un puesto de **lead técnico encubierto**. La mitad de la evaluación será: ¿sabe decidir, priorizar, documentar y enseñar? |
| "Aufbau, Organisation und QS von Annotation-Prozessen" | Punto sorprendentemente destacado. Significa que **no tienen dataset propio maduro**. Es un dolor real y actual. Prepárate a fondo (Día 6). |
| "Simulationsumgebungen zur Validierung vor dem Feldeinsatz" | Poco acceso a hardware / campo caro y logísticamente difícil (más aún en defensa). La simulación no es un juguete: es su único ciclo de iteración rápido. |
| "Defense-/Sicherheitsumfeld" | Implicaciones en datos (no se pueden subir a un labeling provider cualquiera), en compute (on-prem/edge), en comms (enlaces degradados/jammed) y en tu propio estatus (Sicherheitsüberprüfung). |
| "software-definiert" | Esperan que hables de arquitectura modular, CI/CD para robots, OTA, versionado, observabilidad — no solo de modelos. |

**Hipótesis sobre el cliente (útil, no la afirmes como hecho):** el perfil encaja mucho con el ecosistema de UGV de defensa del área de Múnich — ARX Robotics es el nombre más obvio (UGV modulares "software-defined", Múnich, expansión de producción, alianza con Helsing), pero también podría ser un tier-1 clásico (Rheinmetall/KNDS) o un spin-off. Mira sus webs y notas de prensa antes de la entrevista y menciona algo concreto de su producto: en freelancing eso desnivela la conversación.

---

## 1. Matriz de prioridades (qué estudiar si solo tienes X horas)

**Si solo tuvieras 6 horas, estudia esto y nada más:**

1. Traversability estimation offroad (geométrica + semántica + auto-supervisada) — es *el* tema del puesto.
2. Diseño de un pipeline de labeling de datos multimodales con QA, en entorno donde no puedes externalizar los datos.
3. Estrategia de validación en simulación: qué se puede validar en sim, qué no, y cómo lo mides.
4. Tu narrativa senior: 3 historias STAR donde tomaste decisiones de arquitectura y subiste el nivel de un equipo.

**Prioridad alta (must-have de la oferta):** ROS2 · sensores cámara/LiDAR/radar y series temporales · Python (C++ como plus) · al menos un simulador con criterio.
**Prioridad media:** PyTorch, behavior trees / planners, MLOps de robótica.
**Prioridad baja pero rentable:** vocabulario técnico en alemán, aspectos de defensa (STANAG, Sicherheitsüberprüfung), condiciones de freelance.

---

## 2. Día 1 — Estrategia, narrativa y el argumento "offroad ≠ carretera"

**Objetivo del día:** que tengas un discurso propio antes de meterte en tecnología.

### 2.1 Prepara el argumento central `[PROFUNDIZAR]`
Van a preguntarte, casi seguro: *"¿Qué cambia respecto al conducción autónoma en carretera?"*. Estructura tu respuesta en cinco ejes:

1. **No hay estructura previa.** Sin carriles, sin señales, sin mapas HD, sin OpenDRIVE. El "mapa" es el terreno mismo. Consecuencia: se pasa de *detección de objetos* a *estimación de transitabilidad (traversability)* como representación primaria.
2. **La geometría no basta.** Un matorral alto y una roca tienen la misma firma geométrica en una nube de puntos, pero uno se atropella y el otro te rompe el vehículo. Requiere semántica y/o propiedades físicas (compliance del terreno). Y al revés: la hierba alta genera falsos obstáculos que paralizan el robot.
3. **Obstáculos negativos y el suelo como riesgo.** Zanjas, socavones, pendientes, terreno blando (barro, arena), cornisas. La pregunta no es "¿hay algo delante?" sino "¿puedo poner las orugas ahí y salir?".
4. **Percepción degradada.** Polvo, humo, lluvia, nieve, vegetación que ocluye, vibración fuerte, GNSS denegado o jammed. Esto empuja hacia radar 4D, LiDAR con múltiples ecos, e state estimation robusta sin GPS.
5. **La verdad de terreno es cara y escasa.** No existe el equivalente a millones de km de flota. De ahí la centralidad de simulación + datos sintéticos + labeling propio (y por qué esa tarea está en la oferta).

Y un sexto eje que casi nadie menciona y que te distingue: **el modelo de operación**. Vienen de teleoperación. Eso significa que la autonomía debe diseñarse como un *continuo* — teleop directa → teleop asistida (obstacle avoidance, speed limiting) → waypoint following → autonomía supervisada — con transferencia de control limpia, comportamiento definido ante pérdida de enlace, y siempre un humano en el bucle de decisión en contexto defensa.

### 2.2 Prepara tus historias `[PROFUNDIZAR]`
Escribe (literalmente, en un fichero) 4 historias en formato **STAR**, de 2 minutos cada una:

- Una decisión de **arquitectura** que tomaste, con las alternativas que descartaste y por qué (esto es lo que evalúan de "senior").
- Un caso en que **subiste el nivel del equipo**: introdujiste una práctica, hiciste mentoring, documentaste algo que se adoptó.
- Un fallo en **campo/producción** que diagnosticaste, con el ciclo dato → hipótesis → fix → validación.
- Un proyecto donde montaste **infraestructura de datos o evaluación** desde cero.

Regla: en cada una, incluye un número (latencia, tamaño de dataset, % de mejora, semanas ahorradas) y una decisión que hoy tomarías distinta. Lo segundo es lo que suena verdaderamente senior.

### 2.3 Investiga al cliente (30 min)
Web, notas de prensa, LinkedIn de su equipo de ingeniería, ofertas de empleo abiertas suyas (delatan el stack: si buscan "ROS2 + Rust" o "Isaac Sim", ya lo sabes). Anota 2 preguntas concretas sobre su producto.

---

## 3. Día 2 — Percepción offroad (el bloque grande)

### 3.1 Representaciones del entorno `[PROFUNDIZAR]`
- **Elevation maps / 2.5D grid maps**: `grid_map` (ETH Zurich) y `elevation_mapping` / `elevation_mapping_cupy` — el estándar de facto en robótica de campo. Métricas derivadas: pendiente, step height, rugosidad (roughness), curvatura, varianza de altura.
- **Costmaps de transitabilidad**: cómo se fusionan capas geométricas y semánticas en un coste continuo, y cómo se propaga la **incertidumbre** (celdas no observadas ≠ celdas libres — error clásico y letal offroad).
- **Voxel / TSDF / ESDF**: Voxblox, nvblox (NVIDIA, acelerado en Jetson), OctoMap. Cuándo hace falta 3D real (vegetación con dosel, túneles, salientes) frente a 2.5D.
- **BEV (bird's-eye view) learned representations**: pasar de fusión artesanal a features BEV aprendidas (línea BEVFusion / LSS). Es la dirección moderna y suena bien mencionarla como opción con criterio (necesita muchos datos → tal vez no sea su primer paso).

### 3.2 Traversability learning `[PROFUNDIZAR]`
Ordena mentalmente tres familias y sé capaz de recomendar una para su caso:

1. **Geométrica pura** (reglas sobre elevation map). Barata, interpretable, funciona el día 1, sin datos. Falla con vegetación y terreno blando.
2. **Semántica supervisada** (segmentación de imagen y/o nube → clases: hierba, barro, grava, asfalto, agua, arbusto, tronco, roca) → mapeo clase→coste. Necesita labeling: aquí conecta directamente con la tarea 3 de la oferta.
3. **Auto-supervisada / propioceptiva**: el robot aprende de su propia experiencia (vibración IMU, consumo de motores, slip de orugas, éxito/fracaso de trayectorias) y proyecta esa señal retroactivamente sobre lo que veía. Palabras clave: WayFAST, BADGR, ScaTE, "self-supervised traversability", "learning from proprioception". **Este es el argumento estrella para un cliente sin dataset**: genera etiquetas gratis mientras teleoperan. De hecho: *cada hora de teleoperación que ya están haciendo es un dataset de demostraciones humanas que probablemente no estén explotando*. Dilo en la entrevista.

También: aprendizaje de coste a partir de **demostraciones de teleoperación** (IRL / imitation) — muy encajado con su situación.

### 3.3 Datasets y benchmarks offroad `[PONERSE AL DÍA]`
Debes poder nombrarlos:
- **GOOSE / GOOSE-Ex** (German Outdoor and Offroad Dataset, del Fraunhofer IOSB, contexto Bundeswehr) — **el más relevante para esta entrevista**: alemán, offroad, multimodal, ontología pensada para vehículos militares. Mencionarlo demuestra que conoces su nicho exacto.
- **RELLIS-3D** (Texas A&M, LiDAR + cámara + pose, offroad militar), **RUGD**, **Freiburg Forest**, **ORFD**, **CaT**, **TartanDrive / TartanDrive 2.0** (CMU AirLab, dinámica offroad a alta velocidad).
- Para comparación on-road: nuScenes, SemanticKITTI, Waymo — útiles como referencia de escala y de ontología.

Dedica 45 min a mirar la ontología de clases de GOOSE. Te dará munición concretísima para la parte de labeling.

### 3.4 Modelos y sensores `[REFRESCAR]`
- **Segmentación 2D**: DeepLabv3+, SegFormer, Mask2Former; SAM/SAM2 como pre-etiquetador, no como modelo de producción.
- **Nubes de puntos**: PointNet++, RandLA-Net, SalsaNext, Cylinder3D, SPVNAS/MinkowskiEngine (sparse convs); detección 3D: PointPillars, CenterPoint (rápidos, desplegables en Jetson).
- **Fusión**: early / mid (feature-level, BEV) / late. Cuándo cada una y qué implica en latencia y en robustez ante fallo de un sensor (degradación elegante: si la cámara se ciega por polvo, ¿el sistema para o sigue con LiDAR+radar en modo conservador?).
- **Calibración y sincronización** `[PROFUNDIZAR — se pregunta mucho y filtra a los que no han tocado hardware]`: intrínsecos/extrínsecos, calibración LiDAR-cámara (target-based vs targetless), sincronización temporal (PTP, hardware trigger, timestamps de DDS vs del sensor), **motion compensation / deskewing** de la nube de puntos en vehículo que se mueve por terreno accidentado, y cómo la calibración se degrada por vibración → autocalibración online / monitorización de deriva.
- **Radar** `[PONERSE AL DÍA si vienes de cámara/LiDAR]`: FMCW, rango-doppler-ángulo, radar imaging 4D, penetración de polvo/humo/lluvia, baja resolución angular, clutter en terreno. Conocer sus límites reales importa más que los detalles de procesado.
- **Series temporales / state estimation**: fusión IMU+odometría+GNSS/RTK, EKF/UKF (`robot_localization`), preintegración de IMU, LiDAR-inertial odometry (**FAST-LIO2**, LIO-SAM, KISS-ICP), operación **GNSS-denied** (crítico en defensa: jamming/spoofing), detección de deriva y de slip en orugas.

### 3.5 Incertidumbre y OOD `[PROFUNDIZAR — muy senior, poca gente lo trae]`
En terreno no estructurado la clase "nunca visto" es la norma. Prepárate a hablar de: calibración de confianza, ensembles / MC-dropout, evidential deep learning, detección de out-of-distribution, y sobre todo **qué hace el sistema cuando la percepción no está segura** (reducir velocidad, ampliar margen, pedir confirmación al teleoperador, detenerse). Ese enlace percepción→comportamiento es exactamente la intersección de los dos roles del título.

---

## 4. Día 3 — ROS2 y arquitectura del stack

### 4.1 ROS2 de nivel senior `[REFRESCAR + PONERSE AL DÍA]`
No repases tutoriales de publisher/subscriber. Repasa lo que se pregunta a un senior:

- **Distros actuales (2026):** Jazzy Jalisco (LTS, mayo 2024, hasta 2029) es lo que verás en producción; Kilted Kaiju (mayo 2025, no-LTS); **Lyrical Luth (mayo 2026)** es la nueva LTS. Pregunta en la entrevista en cuál están y si tienen plan de migración — es una pregunta de senior.
- **DDS y middleware**: Fast DDS vs Cyclone DDS; **rmw_zenoh**, que ha ganado tracción como RMW alternativo y es especialmente relevante para enlaces inalámbricos con pérdidas y comunicación robot↔estación de teleoperación (justo su caso). Descubrimiento, ROS_DOMAIN_ID, problemas de discovery en redes de campo.
- **QoS**: reliable vs best-effort, durability transient_local, deadline, liveliness, lifespan. Saber elegir el perfil para nubes de LiDAR a 10 Hz vs comandos de control vs telemetría por radio degradada.
- **Ejecución y rendimiento**: executors single/multi-threaded, callback groups, composición en un solo proceso, **intra-process comms y zero-copy** (loaned messages, shared memory) para no copiar nubes de puntos; presupuesto de latencia end-to-end sensor→actuador.
- **Lifecycle nodes** y gestión de arranque/degradación; `tf2` (árboles de transformadas, `base_link`/`odom`/`map`, extrapolación, buffer); `ros2_control` (hardware interfaces, controller manager) para plataformas con orugas.
- **rosbag2 + MCAP**: grabación selectiva en campo, tamaño, particionado, replay determinista. Es la base de todo lo demás (datos, sim, regresión).
- **SROS2 / seguridad**: autenticación, cifrado DDS. En defensa, esto se pregunta.
- **Real-time**: qué es realista en ROS2, dónde poner el control duro (a menudo fuera de ROS, en MCU/PLC), watchdogs.

### 4.2 Arquitectura de un stack de autonomía `[PROFUNDIZAR]`
Ten preparada una **arquitectura de referencia que puedas dibujar en 3 minutos** (practícala en papel):

```
Sensores → Drivers/Sync → State Estimation ─┐
                                            ├→ Mapa local (elevation + semantics + traversability)
Percepción (2D/3D, det+seg) ────────────────┘         │
                                                      ▼
                                          Behavior / Mission layer (BT)
                                                      │
                                          Global planner → Local planner (MPPI/MPC)
                                                      │
                                          Controller → ros2_control → Plataforma
                                                      │
                     Safety monitor (independiente, e-stop, geofence, watchdog de enlace)
                     Teleop / HMI ←→ Shared autonomy (transferencia de control)
                     Logging & observabilidad → data flywheel
```

Puntos a defender: por qué **modular y no end-to-end** en este dominio (certificabilidad, depuración, datos escasos, defensa exige explicabilidad); dónde meterías aprendizaje y dónde no; **el safety monitor como componente independiente y simple**, no como parte del modelo.

- **Cómputo embebido** `[PONERSE AL DÍA]`: NVIDIA Jetson AGX Orin / Thor, TensorRT, cuantización INT8, Isaac ROS (paquetes acelerados, NITROS para evitar copias entre GPU y CPU). Presupuesto de potencia y térmico en vehículo — en defensa además firma térmica y consumo importan de verdad.
- **DevOps de robótica**: Docker/contenedores para ROS2, colcon, CI que corre tests y sim en PR, despliegue OTA a flota, feature flags, versionado de modelos y de mapas, **Foxglove** (visualización y depuración de bags — casi estándar hoy) y **Rerun** como alternativa moderna.

---

## 5. Día 4 — Behavior y Control

### 5.1 Capa de comportamiento `[PROFUNDIZAR]`
- **Behavior Trees**: BehaviorTree.CPP v4, Groot2 para visualización, el BT Navigator de Nav2. Ten claro **por qué BT y no FSM** (composabilidad, reactividad, legibilidad para no-expertos, reutilización de subárboles) y también sus límites (estado compartido, blackboards que se convierten en variables globales).
- **Nav2**: costmap_2d y sus capas (obstacle, inflation, voxel, y capas custom — que es donde metes tu traversability), planner/controller/behavior servers como plugins, recovery behaviors, lifecycle. Aunque Nav2 está pensado para interiores/estructurado, es el punto de partida de casi todo el mundo y debes saber **qué partes sirven offroad y cuáles hay que sustituir** (respuesta corta: el framework y los plugins sí; el modelo de costmap binario 2D y los supuestos de suelo plano, no).
- **Máquina de modos operacionales**: manual / teleop asistida / waypoints / autónomo supervisado; degradación ante pérdida de enlace (¿parar? ¿continuar a último waypoint? ¿volver por la ruta grabada — "breadcrumb return"?). Esto en su producto es una decisión de diseño real y candente.

### 5.2 Planificación `[REFRESCAR]`
- Global: A*, D* Lite / Field D* (replanificación en mapas cambiantes), Hybrid A* (kinodinámico, con restricciones no holonómicas), planificación sobre costmaps continuos de transitabilidad, planificación 3D en terreno con pendiente.
- Local: **MPPI** (Model Predictive Path Integral — es el controlador moderno de Nav2 y el más adecuado offroad porque maneja dinámicas no lineales y costes no diferenciables), DWB/DWA, TEB. Sampling-based: RRT*, kinodynamic RRT.
- Costes: no solo distancia — riesgo de vuelco, slip esperado, consumo, exposición/visibilidad (¡en defensa, planificar minimizando exposición es un requisito real!), incertidumbre del mapa.

### 5.3 Control `[REFRESCAR]`
- Cinemática **skid-steer / tracked**: no holonómica, con deslizamiento inherente; por qué los modelos de bicicleta/differential-drive ideales fallan y cómo se compensa (identificación de parámetros de slip, modelos aprendidos de dinámica).
- Pure Pursuit / Regulated Pure Pursuit, Stanley, MPC (lineal vs no lineal), control adaptativo al terreno (limitar velocidad según pendiente/rugosidad/estimación de tracción).
- Nociones de **terramecánica** (Bekker/Wong, presión de contacto, sinkage): no necesitas dominarlas, pero nombrarlas te sitúa en el mundo offroad.
- Estabilidad: márgenes de vuelco (static/dynamic stability margin), centro de masas, pendiente máxima lateral.

### 5.4 Aprendizaje en behavior/control `[PONERSE AL DÍA]`
RL (y por qué sim2real es duro en dinámica de terreno), imitation learning desde teleoperación (ventaja: **ya tienen los datos**), aprendizaje de modelos de dinámica para MPC, hybrid/residual control (control clásico + corrección aprendida) — que suele ser la respuesta pragmática y la que un cliente quiere oír.

---

## 6. Día 5 — Simulación y validación

### 6.1 Panorama de simuladores `[PONERSE AL DÍA — es must-have de la oferta]`
Debes poder **comparar con criterio**, no solo nombrar. Elige uno como "el que dominas" y ten opinión sobre los demás.

| Herramienta | Fuerte en | Débil en | Encaje offroad/defensa |
|---|---|---|---|
| **NVIDIA Isaac Sim 5.x / Isaac Lab** | Renderizado RTX, sensores físicamente plausibles (RTX LiDAR, radar), USD/Omniverse, Replicator para datos sintéticos, integración ROS2, RL a escala | Curva de aprendizaje, exige GPU potente, terreno deformable limitado | **La apuesta más probable hoy**; open-source desde 5.0 |
| **Unreal Engine 5** | Fidelidad visual, terreno enorme (Landscape, Nanite), Cesium para datos geoespaciales reales | Física de vehículo no es su fuerte, hay que construir el puente a ROS2 | Muy usado en defensa por realismo visual y entrenamiento |
| **CARLA** | Maduro, scenario runner, OpenSCENARIO | Diseñado para **carretera**; offroad es forzarlo | Útil como referencia metodológica, no como plataforma |
| **Gazebo (Harmonic/Ionic)** | Nativo ROS2, ligero, CI-friendly, plugins de terreno | Fidelidad de sensores y visual limitada | Ideal para **tests de regresión en CI**, no para percepción fotorrealista |
| **MORAI, Foretellix** | Verificación basada en escenarios, **coverage-driven**, generación masiva de variantes | Comerciales, orientados a automoción | Foretellix aporta la *metodología* de verificación que a ellos les falta |
| **Chrono / Chrono::Vehicle** | Terramecánica real, terreno deformable, orugas | No es un simulador de percepción | La referencia si quieren validar movilidad en barro/arena |

Nota clave para la entrevista: **la respuesta correcta casi nunca es "un simulador"**, sino una **pila**: Gazebo/headless para regresión rápida en CI, Isaac Sim o UE5 para percepción y datos sintéticos, Chrono si la movilidad sobre terreno blando es el riesgo, y **replay de rosbags reales** como el test más valioso de todos.

### 6.2 Metodología de validación `[PROFUNDIZAR — aquí demuestras senioridad]`
- **Pirámide de test**: unit → component (nodo con datos grabados) → **replay/open-loop sobre bags reales** → closed-loop en sim → SIL/HIL → campo restringido → operación.
- **Verificación basada en escenarios**: parametrizar escenarios (pendiente, vegetación, iluminación, meteorología, tipo de obstáculo) y hacer **barridos**; medir *cobertura* del espacio de escenarios, no "pasa/no pasa" de un demo. Vocabulario: OpenSCENARIO 2 / M-SDL, coverage-driven verification, fuzzing de escenarios, búsqueda de casos límite dirigida.
- **Métricas de autonomía** (ten una lista propia): intervenciones por km, tiempo hasta intervención, tasa de éxito de misión, distancia mínima a obstáculo, aceleraciones laterales / margen de vuelco, coste de trayectoria vs óptimo, latencia percepción→actuación, tasas de falso positivo/negativo del traversability *ponderadas por consecuencia* (un falso negativo que te mete en una zanja no vale lo mismo que un falso positivo que te frena de más).
- **El sim2real gap**: dónde está realmente (modelos de sensor y ruido, dinámica de contacto suelo-oruga, apariencia de la vegetación) y cómo se mide (validación cruzada sim vs bag real en las mismas trayectorias, domain randomization, calibración del modelo de sensor contra datos reales).
- **Datos sintéticos**: generación con Replicator/Omniverse para clases raras (obstáculos negativos, alambradas, cráteres), domain randomization, y su límite honesto — funcionan mejor para geometría/LiDAR que para apariencia fotométrica.

---

## 7. Día 6 — Datos, labeling y práctica

### 7.1 Diseño de un pipeline de anotación `[PROFUNDIZAR — es la tarea más explícita y menos común de la oferta]`
Prepara una respuesta estructurada de 5 minutos, porque casi seguro te preguntan *"¿cómo montarías esto desde cero?"*. Esqueleto:

1. **Ingesta**: rosbag2/MCAP desde campo → almacenamiento con metadatos (vehículo, sesión, sensores, ubicación, meteo, versión de software, calibración vigente). Sin esta metadata, el dataset es inútil a los 6 meses.
2. **Curación / selección** (el paso que todo el mundo se salta): no anotas todo, anotas lo que aporta. Muestreo por diversidad de embeddings, deduplicación, **active learning** (anotar donde el modelo tiene más incertidumbre o discrepa con el consenso), minería de casos límite a partir de intervenciones del teleoperador (¡señal gratis: cada vez que un operador toma el control es una etiqueta de "aquí el sistema no supo"!). Herramientas: **FiftyOne (Voxel51)**.
3. **Ontología / label schema**: la decisión más cara de revertir. Diseñarla con los ingenieros de behavior — las clases deben corresponder a *diferencias de coste de navegación*, no a categorías botánicas. Mira GOOSE como punto de partida en vez de inventarla. Prever atributos (altura de vegetación, humedad, densidad) y una clase "unknown/other" bien definida.
4. **Herramientas**: **CVAT** y **Label Studio** (open source, self-hosted — importante en defensa), **SUSTechPOINTS** (nubes de puntos, ligero), y comerciales tipo Segments.ai, Kognic, Encord, Scale, Deepen si se permitiera externalizar. **En contexto defensa, el criterio decisivo suele ser que la herramienta sea on-premise y los anotadores estén autorizados** — dilo, demuestra que entiendes su restricción real.
5. **Pre-etiquetado / auto-labeling**: modelo existente + SAM2 para máscaras + propagación temporal entre frames + proyección 3D↔2D entre LiDAR y cámara (etiqueta una vez, propaga a ambos dominios). Reduce coste 3–10×; el humano corrige, no dibuja desde cero.
6. **Aseguramiento de calidad (esto es lo que piden literalmente)**: guía de anotación versionada con ejemplos y casos límite; **golden set** de referencia; acuerdo inter-anotador (Cohen's/Fleiss' kappa, mIoU entre anotadores); revisión por muestreo estadístico con umbral de aceptación; ciclo de feedback al anotador; métricas de coste y throughput; auditoría periódica de la propia guía (los desacuerdos recurrentes indican una ontología mal definida, no anotadores malos).
7. **Versionado y trazabilidad**: DVC / LakeFS / dataset registry, splits congelados, evitar fugas train/test (¡en robótica la fuga clásica es partir por frame y no por sesión/ubicación!), enlazar cada modelo entrenado con su dataset exacto.
8. **Cierre del bucle**: métricas de modelo → identificar clases débiles → dirigir la siguiente ronda de recogida y anotación. El "data flywheel".

### 7.2 Práctica manos a la obra (2–3 h, elige UNA)
Elige la que más lejos te quede de tu experiencia. El objetivo no es un producto, es poder decir "lo hice esta semana":

- **Opción A (percepción):** descarga una secuencia de RELLIS-3D o GOOSE, calcula un elevation map con `grid_map`, deriva pendiente/rugosidad, y superpón una segmentación semántica sencilla para producir un costmap de transitabilidad. Haz una captura de pantalla.
- **Opción B (simulación):** instala Isaac Sim 5.x, carga un terreno con relieve, añade un RTX LiDAR + cámara, publica por el ROS2 bridge y visualiza en Foxglove/RViz. Anota los problemas que encontraste — contarlos es más creíble que decir "tengo experiencia".
- **Opción C (behavior):** monta Nav2 con el controlador MPPI en un mundo con terreno irregular en Gazebo, añade una **capa de costmap propia** alimentada por rugosidad. Es la demo que más directamente mapea a "Perception & Behavior/Control".

Sube lo que salga a un repo privado o ten las capturas a mano para compartir pantalla.

---

## 8. Día 7 — Simulacro, preguntas y logística

### 8.1 Preguntas probables (prepara respuestas habladas, en voz alta, cronometradas)

**Técnicas de dominio**
1. ¿Cómo estimarías transitabilidad en un bosque con hierba alta y suelo irregular? *(Respuesta: híbrida geométrica+semántica+propioceptiva, con incertidumbre explícita.)*
2. ¿Cómo detectas obstáculos negativos (zanjas) con LiDAR montado bajo? *(Sombras de rango, ausencia de retorno donde el modelo de suelo predice retorno, estéreo, tratar lo no observado como no transitable.)*
3. Tu robot se para constantemente ante hierba alta. ¿Cómo lo diagnosticas y arreglas? *(Muy probable: es su dolor real. Diagnóstico por datos, no por intuición.)*
4. ¿Cómo mantienes la localización cuando pierdes GNSS 20 minutos? *(LIO, deriva, cierre de bucle, mapas previos, fusión con odometría de orugas con modelo de slip.)*
5. Cámara, LiDAR y radar: ¿cómo los fusionas y qué pasa si uno falla?
6. ¿Cómo pasas de teleoperación a autonomía sin romper la confianza del operador? *(Autonomía incremental, transparencia de intención, transferencia de control, modos degradados.)*
7. ¿End-to-end o modular? *(Ten opinión, con matices y con condiciones bajo las que cambiarías de idea.)*

**De proceso y senioridad**
8. Llegas y el equipo tiene teleop funcionando. ¿Cuáles son tus primeros 30/60/90 días? — **prepara esta con especial cuidado, es la pregunta que decide contrataciones de freelance senior.**
9. ¿Cómo montarías el proceso de anotación con datos que no pueden salir de la empresa?
10. ¿Cómo convences al equipo de una decisión de arquitectura con la que no están de acuerdo?
11. ¿Cómo aseguras transferencia de conocimiento sabiendo que te vas en 12 meses? *(Documentación, pairing, ADRs, tests como especificación, no dejar componentes de los que solo tú sabes.)*
12. ¿Qué validarías en simulación y qué te negarías a validar solo en simulación?

**Borrador de respuesta a la 8 (adáptalo):**
- *Días 1–30:* escuchar y medir. Auditar el stack actual, la calidad y volumen de bags existentes, la infraestructura de calibración/sincronización, y **grabar sistemáticamente sesiones de teleoperación** (aún sin anotar). Entregable: un documento de arquitectura y riesgos + un baseline de métricas. Y una victoria rápida visible (p. ej., asistencia de obstáculos en teleop, que reduce carga del operador sin prometer autonomía).
- *Días 31–60:* pipeline de datos + banco de simulación mínimo + primer traversability geométrico en el vehículo, con métricas y test de regresión automatizados.
- *Días 61–90:* capa semántica entrenada con el primer dataset anotado, integración con planificación local, primeras misiones de waypoints supervisadas en campo restringido, y la metodología documentada y transferida.

### 8.2 Preguntas que **tú** debes hacer (te evalúan también por esto)
- ¿En qué distro de ROS2 estáis y quién es dueño de la arquitectura del stack hoy?
- ¿Qué volumen de datos de campo tenéis grabados y en qué formato/con qué metadata?
- ¿Los datos pueden salir de la empresa? ¿Hay anotadores internos o hay que crear la función?
- ¿Qué acceso tendré a hardware real y con qué cadencia hay ventanas de test en campo?
- ¿Cuál es el criterio de éxito del proyecto a 12 meses, medido en algo concreto?
- ¿Qué grado de autonomía es aceptable para vuestro cliente final — supervisada siempre, o hay ambición de mayor independencia? ¿Qué restricciones de human-in-the-loop imponen?
- ¿Existe un requisito de habilitación de seguridad (Sicherheitsüberprüfung) para este rol?
- ¿Cómo se toman las decisiones técnicas hoy — quién dice la última palabra?

### 8.3 Lo no técnico (no lo dejes para el final real) `[PONERSE AL DÍA]`
- **Alemán técnico**: la oferta pide "Deutsch und Englisch". Aunque la parte técnica vaya en inglés, prepara 5 minutos de autopresentación en alemán y el vocabulario clave: *Umfelderfassung, Hinderniserkennung, Befahrbarkeit, Geländeoberfläche, Regelung vs Steuerung, Sensordatenfusion, Zustandsschätzung, Bahnplanung, Ausweichmanöver, Simulationsumgebung, Datenannotation, Qualitätssicherung, Wissenstransfer*. La distinción **Regelung (control en lazo cerrado) vs Steuerung (mando en lazo abierto)** es la que delata a quien no ha trabajado técnicamente en alemán.
- **Defensa**: sensibilidad al contexto (human-in-the-loop, marco ético y legal, que la UE AI Act excluye lo militar pero los clientes tienen sus propias exigencias), **Sicherheitsüberprüfung (Ü1/Ü2/Ü3)** y qué implica para un autónomo, control de exportación (dual-use, ITAR si hay componentes US), interoperabilidad NATO (STANAG). No hace falta profundidad; hace falta que no te pille de sorpresa.
- **Freelance en Alemania**: ten claro tu **tarifa diaria** y defiéndela sin titubeos (para un perfil senior de autonomía/ML en defensa en el mercado alemán, el rango habitual está en la banda alta de consultoría técnica — investiga tarifas actuales antes, en Freelancermap/GULP, y ten una cifra y un mínimo). Prepárate además para: riesgo de **Scheinselbständigkeit** (jornada completa 9–12 meses con un solo cliente y presencia semanal es exactamente el patrón que la Deutsche Rentenversicherung mira con lupa — conviene poder hablar de ello con naturalidad: contrato de obra/servicio bien redactado, sin integración en jerarquía, otros clientes o al menos capacidad de tenerlos), propiedad intelectual, responsabilidad, y logística del día presencial en Múnich (¿gastos incluidos?).

### 8.4 Checklist de las últimas 24 horas
- [ ] Arquitectura de referencia dibujada de memoria en 3 minutos.
- [ ] 4 historias STAR con números, dichas en voz alta.
- [ ] Respuesta 30/60/90 fluida.
- [ ] Argumento "offroad ≠ carretera" en 5 ejes.
- [ ] 3 nombres que demuestran nicho: GOOSE, traversability auto-supervisada, MPPI.
- [ ] Demo/captura de la práctica del Día 6 lista para compartir pantalla.
- [ ] 8 preguntas tuyas escritas.
- [ ] Tarifa diaria y disponibilidad decididas.
- [ ] Autopresentación de 2 min en alemán ensayada.
- [ ] 2 datos concretos sobre el producto del cliente.

---

## 9. Tres cosas que te van a diferenciar

Si solo recuerdas tres ideas de todo este documento, que sean estas — son las que un candidato medio no dirá:

1. **"Vuestra teleoperación ya es vuestro dataset."** Cada sesión teleoperada contiene demostraciones humanas, trayectorias etiquetadas implícitamente como transitables, y cada intervención marca un caso límite. Empezar por explotar eso da resultados antes que cualquier campaña de anotación.
2. **"El objetivo no es detectar objetos, es estimar transitabilidad con incertidumbre, y que el comportamiento reaccione a esa incertidumbre."** Une los dos lados del título del puesto en una sola frase.
3. **"Validar autonomía es un problema de cobertura de escenarios, no de demos."** Ofrecer una metodología medible de validación es lo que un cliente que va a llevar robots a campo real necesita, y casi nadie se lo propone.

---

## Fuentes consultadas para actualizar versiones y estado del arte

- [ROS 2 Releases — Lyrical Luth (mayo 2026)](https://docs.ros.org/en/kilted/Releases/Release-Lyrical-Luth.html) · [Kilted Kaiju](https://docs.ros.org/en/jazzy/Releases/Release-Kilted-Kaiju.html) · [ROS 2 EOL dates](https://endoflife.date/ros-2)
- [NVIDIA Isaac Sim 5.0 e Isaac Lab 2.2 — disponibilidad general](https://developer.nvidia.com/blog/isaac-sim-and-isaac-lab-are-now-available-for-early-developer-preview/) · [Isaac Sim release notes](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/overview/release_notes.html)
- [A Review of Learning Off-Road Terrain Traversability for AGVs (ASME)](https://asmedigitalcollection.asme.org/autonomousvehicles/article/6/2/020801/1229986/A-Review-of-Learning-Off-Road-Terrain) · [Advances and Trends in Terrain Classification for Off-Road Perception (J. Field Robotics)](https://onlinelibrary.wiley.com/doi/10.1002/rob.22586) · [Learning-based Traversability Costmap (arXiv)](https://arxiv.org/html/2406.08187v2) · [CMU AirLab — Autonomous Off-road driving](https://theairlab.org/offroad/)
- [Best LiDAR Annotation Platforms 2026 (Kognic)](https://www.kognic.com/articles/best-lidar-annotation-platforms-2026) · [Point cloud labeling tools 2026 (Segments.ai)](https://segments.ai/blog/the-8-best-point-cloud-labeling-tools/)
- [ARX Robotics — UGV Hector y expansión en Múnich](https://www.arx-robotics.com/news) · [ARX Robotics abre la mayor planta de robótica de defensa de Europa](https://www.arx-robotics.com/article/arx-robotics-opens-europes-largest-production-facility)
