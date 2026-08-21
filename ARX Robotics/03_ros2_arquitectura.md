# Dossier 2 — ROS 2 senior y arquitectura del stack

*ARX pide literalmente C++ + ROS 2 + Linux como núcleo. Esto no es un tema secundario para ellos.*

---

## 1. Distribuciones: la respuesta correcta en agosto de 2026

| Distro | Release | EOL | LTS |
|---|---|---|---|
| **Lyrical Luth** | 22 may 2026 | **may 2031** | ✅ LTS activa (Ubuntu 26.04) |
| **Jazzy Jalisco** | 23 may 2024 | may 2029 | ✅ LTS madura, la más probable en producción |
| Kilted Kaiju | 23 may 2025 | **dic 2026** | ❌ muere en meses |
| Humble Hawksbill | 23 may 2022 | may 2027 | ✅ legado |

Cadencia: release cada 23 de mayo; años pares = LTS de 5 años, impares = 1,5 años.

**Cómo usarlo en la entrevista:** *"¿En qué distro estáis? Si es Kilted, el EOL de diciembre convierte la migración en una decisión de este trimestre, no del año que viene."* Es una pregunta de arquitectura con consecuencias de planificación — exactamente el registro que buscan.

---

## 2. Los seis temas de ROS 2 que se preguntan a un senior

### 2.1 QoS — el que más filtra
Las políticas: **reliability** (reliable vs best-effort), **durability** (volatile vs transient_local), **history/depth**, **deadline**, **liveliness**, **lifespan**.

Lo que importa es saber **elegir**:
- Nubes de LiDAR a 10 Hz: `best_effort` + depth 1. Perder un barrido no importa; acumular una cola sí — te da datos viejos y latencia creciente.
- Comandos de control: `reliable`, depth 1, con `deadline` para detectar que el productor dejó de publicar.
- Mapa estático o parámetros de calibración: `transient_local` para que un nodo que arranque tarde reciba el último valor.
- Telemetría por radio degradada hacia la estación de teleoperación: `best_effort` + `lifespan` (un dato de hace 3 segundos ya no sirve, mejor descartarlo que entregarlo tarde).

**Incompatibilidad de QoS** es la causa nº1 de "mi suscriptor no recibe nada": un suscriptor `reliable` no se empareja con un publicador `best_effort`. Sabérselo demuestra horas de vuelo.

### 2.2 Ejecutores y callback groups
- `SingleThreadedExecutor` (por defecto), `MultiThreadedExecutor`, `StaticSingleThreadedExecutor` y el más moderno **`EventsExecutor`** (basado en eventos en lugar de wait-set: menor latencia y menos CPU).
- **Callback groups:** `MutuallyExclusive` (los callbacks del grupo nunca corren en paralelo) vs `Reentrant`. El caso clásico: llamar a un servicio desde dentro de un callback con executor single-threaded produce **deadlock**. La solución es poner el cliente en un callback group reentrante o usar un executor multihilo con grupos bien separados.
- Saber que el *orden* de ejecución de callbacks en ROS 2 no está garantizado como uno espera, y que si el determinismo importa hay que diseñarlo explícitamente.

### 2.3 Composición e intra-process / zero-copy
Con nubes de puntos de decenas de MB/s esto deja de ser una optimización y pasa a ser arquitectura.

- **Composición:** cargar varios nodos como componentes en un mismo proceso (`rclcpp_components`). Permite comunicación intra-proceso.
- **Intra-process comms:** publicar con `unique_ptr` para transferir propiedad sin copia. Requiere que el tipo sea el mismo y que el publicador y suscriptor estén en el proceso.
- **Zero-copy entre procesos:** *loaned messages* + memoria compartida (data-sharing de Fast DDS). Solo funciona con mensajes de tamaño fijo (POD), lo que excluye `PointCloud2` tal cual — matiz que casi nadie menciona.
- Hay un paper que **cuantifica** la ganancia: Macenski et al., *Impact of ROS 2 Node Composition in Robotic Systems* (RA-L 2023). Citarlo es oro.

📚 [arXiv:2305.09933](https://arxiv.org/abs/2305.09933)

### 2.4 Lifecycle nodes
Máquina de estados: `unconfigured → inactive → active → finalized`. Sirve para arranque ordenado (no publicar basura mientras se calibran sensores), para reconfiguración en caliente y, sobre todo, para **degradación controlada**: si un sensor falla, desactivas su nodo y el sistema entra en modo reducido en vez de morir. En un vehículo militar esto es requisito, no lujo.

### 2.5 Middleware: DDS, y por qué Zenoh importa aquí
- **Fast DDS** (por defecto) vs **Cyclone DDS**. No hay comparativa neutral reciente del TSC (los informes oficiales solo cubren Galactic y Humble), así que evita afirmaciones tajantes.
- **`rmw_zenoh`** es el tema actual: RMW basado en Zenoh, con arquitectura de router en lugar de descubrimiento multicast. **Por qué es relevante para ARX en concreto:** el descubrimiento DDS multicast se comporta mal en enlaces inalámbricos con pérdidas y en redes de campo; Zenoh está diseñado para topologías con routers y enlaces intermitentes — es decir, para el enlace vehículo↔estación de teleoperación a 4 km. Su issue de "llegar a Tier-1" está cerrado y se incorporó a REP-2005. *(Confirma el estado exacto en REP-2005 antes de afirmarlo como hecho.)*
- **SROS2** — autenticación, cifrado y control de acceso vía DDS-Security, con keystores y enclaves. En defensa te lo van a preguntar o valorar.

📚 [rmw_zenoh](https://github.com/ros2/rmw_zenoh) · [sros2](https://github.com/ros2/sros2)

### 2.6 rosbag2 y MCAP — la base de todo lo demás
El storage plugin **por defecto es ahora MCAP** (sqlite3 sigue disponible). MCAP es un contenedor de log multimodal con índices y compresión por chunks, y es el formato nativo de Foxglove.

Esto importa porque **el bag es la unidad atómica de tu data loop**: grabación selectiva en campo (no puedes grabar todo, hay que decidir qué y con qué política de retención), particionado, replay determinista, y metadatos (vehículo, sesión, versión de software, calibración vigente) sin los cuales el dataset es inservible a los seis meses.

📚 [rosbag2](https://github.com/ros2/rosbag2) · [MCAP](https://mcap.dev/) · [Foxglove docs](https://docs.foxglove.dev/docs)

### Extra: tiempo real
Qué es realista: ROS 2 con PREEMPT_RT, `mlockall`, prioridades SCHED_FIFO, aislamiento de CPU y allocators sin page faults puede dar latencias acotadas para lazos de control blandos. Lo que **no** debe ir en ROS 2 es el lazo de control duro de bajo nivel: eso vive en un microcontrolador o en el controlador de la plataforma. Saber dónde poner la frontera es la respuesta senior.

📚 [ROS 2 Real-Time WG](https://ros-realtime.github.io/) · [DDS tuning](https://docs.ros.org/en/jazzy/How-To-Guides/DDS-tuning.html)

---

## 3. Arquitectura de referencia (practica dibujarla en 3 minutos)

```
   ┌── Sensores ──┐   cámara · LiDAR · radar · IMU · GNSS · odom orugas
   │  drivers +   │
   │  sync (PTP)  │
   └──────┬───────┘
          │  (deskewing con IMU)
   ┌──────▼───────────────┐        ┌───────────────────────────┐
   │ State Estimation     │◄──────►│ Factor graph / EKF        │
   │ (LIO + GNSS + slip)  │        │ detección degeneración    │
   └──────┬───────────────┘        └───────────────────────────┘
          │ pose + incertidumbre
   ┌──────▼──────────────────────────────────────┐
   │ MAPA LOCAL multicapa (robot-céntrico)       │
   │  elevación · varianza · semántica ·         │
   │  traversability + INCERTIDUMBRE             │
   └──────┬──────────────────────────────────────┘
          │ costmap probabilístico
   ┌──────▼───────────────┐
   │ BEHAVIOR (BT)        │  modos: manual / teleop asistida /
   │ misión + modos       │  waypoints / autónomo supervisado
   └──────┬───────────────┘
   ┌──────▼───────────────┐
   │ Global planner       │  Hybrid-A* / Smac sobre coste continuo
   └──────┬───────────────┘
   ┌──────▼───────────────┐
   │ Local planner/ctrl   │  MPPI (modelo de dinámica con slip)
   └──────┬───────────────┘
   ┌──────▼───────────────┐
   │ ros2_control → HW    │
   └──────────────────────┘

   ══ TRANSVERSAL ══
   SAFETY MONITOR independiente: e-stop, geofence, watchdog de enlace,
        límites de velocidad por pendiente — simple, auditable, sin ML
   TELEOP / HMI: transferencia de control, transparencia de intención
   OBSERVABILIDAD: logging selectivo → MCAP → data loop
```

### Los cinco argumentos de arquitectura que debes poder defender

1. **Modular, no end-to-end.** En defensa se necesita explicabilidad, depurabilidad y trazabilidad de por qué el vehículo hizo lo que hizo. Además hay pocos datos. End-to-end es tentador y es la respuesta equivocada aquí — aunque debes reconocer dónde sí encaja (predicción de dinámica, traversability aprendida como *módulo* dentro del stack).

2. **El safety monitor es independiente y tonto a propósito.** No comparte código ni modelos con el stack de autonomía, no contiene ML, y puede vetar cualquier comando. Es lo único que puedes razonar formalmente. Si el monitor depende del mismo mapa que el planificador, un fallo del mapa se propaga a los dos.

3. **La abstracción de plataforma es un problema de primer orden en ARX.** El mismo stack debe correr en GEREON (orugas, 15 km/h, 500 kg) y HECTOR (ruedas, 70 km/h, 1.000 kg, opcionalmente tripulado) y sobre camiones retrofitados. Eso obliga a: un modelo de vehículo como *dato de configuración* (cinemática, límites de pendiente, footprint, modelo de slip), no como código; una capa de abstracción de sensores; y perfiles de misión parametrizados. **Muy poca gente les va a hablar de esto y es exactamente lo que necesitan.**

4. **Contratos de interfaz explícitos entre capas.** Percepción entrega un costmap con semántica *y* con incertidumbre, con un contrato versionado. Behavior no lee capas internas de percepción. Eso permite sustituir la implementación de traversability sin tocar el planificador — que es justo lo que vas a hacer tres veces en 12 meses.

5. **Degradación en niveles, no binaria.** Nada de "funciona / no funciona". Define modos: nominal → sin GNSS → sin cámara (polvo) → sin enlace → parada segura. Cada modo con su política de velocidad y su comportamiento. Es la diferencia entre un demo y un producto.

---

## 4. Cómputo embebido y despliegue

- **Edge:** ARX menciona CUDA y optimización edge, sin nombrar plataforma. Asume familia Jetson (AGX Orin, y Thor en lo nuevo). Prepara: presupuesto de potencia y térmico, latencia p99 por módulo, y qué recortas primero cuando no cabe.
- **TensorRT** (lo piden explícitamente): conversión ONNX → engine, precisión FP16/INT8, calibración de cuantización, layers no soportadas, y que un engine está atado a la versión de TensorRT y a la arquitectura de GPU — trampa de despliegue clásica.
- **Isaac ROS** si están en GPU NVIDIA: paquetes acelerados y **NITROS**, que evita copias GPU↔CPU entre nodos encadenados. Es el argumento técnico correcto para justificarlo.
- **Contenedores y CI/CD** (lo piden): imagen base ROS 2, `colcon`, cache de build, tests en PR, y —el punto que impresiona— **simulación en CI**: cada PR ejecuta un conjunto de escenarios en headless y compara métricas contra baseline. Enlaza directamente con su equipo de Autonomy & VVT.
- **OTA** a flota desplegada: versionado de modelos y de mapas, rollback, y el problema real de actualizar vehículos que están en Ucrania con conectividad intermitente.

---

## 5. Autoevaluación

1. Un suscriptor no recibe nada y el tópico existe. Tres causas y cómo las descartas en orden.
2. ¿Cuándo usarías `transient_local` y por qué es peligroso por defecto?
3. Explica un deadlock por callback groups y cómo lo arreglas.
4. ¿Por qué zero-copy no funciona directamente con `PointCloud2`?
5. ¿Qué le pedirías a Zenoh que DDS no te da en un enlace de radio a 4 km?
6. ¿Dónde pondrías la frontera entre ROS 2 y control de tiempo real duro?
7. ¿Cómo diseñas el stack para que corra en dos vehículos con cinemática distinta sin bifurcar el código?
8. ¿Qué grabas en campo si solo puedes permitirte el 5% de los datos, y cómo lo decides?
