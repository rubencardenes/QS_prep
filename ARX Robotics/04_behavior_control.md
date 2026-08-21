# Dossier 3 — Behavior y Control

*ARX pide literalmente: behavior trees / máquinas de estado, occupancy grids, cost maps, planners global y local.*

---

## 1. Capa de comportamiento

### 1.1 Behavior Trees vs máquinas de estado

Una FSM define transiciones entre estados: con N estados tienes hasta N² transiciones, y cada estado nuevo obliga a revisar las transiciones existentes. Un **Behavior Tree** invierte el control: los nodos padre (secuencia, fallback/selector, paralelo, decoradores) *tickean* a los hijos y estos devuelven `SUCCESS`, `FAILURE` o `RUNNING`. La reactividad emerge del tick periódico desde la raíz.

**Ventajas reales:** composabilidad (un subárbol es reutilizable), reactividad natural (cada tick reevalúa las condiciones desde arriba), y legibilidad para gente no-software — lo que en un cliente de defensa importa porque el árbol de decisión es lo que un operador o un evaluador quiere revisar.

**Límites que debes reconocer** (esto te hace creíble): el *blackboard* degenera fácilmente en variables globales; el estado implícito distribuido por el árbol es difícil de razonar; y los BT no son buenos expresando concurrencia con recursos compartidos. La respuesta madura: BT para la lógica de misión y arbitraje, FSM pequeña y explícita para los **modos operacionales**, y el safety monitor fuera de los dos.

**Herramientas:** `BehaviorTree.CPP` v4.x (MIT) y **Groot2** para edición visual, monitorización en vivo, replay de logs y fault injection. Groot2 es un argumento fuerte para la parte de "transferencia de conocimiento": el equipo puede ver y modificar el comportamiento sin leer C++.

📚 [BehaviorTree.CPP](https://www.behaviortree.dev/) · [Groot2](https://www.behaviortree.dev/groot) · [Nav2 Behavior Trees](https://docs.nav2.org/behavior_trees/index.html)

### 1.2 Modos operacionales — el diseño que más le importa a ARX

Vienen de teleoperación con alcance de 4 km. El diseño clave no es el planificador: es **el continuo de autonomía y la transferencia de control**.

Escalera propuesta (y defiéndela así en la entrevista):

1. **Teleoperación directa** — lo que tienen hoy.
2. **Teleoperación asistida** — el operador sigue mandando, pero el sistema veta comandos que llevan a colisión o vuelco, y limita velocidad según pendiente y rugosidad. *Este es el primer escalón que hay que entregar*: aumenta la seguridad, reduce la carga cognitiva del operador, no requiere que nadie confíe en la autonomía, y **empieza a generar el dataset**.
3. **Waypoint following supervisado** — el operador marca puntos, el vehículo navega, el operador vigila y puede tomar el control en cualquier momento.
4. **Comportamientos de misión** — convoy following, retorno autónomo por la ruta grabada ("breadcrumb return"), patrulla, aproximación a un punto.
5. **Autonomía supervisada extendida** — con humano en el bucle para cualquier decisión con consecuencias.

**Pérdida de enlace** — la decisión de diseño más delicada y la que más revela madurez. Las opciones no son equivalentes:
- Parar en seco: seguro pero convierte al vehículo en un blanco estático y en un obstáculo.
- Continuar al último waypoint: útil, riesgoso si el entorno cambió.
- **Breadcrumb return** (volver por la ruta ya recorrida hasta recuperar enlace): la opción más defendible, porque el terreno ya se demostró transitable.
- Buscar posición de mejor cobertura.

La respuesta correcta es *que sea configurable por misión y explícita para el operador*, con un temporizador y un comportamiento por defecto conservador. Y que el operador sepa, antes de perder el enlace, qué va a hacer el vehículo.

**Transparencia de intención:** el operador debe ver qué va a hacer el vehículo *antes* de que lo haga (trayectoria prevista, coste percibido, nivel de confianza). Sin esto, la autonomía no se adopta aunque funcione. Es un punto de producto, no solo técnico, y lo aprecian mucho en un perfil senior.

---

## 2. Planificación

### 2.1 Global
- **A\*** y **D\* Lite / Field D\***: replanificación eficiente cuando el mapa cambia — y off-road el mapa cambia constantemente porque la percepción tiene alcance limitado.
- **Hybrid-A\***: búsqueda en `(x, y, θ)` con primitivas de movimiento que respetan la cinemática. Necesario cuando el vehículo no puede girar sobre sí mismo (HECTOR, ruedas) — menos crítico en orugas que sí pueden.
- En Nav2 esto es la familia **Smac Planner** (Hybrid-A*, State Lattice, 2D-A*), con paper propio de Macenski et al.
- **Planificación sobre coste continuo, no binario.** Off-road no hay "libre/ocupado": hay grados. El planificador debe integrar coste a lo largo de la ruta, no solo evitar celdas.
- **Costes que no son distancia:** riesgo de vuelco, deslizamiento esperado, consumo energético, incertidumbre del mapa, y —en defensa— **exposición/visibilidad**. Planificar minimizando la exposición a líneas de visión es un requisito real en UGV militares y mencionarlo demuestra que entiendes el dominio.

📚 [Smac Planner (arXiv:2401.13078)](https://arxiv.org/abs/2401.13078) · [Nav2 docs](https://docs.nav2.org/)

### 2.2 Local: MPPI es la respuesta moderna

**MPPI (Model Predictive Path Integral)**: muestrea miles de secuencias de control perturbadas, las rueda a través de un modelo de dinámica, evalúa el coste de cada trayectoria resultante y calcula el control como una **media ponderada exponencialmente** por el coste (importance sampling).

Por qué encaja tan bien off-road:
- **No necesita que el coste sea diferenciable ni convexo** — puedes meter un costmap de traversability aprendido tal cual, con discontinuidades.
- Maneja **dinámica no lineal** directamente (incluido un modelo de slip aprendido).
- Paraleliza trivialmente en GPU — y ARX ya tiene CUDA en el stack.
- Está implementado y mantenido en Nav2 (`nav2_mppi_controller`), con soporte de modelos diff-drive, omni y Ackermann.

**Matiz para no meter la pata:** no existe un paper propio de Nav2 sobre su MPPI. La referencia es Williams et al. (2015/2016, Georgia Tech, el trabajo de AutoRally) más el README del paquete. Cítalo así.

Alternativas: DWB/DWA (simple, limitado a dinámicas sencillas), TEB (bueno con restricciones no holonómicas, más frágil de ajustar), Regulated Pure Pursuit (seguimiento de ruta robusto y muy predecible — buena elección para el modo "seguir ruta grabada").

📚 [MPPI original (arXiv:1509.01149)](https://arxiv.org/abs/1509.01149) · [Configuración MPPI en Nav2](https://docs.nav2.org/configuration/packages/configuring-mppic.html) · [Regulated Pure Pursuit (arXiv:2305.20026)](https://arxiv.org/abs/2305.20026)

### 2.3 Nav2: qué sirve y qué no off-road

Nav2 está diseñado para interiores y suelo plano, pero es el punto de partida realista. La respuesta matizada:

| Sirve | No sirve tal cual |
|---|---|
| El **framework de plugins** (planners, controllers, behaviors, costmap layers, nodos BT) | El costmap 2D binario con supuesto de suelo plano |
| El **BT Navigator** y su lógica de recovery | Las recovery behaviors por defecto (girar en el sitio puede ser peligroso en pendiente) |
| El **controlador MPPI** | El inflation layer clásico, pensado para obstáculos discretos |
| Lifecycle management y estructura general | La noción de "obstáculo" como celda binaria |

**Lo que harías:** conservar el framework, escribir una **capa de costmap propia** que consuma tu mapa de traversability multicapa (el tutorial oficial de "Writing a New Costmap2D Plugin" es el punto de entrada), sustituir el modelo de coste por uno continuo, y añadir la dimensión de pendiente. Esto es además la mejor demo práctica que puedes montar en un día.

📚 [Writing a New Costmap2D Plugin](https://docs.nav2.org/plugin_tutorials/docs/writing_new_costmap2d_plugin.html) · [The Marathon 2 — arquitectura de Nav2 (arXiv:2003.00368)](https://arxiv.org/abs/2003.00368)

---

## 3. Control de vehículos de orugas

Este es el bloque donde puedes sonar específico de su producto (GEREON es de orugas).

### 3.1 Por qué skid-steer es difícil
Un vehículo de orugas gira **deslizando**: no existe un centro instantáneo de rotación en el eje de las ruedas como en un differential drive ideal. El ICR real se desplaza y depende del terreno, la carga, la velocidad y el radio de giro. Consecuencia: **el modelo cinemático ideal es sistemáticamente erróneo**, y el error crece con el giro y con lo blando del terreno.

Aproximaciones:
- **Modelo cinemático extendido con factores de corrección empíricos** (Mandow et al., IROS 2007 — la referencia clásica): se identifican experimentalmente los desplazamientos del ICR. Simple y sorprendentemente eficaz.
- **Modelo de slip dependiente del terreno**, estimado online comparando el comando con la odometría real y con la odometría LiDAR-inercial. El residuo *es* una medida de tracción — y aquí se cierra el círculo con la traversability propioceptiva del Dossier 1.
- **Modelo de dinámica aprendido**, entrenado con datos de conducción (esto es literalmente para lo que existe TartanDrive), y usado dentro del MPPI.

📚 [Mandow et al. 2007 — Experimental Kinematics for Wheeled Skid-Steer](https://ieeexplore.ieee.org/document/4399139/) · [Review of models for wheeled and tracked UGV kinematics (open access)](https://doi.org/10.3390/math11173735)

### 3.2 Terramecánica — lo justo
No necesitas dominarla, pero nombrarla te sitúa: modelos de **Bekker-Wong** (relación presión-hundimiento, esfuerzo cortante-desplazamiento), presión de contacto de la oruga, *sinkage*, resistencia a la rodadura en terreno deformable. La idea operativa que sí debes tener: **la tracción disponible depende del terreno y no es observable directamente por cámara o LiDAR — solo se estima conduciendo.**

Para simulación con terreno deformable y orugas, la herramienta seria es **Chrono::Vehicle** (ver Dossier 4).

### 3.3 Estabilidad y límites
- Márgenes de vuelco estático y dinámico, centro de masas (que cambia con el payload — y ARX tiene payloads modulares intercambiables, lo cual es un problema real: **el modelo de vehículo debe reconfigurarse según el payload montado**).
- Pendiente máxima longitudinal vs lateral (la lateral es mucho más restrictiva).
- **Control adaptativo al terreno**: limitar velocidad en función de pendiente, rugosidad y confianza de la percepción. Este es el enlace explícito percepción→control y es una de las cosas que puedes proponer como entrega temprana.

---

## 4. Aprendizaje en behavior y control

Postura recomendada, en orden de riesgo creciente:

1. **Aprender el modelo de dinámica** y usarlo dentro de MPPI. Bajo riesgo, alto retorno, encaja con datos que ya tienen. **Empieza aquí.**
2. **Aprender el coste** desde demostraciones de teleoperación (IRL). Riesgo medio, muy alineado con su situación.
3. **Control residual**: controlador clásico + corrección aprendida acotada. El clásico garantiza el comportamiento base, el aprendido mejora en el margen. Es la respuesta pragmática y la que un cliente de defensa aceptará.
4. **RL end-to-end**: sim2real muy duro en dinámica de contacto suelo-oruga, difícil de certificar, difícil de depurar. Reconoce que existe y explica por qué no es tu primera opción aquí. *Decir que no a algo con buenas razones es una señal de senioridad más fuerte que decir que sí a todo.*

---

## 5. Autoevaluación

1. Explica un BT y por qué su reactividad es distinta de la de una FSM.
2. ¿Qué haces cuando pierdes el enlace de teleoperación? Justifica frente a las otras tres opciones.
3. ¿Por qué MPPI encaja mejor que DWA sobre un costmap de traversability aprendido?
4. ¿Qué partes de Nav2 conservas y cuáles sustituyes off-road?
5. ¿Por qué el modelo differential-drive ideal falla en orugas y cómo lo corriges?
6. Tu vehículo lleva payloads intercambiables. ¿Qué implica para el modelo de control?
7. Diseña la lógica que limita la velocidad usando la salida de percepción, incluida su incertidumbre.
8. ¿Dónde meterías aprendizaje en el lazo de control y dónde te negarías?
