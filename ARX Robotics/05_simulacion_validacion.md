# Dossier 4 — Simulación y validación

*ARX tiene un departamento llamado **Autonomy & VVT** con vacantes de **Robotics SiL Simulation Engineer** y **Senior Data Engineer Simulation & Synthetic**. Este bloque no es opcional: es una de sus apuestas declaradas.*

---

## 1. Por qué la simulación es el cuello de botella real

En un producto de defensa desplegado, el ciclo de iteración por campo es carísimo: hay que mover el vehículo, coordinar un terreno, tener operadores, y muchas veces no puedes reproducir la condición que falló. La simulación no sustituye al campo — **sustituye a las 200 iteraciones que no puedes permitirte hacer en campo antes de la que sí haces**.

Y hay un segundo motivo específico de ARX: su stack tiene que correr sobre plataformas distintas (GEREON orugas 15 km/h, HECTOR ruedas 70 km/h, camiones retrofitados). Validar N funciones × M plataformas × K condiciones en campo real es imposible. En simulación es una matriz de barrido.

---

## 2. Panorama de herramientas (con criterio, no como lista)

| Herramienta | Estado ago-2026 | Fuerte en | Débil en | Cuándo la elegirías |
|---|---|---|---|---|
| **NVIDIA Isaac Sim** | **6.0.1 GA** (jun-2026), Isaac Lab 2.3.2 | Sensores físicamente plausibles (RTX LiDAR, radar), USD/Omniverse, **Replicator** para datos sintéticos, ROS 2 bridge, RL a escala | Curva de aprendizaje, GPU cara, terreno deformable limitado | **Percepción y generación de datos sintéticos**. La apuesta más probable si ya usan CUDA/NVIDIA |
| **Gazebo** | **Jetty** (LTS, sep-2025→2031); Harmonic (LTS, →2029) es lo más extendido | Nativo ROS 2, ligero, headless, ideal en CI | Fidelidad visual y de sensores modesta | **Tests de regresión en CI.** Barato, rápido, reproducible |
| **Unreal Engine 5 / Colosseum** | Colosseum (sucesor de AirSim) requiere UE 5.6, tiene rama ROS 2 | Fidelidad visual, terrenos enormes, integración geoespacial | Física de vehículo mediocre, hay que mantener el puente | Realismo visual para percepción y para entrenamiento de operadores |
| **Project Chrono / Chrono::Vehicle** | v10.0.0, BSD-3 | **Terramecánica real: terreno deformable y vehículos de orugas** con plantillas validadas | No es un simulador de percepción | Si el riesgo es la *movilidad* (barro, arena, pendiente) más que la percepción. **La única de la lista que modela bien orugas sobre terreno blando** |
| **CARLA** | 0.10.0 (dic-2024, UE 5.5) | Maduro, scenario runner, OpenSCENARIO | Diseñado para **carretera** | Referencia metodológica, no plataforma off-road |
| **MORAI** | Comercial; tiene líneas Robotics y **Defense** | Digital twin, escenarios | Cerrado, orientado a automoción | Si compran en vez de construir |
| **Foretellix (Foretify)** | Comercial, sobre OpenSCENARIO DSL | **Verificación coverage-driven**: generar miles de variantes y medir cobertura | Caro, orientado a ADAS | Aporta sobre todo *la metodología*; puedes replicar el concepto sin comprarlo |

### La respuesta correcta en entrevista
**Nunca es "un simulador". Es una pila con propósitos separados:**

- **Gazebo headless en CI** → regresión rápida en cada PR. Segundos, no minutos. Nadie mira los resultados salvo cuando fallan.
- **Isaac Sim** → percepción, sensores realistas y generación de datos sintéticos para clases raras.
- **Chrono** → validación de movilidad y modelo de dinámica sobre terreno deformable, si ese es el riesgo dominante.
- **Replay de bags reales** → el test más valioso de todos, y el más barato. No es simulación pero es la primera línea de defensa.

Si dices esto, y explicas que la pregunta correcta es *"¿qué riesgo estoy intentando reducir con cada nivel?"*, has respondido como arquitecto y no como usuario de herramientas.

📚 [Isaac Sim](https://docs.isaacsim.omniverse.nvidia.com/latest/index.html) · [Isaac Lab](https://isaac-sim.github.io/IsaacLab/main/index.html) · [Replicator](https://docs.omniverse.nvidia.com/extensions/latest/ext_replicator.html) · [Gazebo releases](https://gazebosim.org/docs/latest/releases/) · [ros_gz](https://github.com/gazebosim/ros_gz) · [Project Chrono](https://projectchrono.org/) · [Colosseum](https://github.com/CodexLabsLLC/Colosseum)

**Emparejamientos ROS 2 ↔ Gazebo** (dato útil y concreto): Jazzy↔Harmonic, Kilted↔Ionic, **Lyrical↔Jetty**, Rolling↔Jetty.

---

## 3. SiL, HiL y la pirámide de test

ARX busca literalmente un *Robotics SiL Simulation Engineer*. Ten clara la pirámide:

```
        ▲  campo real (caro, lento, no reproducible)
       ╱ ╲     ← lo mínimo imprescindible, y solo tras pasar todo lo de abajo
      ╱   ╲  HiL: hardware real en el lazo (ECU, sensores reales, timing real)
     ╱     ╲    ← captura problemas de integración y de tiempo
    ╱       ╲ SiL closed-loop: stack completo contra simulador
   ╱         ╲  ← el grueso de la validación funcional; barridos de escenarios
  ╱           ╲ Replay / open-loop sobre bags reales
 ╱             ╲ ← datos auténticos, sin dinámica. Detecta regresiones de percepción
╱               ╲ Component tests (un nodo con entradas grabadas) + unit tests
─────────────────  ← rápido, determinista, corre en cada commit
```

**Puntos de discusión que demuestran experiencia:**

- **El replay open-loop es el test más rentable y el más ignorado.** Coges bags reales de campo, los pasas por la percepción y comparas con el resultado anterior o con anotación. Detecta regresiones el mismo día, sin simulador y sin hardware. En ARX, con flota desplegada, es la primera cosa que montaría.
- **El salto de open-loop a closed-loop es donde aparecen los problemas de verdad**, porque en lazo cerrado los errores de percepción cambian la trayectoria y por tanto cambian lo que se percibe después. Un modelo que puntúa bien en mIoU puede navegar fatal.
- **Determinismo.** Un test que no es reproducible no es un test. En ROS 2 esto exige cuidado: orden de callbacks, timing, semillas aleatorias, `use_sim_time`. Merece la pena invertir en ello desde el principio.
- **HiL** importa especialmente cuando hay CAN, ECUs y latencias reales — ARX menciona CAN en sus vacantes.

---

## 4. Verificación basada en escenarios y cobertura

Este es el marco conceptual que eleva la respuesta de "hacemos pruebas" a "tenemos una estrategia de validación".

### La idea
En vez de escribir tests como demos concretas ("el robot esquiva esta roca"), **parametrizas el espacio de escenarios** y mides qué fracción has ejercitado:

- Parámetros de entorno: tipo de terreno, pendiente, densidad de vegetación, altura de vegetación, meteorología, hora del día, visibilidad, presencia de polvo.
- Parámetros de escenario: tipo de obstáculo, posición relativa, si aparece súbitamente, obstáculos negativos, terreno blando.
- Parámetros de sistema: velocidad comandada, payload montado, sensores degradados o fuera de servicio, latencia o pérdida del enlace.
- Parámetros de plataforma: GEREON vs HECTOR vs retrofit.

Después generas combinaciones (barrido factorial reducido, muestreo latin hypercube, o búsqueda dirigida hacia el fallo) y mides **cobertura**: qué porcentaje del espacio has ejercitado y dónde están los huecos.

### Estándares y vocabulario
- **ASAM OpenSCENARIO XML** (v1.3.1) — escenarios *concretos* en XML (`.xosc`).
- **ASAM OpenSCENARIO DSL** (v2.2.0) — lenguaje *declarativo y abstracto* para describir familias de escenarios y generar variantes automáticamente.
- **Dato fino que impresiona:** XML (1.x) y DSL (2.x) son **estándares independientes, no versiones sucesivas** — ASAM los separó formalmente. Mucha gente dice "OpenSCENARIO 2.0" como si fuera la siguiente versión de 1.x. No lo es.
- **OpenDRIVE** (v1.8.1) describe redes de carreteras — **y aquí está el problema honesto para off-road: no hay equivalente.** No existe un estándar de descripción de terreno no estructurado. Se trabaja con heightmaps, terreno procedural y ontologías propias. Decir esto demuestra que has pensado en el problema y no solo leído el vocabulario.

📚 [OpenSCENARIO XML](https://www.asam.net/standards/detail/openscenario-xml/) · [OpenSCENARIO DSL](https://www.asam.net/standards/detail/openscenario-dsl/) · [Survey on Scenario-Based Testing (arXiv:2112.00964)](https://arxiv.org/pdf/2112.00964)

### SOTIF (ISO 21448)
El marco mental más útil aunque no sea aplicable formalmente a un vehículo militar. Divide el espacio en cuatro áreas:

| | Seguro | Inseguro |
|---|---|---|
| **Conocido** | Área 1: validado | Área 2: identificado, hay que mitigar |
| **Desconocido** | Área 4 | **Área 3: los peligros que ni sabes que existen** |

Todo el trabajo de validación consiste en **encoger el área 3 moviéndola al área 2**, y luego mitigar el área 2 hacia el área 1. Y off-road el área 3 es enorme. Este marco te da una manera clara y profesional de responder a "¿cómo sabes que es seguro?": *no puedes probar que lo es; puedes demostrar que has reducido sistemáticamente lo desconocido y que tienes mecanismos que degradan con seguridad cuando aparece.*

📚 [Guía SOTIF de Jama (gratis)](https://www.jamasoftware.com/requirements-management-guide/automotive-engineering/sotif/) · [eBook LHP sobre ISO 21448 (PDF gratis)](https://www.lhpes.com/hubfs/LSS-eBook-PDF-The-Guide-to-SOTIF-ISO-21448.pdf)

---

## 5. Métricas de autonomía

Ten una lista propia y sé capaz de justificar cada una. Sin métricas, "mejoramos la autonomía" no significa nada.

**De misión:** tasa de éxito de misión, distancia media entre intervenciones del operador, tiempo hasta la primera intervención, % de la ruta en modo autónomo.

**De seguridad:** distancia mínima a obstáculo, margen de vuelco mínimo, número de eventos de e-stop, aceleraciones laterales máximas.

**De calidad de navegación:** coste real de la trayectoria vs óptimo, suavidad (jerk), oscilaciones de control, tiempo detenido sin causa.

**De percepción, y aquí está el matiz importante:** no basta con mIoU y AP. Hay que ponderar **por consecuencia**. Un falso positivo de traversability (creo que no puedo pasar y sí podía) te cuesta tiempo y frustra al operador. Un falso negativo (creo que puedo pasar y no podía) te vuelca el vehículo. **No son el mismo error y la métrica no debe tratarlos igual.** Diseña una métrica asimétrica ponderada por coste operacional — es una de las cosas más "senior" que puedes proponer.

**De sistema:** latencia p99 sensor→actuador (no la media), uso de CPU/GPU, temperatura, consumo.

---

## 6. El sim2real gap

Dónde está realmente, en orden de importancia off-road:

1. **Dinámica de contacto suelo-oruga.** Es el gap más grande y el menos reconocido. Los simuladores generales modelan terreno rígido; el barro, la arena y la nieve se comportan de otra manera. Chrono es la excepción.
2. **Modelos de sensor.** El ruido del LiDAR, los múltiples ecos en vegetación, el comportamiento en polvo y lluvia. Isaac Sim con RTX LiDAR es lo mejor disponible, pero sigue siendo una aproximación.
3. **Apariencia visual de la vegetación.** Muy difícil de sintetizar de forma convincente. Por eso los datos sintéticos funcionan mejor para geometría y LiDAR que para modelos basados en RGB — un matiz honesto que te distingue de quien vende datos sintéticos como panacea.

**Cómo se mide el gap** (y esto es lo que casi nadie sabe responder): conduces la misma trayectoria en campo y en sim, con las mismas entradas, y comparas — trayectoria ejecutada, salidas de percepción, señales del sensor. La divergencia cuantifica el gap. Luego calibras el modelo de sensor y de dinámica contra datos reales hasta que la divergencia baja de un umbral. Sin esa medida, la simulación es fe.

**Domain randomization** para cerrar el appearance gap: aleatorizar texturas, iluminación, condiciones atmosféricas y posiciones para que el modelo no dependa de detalles que la sim no reproduce bien.

---

## 7. Datos sintéticos: para qué sí y para qué no

**Sí, y muy bien:**
- Clases raras y peligrosas de recoger: obstáculos negativos profundos, alambradas, cráteres, vehículos volcados, minas visibles.
- Geometría y LiDAR (el gap es menor).
- Casos de degradación de sensores.
- Ground truth perfecta y gratuita: segmentación, profundidad, poses, oclusión — cosas que anotar a mano cuesta una fortuna.
- Cobertura sistemática de condiciones (iluminación × meteorología × pendiente).

**No, o con mucha cautela:**
- Sustituir el dataset real de apariencia visual.
- Validar comportamiento de misión sin ninguna evidencia de campo.
- Reclamar rendimiento en el mundo real basándose solo en métricas de sim.

**Enfoque recomendado:** sintético para *ampliar* la cola larga, real para *anclar* la distribución principal, y siempre un conjunto de test compuesto exclusivamente por datos reales de campo que nunca se usa para entrenar.

📚 [Omniverse Replicator](https://docs.omniverse.nvidia.com/extensions/latest/ext_replicator.html)

---

## 8. Autoevaluación

1. ¿Qué validarías en simulación y qué te negarías a validar solo en simulación?
2. Diseña la pirámide de test para un cliente que hoy solo prueba en campo.
3. ¿Por qué un modelo con buen mIoU puede navegar mal, y cómo lo detectas antes del campo?
4. ¿Cómo mides cuantitativamente el sim2real gap?
5. ¿Qué es la cobertura de escenarios y cómo la calcularías off-road sin un estándar tipo OpenDRIVE?
6. Explica las cuatro áreas de SOTIF y qué significa "reducir el área 3".
7. ¿Por qué un falso negativo de traversability y un falso positivo no deben pesar igual en tu métrica?
8. Tienes un presupuesto para *una* inversión en simulación este trimestre. ¿En qué la gastas y por qué?
