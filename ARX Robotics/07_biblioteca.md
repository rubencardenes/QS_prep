# Biblioteca de referencias verificadas

*Todos los enlaces comprobados en agosto de 2026. Ordenados por prioridad para tu caso concreto, con tiempo estimado.*

---

## ⭐ NIVEL 1 — Si solo tienes 5 horas, lee esto

| # | Recurso | Tiempo | Por qué |
|---|---|---|---|
| 1 | [**GOOSE Labeling Policy (PDF)**](https://goose-dataset.de/docs/resources/labeling_policy.pdf) | 45 min | 64 clases off-road militares con definiciones y casos límite. Munición directa para toda la parte de anotación, y es alemán y del contexto Bundeswehr |
| 2 | [**Repo del survey: Autonomous Driving in Unstructured Environments**](https://github.com/chaytonmin/Survey-Autonomous-Driving-in-Unstructured-Environments) | 30 min hojeando | Índice vivo de todo el campo: 18 datasets, 50+ papers de percepción, 30 de planificación. El recurso individual más rentable que existe |
| 3 | [**Wild Visual Navigation** (arXiv:2305.08510)](https://arxiv.org/abs/2305.08510) | 40 min | Traversability auto-supervisada aprendida online en minutos de campo. Es tu argumento estrella para ARX, hecho concreto |
| 4 | [**EVORA** — traversabilidad evidencial](https://xiaoyi-cai.github.io/evora/) | 40 min | El enlace incertidumbre→planificación, que es lo que casi nadie lleva preparado |
| 5 | [**Configuración del MPPI en Nav2**](https://docs.nav2.org/configuration/packages/configuring-mppic.html) | 30 min | Para poder hablar de MPPI con parámetros reales y no de oídas |
| 6 | [**Nav2: Writing a New Costmap2D Plugin**](https://docs.nav2.org/plugin_tutorials/docs/writing_new_costmap2d_plugin.html) | 45 min | Es exactamente lo que harías el primer mes en ARX. Léelo y, si puedes, hazlo |
| 7 | [**CVAT — QA, ground truth y honeypots**](https://docs.cvat.ai/docs/qa-analytics/auto-qa/) | 30 min | La oferta pide QS de anotación literalmente. Esto es el cómo, en concreto |
| 8 | [**Isaac Sim — releases**](https://github.com/isaac-sim/IsaacSim/releases) + [Isaac Lab](https://isaac-sim.github.io/IsaacLab/main/index.html) | 20 min | Solo para tener versiones y capacidades actuales correctas (6.0.1 GA) |

---

## PERCEPCIÓN OFF-ROAD

### Surveys (empieza por aquí si vas justo de base)
- [Autonomous Driving in Unstructured Environments: How Far Have We Come? (arXiv:2410.07701)](https://arxiv.org/abs/2410.07701) — +250 papers, el más completo. Publicado en *J. Field Robotics* mar-2026.
- [A Survey of Traversability Estimation for Mobile Robots (arXiv:2204.10883)](https://arxiv.org/abs/2204.10883) — 2022, buena base histórica: de métodos clásicos a self-supervised.
- [Overview of Terrain Traversability Evaluation for Autonomous Robots (JFR 2024/25)](https://onlinelibrary.wiley.com/doi/10.1002/rob.22461)
- [awesome-traversability-analysis](https://github.com/Ikhyeon-Cho/awesome-traversability-analysis) — lista curada por categorías, útil como índice rápido.
- ⚠️ [A Review of Learning Off-Road Terrain Traversability for AGVs (ASME, 2026)](https://asmedigitalcollection.asme.org/autonomousvehicles/article/6/2/020801/1229986/A-Review-of-Learning-Off-Road-Terrain) — DOI 10.1115/1.4070847. Existe y es muy pertinente (perspectiva de vehículos militares del US Army GVSC), pero es de pago.
- ⚠️ [Advances and Trends in Terrain Classification Methods for Off-Road Perception (JFR, may-2025)](https://onlinelibrary.wiley.com/doi/10.1002/rob.22586) — DOI 10.1002/rob.22586. De pago.

### Traversability auto-supervisada (el bloque clave)
- [BADGR (arXiv:2002.05700)](https://arxiv.org/abs/2002.05700) — 2020, el fundacional.
- [WayFAST (arXiv:2203.12071)](https://arxiv.org/abs/2203.12071) · [código](https://github.com/matval/WayFAST) — supervisión desde el tracking del propio controlador.
- [Wild Visual Navigation (arXiv:2305.08510)](https://arxiv.org/abs/2305.08510) · [código](https://github.com/leggedrobotics/wild_visual_navigation) — ETH+Oxford, online en minutos.
- [V-STRONG (arXiv:2312.16016)](https://arxiv.org/abs/2312.16016) — modelos fundacionales + contrastivo.
- [ScaTE (arXiv:2209.06522)](https://arxiv.org/abs/2209.06522) · [LeSTA](https://github.com/Ikhyeon-Cho/LeSTA) · [Follow the Footprints (arXiv:2402.15363)](https://arxiv.org/abs/2402.15363)

### Coste desde demostración humana
- [Learning Risk-Aware Costmaps via IRL for Off-Road Navigation (arXiv:2302.00134)](https://arxiv.org/abs/2302.00134) — **la referencia**: −57% intervenciones frente a baselines geométricos.

### Incertidumbre y riesgo
- [EVORA (arXiv:2311.06234)](https://arxiv.org/abs/2311.06234) · [proyecto](https://xiaoyi-cai.github.io/evora/) · [código MPPI](https://github.com/mit-acl/mppi_numba) — MIT ACL, T-RO.
- [STEP (arXiv:2103.02828)](https://arxiv.org/abs/2103.02828) — JPL, equipo NeBula de DARPA SubT, riesgo con CVaR.

### BEV / terreno aprendido
- [TerrainNet (arXiv:2303.15771)](https://arxiv.org/abs/2303.15771) · [RoadRunner (arXiv:2402.19341)](https://arxiv.org/abs/2402.19341) · [RoadRunner M&M (arXiv:2409.10940)](https://arxiv.org/abs/2409.10940)

### Obstáculos negativos
⚠️ Área sin paper canónico moderno. Lo mejor accesible:
- [LiDAR-Based Negative Obstacle Detection (Sensors 2024, open access)](https://pmc.ncbi.nlm.nih.gov/articles/PMC11679008/) — lo más reciente.
- [An Analytic Model for Negative Obstacle Detection with Lidar (Sensors 2021, open access)](https://pmc.ncbi.nlm.nih.gov/articles/PMC8125519/) — **el mejor de los dos**: modelo analítico de los límites físicos de detección según densidad angular y distancia. Útil para argumentar diseño de sensores.

### Datasets
- [**GOOSE**](https://goose-dataset.de/) ⭐ · [labeling policy](https://goose-dataset.de/docs/resources/labeling_policy.pdf) · [clases](https://goose-dataset.de/docs/class-definitions/) · [paper (arXiv:2310.16788)](https://arxiv.org/abs/2310.16788) · [GOOSE-Ex (arXiv:2409.18788)](https://arxiv.org/abs/2409.18788) · [repo](https://github.com/FraunhoferIOSB/goose_dataset)
- [ORAD-3D (arXiv:2510.16500)](https://arxiv.org/abs/2510.16500) — ICRA 2026, el mayor dataset off-road actual.
- [STONE (arXiv:2603.09175)](https://arxiv.org/abs/2603.09175) — mar-2026, surround-view **con radar**.
- [RELLIS-3D](https://github.com/unmannedlab/RELLIS-3D) · [TartanDrive 2.0](https://theairlab.org/TartanDrive2/) · [RUGD](http://rugd.vision/) · [ORFD](https://arxiv.org/abs/2206.09907) · [CaT (CAVS)](https://www.cavs.msstate.edu/resources/autonomous_dataset.php) · [Yamaha-CMU](https://theairlab.org/yamaha-offroad-dataset/) · [Freiburg Forest](https://deepscene.cs.uni-freiburg.de/)
- [Verti-Bench (arXiv:2502.11426)](https://arxiv.org/abs/2502.11426) — benchmark en simulación de terreno verticalmente desafiante.

### Software
- [grid_map](https://github.com/ANYbotics/grid_map) · [elevation_mapping_cupy](https://github.com/leggedrobotics/elevation_mapping_cupy) (usa esta; la versión CPU está sin mantener) · [nvblox](https://github.com/nvidia-isaac/nvblox) · [Voxblox](https://github.com/ethz-asl/voxblox) · [OctoMap](https://github.com/OctoMap/octomap)
- [FAST-LIO](https://github.com/hku-mars/FAST_LIO) · [LIO-SAM](https://github.com/TixiaoShan/LIO-SAM) · [KISS-ICP](https://github.com/PRBonn/kiss-icp) · [robot_localization](https://github.com/cra-ros-pkg/robot_localization)
- [SalsaNext](https://github.com/TiagoCortinhal/SalsaNext) · [RandLA-Net](https://github.com/QingyongHu/RandLA-Net) · [Cylinder3D](https://github.com/xinge008/Cylinder3D) · [OpenPCDet](https://github.com/open-mmlab/OpenPCDet) · [MMDetection3D](https://github.com/open-mmlab/mmdetection3d) ⚠️ SPVNAS está archivado, úsalo vía MMDetection3D
- [direct_visual_lidar_calibration](https://github.com/koide3/direct_visual_lidar_calibration) — calibración targetless, la primera a probar · [TIER IV CalibrationTools](https://github.com/tier4/CalibrationTools)

---

## ROS 2

- [Distribuciones y EOL](https://docs.ros.org/en/jazzy/Releases.html) · [endoflife.date/ros-2](https://endoflife.date/ros-2) · [Anuncio de Lyrical Luth](https://discourse.openrobotics.org/t/ros-2-lyrical-luth-released/55021)
- [QoS — concepto](https://docs.ros.org/en/jazzy/Concepts/Intermediate/About-Quality-of-Service-Settings.html) · [Overriding QoS para rosbag](https://docs.ros.org/en/jazzy/How-To-Guides/Overriding-QoS-Policies-For-Recording-And-Playback.html)
- [Executors](https://docs.ros.org/en/kilted/Concepts/Intermediate/About-Executors.html) · [Callback groups](https://docs.ros.org/en/jazzy/How-To-Guides/Using-callback-groups.html)
- [Intra-process comms](https://docs.ros.org/en/jazzy/Tutorials/Demos/Intra-Process-Communication.html) · [diseño IPC](https://design.ros2.org/articles/intraprocess_communications.html) · [Zero-copy / loaned messages](https://docs.ros.org/en/rolling/How-To-Guides/Disabling-ZeroCopy-loaned-messages.html)
- [Composition](https://docs.ros.org/en/jazzy/Tutorials/Intermediate/Composition.html) · [**Impact of Node Composition (arXiv:2305.09933)**](https://arxiv.org/abs/2305.09933) ⭐ el paper que lo cuantifica
- [Lifecycle nodes](https://docs.ros.org/en/jazzy/Tutorials/Demos/Managed-Nodes.html) · [tf2](https://docs.ros.org/en/jazzy/Tutorials/Intermediate/Tf2/Tf2-Main.html) · [Debugging tf2](https://docs.ros.org/en/jazzy/Tutorials/Intermediate/Tf2/Debugging-Tf2-Problems.html)
- [ros2_control](https://control.ros.org/jazzy/index.html) · [rosbag2](https://github.com/ros2/rosbag2) · [MCAP](https://mcap.dev/)
- [rmw_zenoh](https://github.com/ros2/rmw_zenoh) · [sros2](https://github.com/ros2/sros2) · [Setting up security](https://docs.ros.org/en/humble/Tutorials/Advanced/Security/Introducing-ros2-security.html)
- [ROS 2 Real-Time WG](https://ros-realtime.github.io/) · [Guides RT](https://ros-realtime.github.io/Guides/guides.html) · [DDS tuning](https://docs.ros.org/en/jazzy/How-To-Guides/DDS-tuning.html)
- [ROS 2 Design (artículos originales)](https://design.ros2.org/) ⭐ la mejor preparación para "¿por qué ROS 2 hace X así?"
- [ROS 2: Design, architecture and uses in the wild (Science Robotics 2022)](https://www.science.org/doi/10.1126/scirobotics.abm6074)
- Gratis y práctico: [Articulated Robotics](https://articulatedrobotics.xyz/) · [código del libro de F. Martín Rico](https://github.com/fmrico/book_ros2)

---

## BEHAVIOR, PLANIFICACIÓN Y CONTROL

- [Nav2 docs](https://docs.nav2.org/) · [Costmaps](https://docs.nav2.org/configuration/packages/configuring-costmaps.html) · [**Custom costmap plugin**](https://docs.nav2.org/plugin_tutorials/docs/writing_new_costmap2d_plugin.html) ⭐ · [Behavior Trees en Nav2](https://docs.nav2.org/behavior_trees/index.html) · [Smac Hybrid-A*](https://docs.nav2.org/configuration/packages/smac/configuring-smac-hybrid.html) · [MPPI](https://docs.nav2.org/configuration/packages/configuring-mppic.html) · [Regulated Pure Pursuit](https://docs.nav2.org/configuration/packages/configuring-regulated-pp.html)
- [BehaviorTree.CPP (v4.8)](https://www.behaviortree.dev/) · [Intro v4](https://www.behaviortree.dev/docs/intro) · [Groot2](https://www.behaviortree.dev/groot)
- [MPPI original — Williams et al. (arXiv:1509.01149)](https://arxiv.org/abs/1509.01149) · [Aggressive Driving with MPPI (ICRA 2016)](https://dl.acm.org/doi/10.1109/ICRA.2016.7487277) ⚠️ **no existe paper propio del MPPI de Nav2** — cita estos + el README del paquete
- [The Marathon 2 — arquitectura de Nav2 (arXiv:2003.00368)](https://arxiv.org/abs/2003.00368) · [Smac Planner (arXiv:2401.13078)](https://arxiv.org/abs/2401.13078) · [Regulated Pure Pursuit (arXiv:2305.20026)](https://arxiv.org/abs/2305.20026) · [Survey de algoritmos ROS 2 (arXiv:2307.15236)](https://arxiv.org/abs/2307.15236) · [Publicaciones de Steve Macenski](https://steve.macenski.com/publications/)
- Orugas y slip: [Mandow et al. 2007 (clásico)](https://ieeexplore.ieee.org/document/4399139/) · [Review de modelos UGV con ruedas y orugas (open access)](https://doi.org/10.3390/math11173735) · [Slip-compensated odometry para orugas (open access)](https://link.springer.com/article/10.1186/s40648-017-0095-1)
- MPC: [do-mpc](https://www.do-mpc.com/en/latest/) (Python, didáctico) · [acados](https://docs.acados.org/) (NMPC embebido real) · [Workshop MPC/MHE de Mehrez con CasADi](https://github.com/MMehrez/MPC-and-MHE-implementation-in-MATLAB-using-Casadi) + [playlist](https://www.youtube.com/playlist?list=PLK8squHT_Uzej3UCUHjtOtm5X7pMFSgAL)

---

## SIMULACIÓN Y VALIDACIÓN

- [Isaac Sim docs](https://docs.isaacsim.omniverse.nvidia.com/latest/index.html) · [releases (6.0.1 GA)](https://github.com/isaac-sim/IsaacSim/releases) · [Isaac Lab 2.3.2](https://isaac-sim.github.io/IsaacLab/main/index.html) · [Isaac ROS](https://nvidia-isaac-ros.github.io/) · [Replicator](https://docs.omniverse.nvidia.com/extensions/latest/ext_replicator.html)
- [Gazebo releases (Jetty LTS / Harmonic)](https://gazebosim.org/docs/latest/releases/) · [ros_gz](https://github.com/gazebosim/ros_gz)
- [Project Chrono](https://projectchrono.org/) · [API](http://api.projectchrono.org/) — **la referencia para orugas sobre terreno deformable**
- [Colosseum (sucesor de AirSim, UE 5.6)](https://github.com/CodexLabsLLC/Colosseum) · [CARLA](https://carla.org/) ⚠️ su doc "latest" describe UE 4.26, no la 0.10.0 sobre UE 5.5
- [ASAM OpenSCENARIO XML 1.3.1](https://www.asam.net/standards/detail/openscenario-xml/) · [OpenSCENARIO DSL 2.2.0](https://www.asam.net/standards/detail/openscenario-dsl/) · [OpenDRIVE 1.8.1](https://www.asam.net/standards/detail/opendrive/) · [ASAM: XML y DSL son estándares separados](https://www.asam.net/news-media/news/detail/news/asam-openscenarior-1-and-2-split-into-separate-standards/) ⭐ dato fino
- [**Survey on Scenario-Based Testing (arXiv:2112.00964)**](https://arxiv.org/pdf/2112.00964) — el mejor punto de entrada gratuito · [Tree-Based Scenario Classification / cobertura (arXiv:2307.05106)](https://arxiv.org/abs/2307.05106)
- SOTIF: [Guía Jama (gratis)](https://www.jamasoftware.com/requirements-management-guide/automotive-engineering/sotif/) · [eBook LHP (PDF gratis)](https://www.lhpes.com/hubfs/LSS-eBook-PDF-The-Guide-to-SOTIF-ISO-21448.pdf) · [ISO 21448 oficial](https://www.iso.org/standard/77490.html)
- [Foretellix Foretify](https://www.foretellix.com/foretify-platform/) · [Qué es OpenSCENARIO DSL](https://www.foretellix.com/what-is-asam-openscenario-dsl/) · [MORAI Defense](https://www.morai.ai/defense-systems)
- [Foxglove docs](https://docs.foxglove.dev/docs) · [Rerun](https://rerun.io/docs)

---

## DATOS, ANOTACIÓN Y MLOps

- [CVAT — anotación 3D](https://docs.cvat.ai/docs/annotation/manual-annotation/modes/3d-object-annotation/) · [**QA & Analytics**](https://docs.cvat.ai/docs/qa-analytics/) ⭐ · [Auto QA y honeypots](https://docs.cvat.ai/docs/qa-analytics/auto-qa/) · [Quality control in data annotation (guía)](https://www.cvat.ai/academy/labeling-quality-control)
- [SUSTechPOINTS](https://github.com/naurril/SUSTechPOINTS) · [Label Studio](https://labelstud.io/guide/) ⚠️ soporte 3D no confirmado · [Segments.ai docs](https://docs.segments.ai/)
- [FiftyOne](https://docs.voxel51.com/) · [curación pre-anotación](https://docs.voxel51.com/workflows/curation_pre.html) · [Smart Sample Selection](https://docs.voxel51.com/getting_started/annotation/03_smart_selection.html) · [FiftyOne Brain](https://docs.voxel51.com/brain/index.html) · [Finding detection mistakes](https://docs.voxel51.com/tutorials/detection_mistakes.html)
- [SAM 2 (Apache 2.0)](https://github.com/facebookresearch/sam2) · [SAM 3 / 3.1](https://github.com/facebookresearch/sam3) ⚠️ licencia restrictiva, no Apache
- [DVC](https://doc.dvc.org/) · [lakeFS](https://docs.lakefs.io/)
- [**Artstein & Poesio — Inter-Coder Agreement** (PDF gratis)](https://aclanthology.org/J08-4004.pdf) ⭐ la referencia canónica sobre kappa, pi y Krippendorff's alpha · [Krippendorff's alpha explicado para ML](https://encord.com/blog/interrater-reliability-krippendorffs-alpha/)

---

## CURSOS Y FORMACIÓN (gratis)

- [**Mobile Sensing and Robotics 2 — Cyrill Stachniss, Univ. Bonn**](https://www.ipb.uni-bonn.de/msr2-2021/index.html) ⭐ 14 semanas, vídeos + slides PDF, sin registro. SLAM, ICP, registro de nubes, graph-SLAM, calibración, geometría epipolar. **La mejor formación gratuita de base.** · [MSR 1](https://www.ipb.uni-bonn.de/msr1-2021/index.html)
- [ROB 530 Mobile Robotics — Univ. of Michigan](https://github.com/UMich-CURLY-teaching/UMich-ROB-530-public) · [clases en YouTube](https://www.youtube.com/playlist?list=PLdMorpQLjeXmbFaVku4JdjmQByHHqTd1F) — nivel posgrado, con tareas y código.
- [ICRA 2024 Workshop on Resilient Off-Road Autonomy (CMU AirLab)](https://theairlab.org/icra2024_offroad_workshop/) — el evento más pertinente a tu tema. ⚠️ Grabaciones no confirmadas.
- [Workshop on Field Robotics — ICRA 2026](https://norlab-ulaval.github.io/icra_workshop_field_robotics/) — incluye competición de segmentación semántica.
- [Autonomous Off-road Driving — CMU AirLab](https://theairlab.org/offroad/) — buena lectura conceptual sobre por qué abandonar la anotación manual a favor de la propiocepción.
- ⚠️ El curso "Programming for Robotics – ROS" de ETH RSL **ya no es de acceso público** (requiere Moodle). No cuentes con él.

---

## ⚠️ Resumen de cosas que NO debes afirmar sin comprobar

1. Que ARX tiene contrato con la **Bundeswehr** (no está confirmado públicamente).
2. Que Rheinmetall o KNDS son socios suyos (no lo son).
3. Que existe un paper propio de Nav2 sobre su MPPI (no existe).
4. Que hay una comparativa neutral y reciente de Fast DDS vs Cyclone DDS (los informes del TSC solo llegan a Humble).
5. Que rmw_zenoh es el RMW por defecto en alguna distro (su Tier-1 sí está cerrado; el resto confírmalo en REP-2005).
6. Que Label Studio o Segments.ai soportan nubes de puntos (no confirmado en su documentación).
7. Que SAM 3 es Apache 2.0 (usa la "SAM License", con restricciones).
8. Que Isaac Sim va por la 5.x (va por **6.0.1 GA**).
