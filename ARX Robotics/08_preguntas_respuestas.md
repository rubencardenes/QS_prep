# 40 preguntas de entrevista con guion de respuesta

*Practica **en voz alta y cronometrado**. Objetivo: 90–120 segundos por respuesta técnica, 2–3 minutos por las de proceso. Leerlas no sirve; decirlas sí.*

---

## A. Percepción off-road (1–10)

**1. ¿Qué cambia respecto al coche autónomo en carretera?**
Cinco ejes: (a) no hay estructura previa — sin carriles, sin mapas HD, sin OpenDRIVE, el mapa *es* el terreno; (b) la representación primaria pasa de detección de objetos a estimación de transitabilidad; (c) la geometría es ambigua — hierba y roca tienen la misma firma, hay que añadir semántica y propiedades físicas; (d) existen obstáculos negativos y el suelo es el riesgo; (e) percepción degradada y GNSS denegado. Y un sexto que casi nadie menciona: el modelo de operación es un continuo teleop→autonomía, no un interruptor.

**2. ¿Cómo estimarías transitabilidad en bosque con hierba alta?**
Tres capas estratificadas. Geométrica sobre elevation map (pendiente, step, rugosidad) como veto duro y arranque inmediato. Semántica para desambiguar vegetación atravesable de obstáculo oculto. Propioceptiva/auto-supervisada para calibrar el coste con la física real del vehículo — vibración del IMU, consumo, slip de orugas, proyectados hacia atrás sobre lo que veía. Todo con incertidumbre propagada, y la capa de comportamiento reaccionando explícitamente a ella.

**3. ¿Cómo detectas obstáculos negativos con LiDAR montado bajo?**
Es detectar *ausencia*, no presencia. Sombras de rango: donde el modelo de suelo predice retorno y no lo hay, hay un hueco o una oclusión. Discontinuidad en el perfil de rango. Estéreo o cámara con textura como complemento. Y la política correcta: **lo no observado no es transitable por defecto**, con la velocidad limitada por el alcance efectivo de detección. Hay un modelo analítico (Sensors 2021) que relaciona densidad angular del LiDAR y distancia con el tamaño mínimo de hueco detectable — sirve para dimensionar el sensor y para justificar el límite de velocidad.

**4. El robot se para constantemente ante hierba alta. Diagnóstico.**
No especular: mirar datos. Tres hipótesis. (a) La capa geométrica trata cualquier elevación como obstáculo — se comprueba visualizando el costmap sobre el bag. (b) La semántica no tiene clase de vegetación atravesable, o la tiene y falla en esas condiciones — se comprueba con métricas por clase en esos frames. (c) El inflation/margen del planificador es demasiado conservador — se comprueba comparando costmap y trayectoria. Las tres se distinguen con el mismo bag y media hora. La solución de fondo es semántica + propiocepción, pero el parche inmediato suele ser un umbral de altura con histéresis.

**5. Cámara, LiDAR y radar: ¿cómo los fusionas y qué pasa si uno falla?**
Early / mid (BEV) / late, con distintos compromisos de latencia y robustez. Lo importante es la **degradación elegante**: si la cámara se ciega por polvo, el sistema no debe fallar sino pasar a un modo LiDAR+radar con velocidad reducida y margen ampliado. Eso exige que la fusión sepa qué sensores están sanos, lo cual exige monitorización de salud de sensor como componente propio. La fusión tardía es más robusta a fallo de un sensor; la intermedia da más rendimiento. Empezaría por tardía y migraría donde el rendimiento lo justifique.

**6. Un LiDAR de 10 Hz a 15 km/h en terreno accidentado: ¿qué corrección aplicas?**
Deskewing / motion compensation con la IMU. El barrido tarda ~100 ms, en los que el vehículo avanza ~40 cm y además cabecea. Sin corregir, la nube sale distorsionada y contamina el mapa, la calibración aparente y la odometría. Requiere sincronización temporal fiable — y hay que distinguir el timestamp del sensor, el del driver y el de publicación DDS.

**7. ¿Cómo mantienes la localización sin GNSS durante 20 minutos?**
LiDAR-inertial odometry (FAST-LIO2 o LIO-SAM) con preintegración de IMU, en un factor graph que permita cierres de bucle. La deriva es inevitable: lo que importa es acotarla y **saber que está ocurriendo**. Detección de degeneración geométrica (campo abierto plano, pasillo forestal uniforme) mirando el condicionamiento de la matriz de información. Odometría de orugas con modelo de slip como restricción adicional. Y relocalización contra mapa previo si existe. Además, detección de spoofing: si el GNSS reaparece y es inconsistente con la odometría, no confiar en él automáticamente.

**8. ¿Qué le pides al radar que no te dan cámara y LiDAR?**
Penetración de polvo, humo, niebla y lluvia, y velocidad Doppler directa. En un teatro como Ucrania eso no es marginal. A cambio: baja resolución angular, mucho clutter en terreno y multipath. Lo usaría como *veto de seguridad* a corta distancia y para detección de objetos en movimiento en condiciones donde los otros dos están ciegos, no como sensor primario de geometría.

**9. ¿Por qué importa la incertidumbre epistémica?**
Porque en terreno no estructurado lo out-of-distribution es la norma. La aleatoria es ruido irreducible; la epistémica dice "esto es nuevo, no lo he visto". Solo esta última justifica un cambio de comportamiento. Métodos: ensembles, MC-dropout, y evidential deep learning —el más apropiado para embarcado, una sola pasada—. Y calibrarla: un 90% de confianza debe acertar el 90%.

**10. ¿Qué haces cuando la percepción no está segura?**
No es una pregunta de percepción, es de arquitectura, y ahí está la gracia. La salida de percepción no debería ser un coste sino una distribución sobre el coste, y el planificador debe optimizar contra un cuantil (CVaR), no contra la media — porque el error es asimétrico: un falso positivo te frena, un falso negativo te vuelca. Las respuestas escalonadas son: reducir velocidad, ampliar margen, aproximarse para observar mejor, pedir confirmación al teleoperador, detenerse.

---

## B. ROS 2 y arquitectura (11–18)

**11. ¿En qué distro estáis y por qué importa?**
Lyrical Luth es la LTS activa desde mayo de 2026 (EOL 2031, Ubuntu 26.04). Jazzy es la LTS madura con más soporte de terceros. **Kilted muere en diciembre de 2026** — si estáis ahí, la migración es una decisión de este trimestre.

**12. Un suscriptor no recibe nada aunque el tópico existe.**
En orden: (a) incompatibilidad de QoS — un suscriptor reliable no se empareja con un publicador best-effort, es la causa nº1; (b) descubrimiento — ROS_DOMAIN_ID distinto, o multicast bloqueado en la red de campo; (c) tipos de mensaje distintos; (d) el nodo no está en un executor que lo gire, o hay un callback bloqueando. `ros2 topic info -v` da lo primero en segundos.

**13. Explica un deadlock por callback groups.**
Llamar a un servicio y esperar el resultado desde dentro de un callback, con executor single-threaded: el executor está ocupado en el callback y nunca puede procesar la respuesta. Solución: cliente en un callback group reentrante con executor multihilo, o —mejor— no bloquear: usar el patrón asíncrono y una máquina de estados.

**14. Zero-copy y por qué no funciona con PointCloud2.**
El zero-copy entre procesos usa loaned messages sobre memoria compartida, y exige mensajes de tamaño fijo (POD). `PointCloud2` tiene un array de tamaño variable, así que no aplica directamente. Dentro del mismo proceso sí se puede evitar la copia con intra-process comms y `unique_ptr`. En la práctica: componer los nodos de percepción en un único proceso. Hay un paper de Macenski et al. (RA-L 2023) que cuantifica la ganancia.

**15. ¿Qué te da Zenoh que no te da DDS en un enlace de 4 km?**
El descubrimiento DDS multicast se comporta mal en redes inalámbricas con pérdidas y particiones. Zenoh usa una arquitectura de routers, tolera enlaces intermitentes y escala mejor entre robot y estación. Para el enlace vehículo↔teleoperación es el argumento fuerte. Su Tier-1 en ROS 2 ya está cerrado.

**16. ¿Dónde pones la frontera con el tiempo real duro?**
ROS 2 con PREEMPT_RT, mlockall, SCHED_FIFO y aislamiento de CPU da latencias acotadas para lazos blandos. El lazo de control duro de bajo nivel vive fuera: microcontrolador o controlador de la plataforma, con su propio watchdog. Saber dónde está esa frontera es más importante que optimizar ROS 2 hasta el límite.

**17. Dibuja la arquitectura del stack.**
*(Practícalo en papel — ver Dossier 2, sección 3. Sensores→sync→state estimation→mapa local multicapa con incertidumbre→behavior BT→global planner→MPPI→ros2_control, con safety monitor independiente, capa de teleop/HMI y observabilidad transversal.)*

**18. ¿Cómo haces que el mismo stack corra en GEREON y en HECTOR?** ⭐
Esta es tu pregunta estrella con ARX. El modelo de vehículo debe ser **configuración, no código**: cinemática (orugas skid-steer vs ruedas Ackermann), footprint, límites de pendiente y velocidad, modelo de slip, altura y posición de sensores, y perfil de misión. Encima, una capa de abstracción de sensores para que percepción no dependa del modelo concreto de LiDAR. Los umbrales de traversability se derivan de la física del vehículo, no se codifican. Y —lo que la gente olvida— si los payloads son intercambiables, el centro de masas y por tanto los márgenes de vuelco cambian con la configuración montada: eso también es configuración en caliente.

---

## C. Behavior y control (19–25)

**19. ¿BT o FSM?**
BT para lógica de misión y arbitraje: composable, reactivo por el tick desde la raíz, legible para no-programadores. FSM pequeña y explícita para los modos operacionales, porque ahí las transiciones son pocas y quieres razonar sobre ellas. Los límites del BT: el blackboard degenera en variables globales y la concurrencia con recursos compartidos se expresa mal. Y el safety monitor fuera de ambos.

**20. ¿Qué haces al perder el enlace?**
Depende de la misión y debe ser configurable y conocido por el operador *antes*. Parar en seco es seguro pero convierte el vehículo en blanco estático y obstáculo. Continuar al último waypoint es útil pero arriesgado si el entorno cambió. Mi opción por defecto sería **breadcrumb return** —volver por la ruta ya recorrida hasta recuperar enlace— porque ese terreno ya demostró ser transitable. Con temporizador, comportamiento por defecto conservador y transparencia total hacia el operador.

**21. ¿Por qué MPPI y no DWA?**
MPPI muestrea miles de secuencias de control, las rueda por un modelo de dinámica y pondera exponencialmente por coste. No exige que el coste sea diferenciable ni convexo, así que puedes meterle un costmap de traversability aprendido con discontinuidades. Maneja dinámica no lineal, incluido un modelo de slip aprendido. Paraleliza en GPU. Está en Nav2 y mantenido. DWA asume dinámicas simples y un costmap prácticamente binario.

**22. ¿Qué conservas y qué sustituyes de Nav2 off-road?**
Conservo el framework de plugins, el BT Navigator y su gestión de lifecycle, y el MPPI. Sustituyo el costmap 2D binario con supuesto de suelo plano por una capa propia que consuma el mapa multicapa de traversability, el modelo de coste binario por uno continuo, y reviso las recovery behaviors — girar sobre sí mismo puede ser peligroso en pendiente lateral.

**23. ¿Por qué el modelo differential-drive ideal falla en orugas?**
Porque una oruga gira deslizando: el centro instantáneo de rotación no está en el eje y se desplaza según terreno, carga, velocidad y radio de giro. El error es sistemático y crece con el giro y con lo blando del terreno. Se corrige con factores empíricos identificados experimentalmente (Mandow et al.), con un modelo de slip estimado online comparando comando contra odometría LIO, o con un modelo de dinámica aprendido dentro del MPPI. Y el residuo de ese error *es* una medida de la tracción del terreno — se realimenta a la percepción.

**24. ¿Dónde meterías aprendizaje y dónde no?**
En orden de riesgo: modelo de dinámica dentro de MPPI (bajo riesgo, alto retorno, datos ya disponibles) → coste aprendido desde demostraciones de teleoperación por IRL → control residual acotado sobre un controlador clásico. RL end-to-end no, aquí: sim2real muy duro en contacto suelo-oruga, difícil de certificar y de depurar. Decir que no a algo con buenas razones vale más que decir que sí a todo.

**25. Diseña el limitador de velocidad basado en percepción.**
Velocidad máxima como mínimo de varios términos: por pendiente longitudinal y lateral (margen de vuelco), por rugosidad (confort y vibración del hardware), por alcance efectivo de detección (no ir más rápido de lo que puedes frenar dentro de lo observado — esto cubre los obstáculos negativos), y por **confianza de la percepción** (si la incertidumbre epistémica sube, la velocidad baja). Con histéresis para no oscilar, y mostrado al operador para que entienda por qué el vehículo va lento.

---

## D. Simulación y validación (26–31)

**26. ¿Qué validarías en sim y qué no?**
En sim: lógica de comportamiento, planificación, cobertura de escenarios geométricos, regresiones de integración, casos peligrosos que no puedes provocar. Nunca solo en sim: rendimiento absoluto de percepción visual, dinámica sobre terreno deformable sin validación experimental, y cualquier afirmación de seguridad para despliegue. La sim reduce el número de iteraciones en campo; no las elimina.

**27. Diseña la estrategia de test para un cliente que solo prueba en campo.**
Pirámide: unit y component tests en cada commit → **replay open-loop sobre bags reales** (lo más rentable y lo que montaría primero: detecta regresiones de percepción el mismo día, sin simulador ni hardware) → SiL closed-loop con barridos de escenarios → HiL para timing y CAN → campo restringido → operación. Con determinismo cuidado en cada nivel, porque un test no reproducible no es un test.

**28. Un modelo con buen mIoU navega mal. ¿Por qué?**
Porque mIoU promedia sobre píxeles y el fallo que importa está concentrado: pocas celdas, en la trayectoria, de la clase equivocada. Y porque el open-loop no captura que en lazo cerrado el error de percepción cambia la trayectoria y por tanto lo que se percibe después. Se detecta con métricas ponderadas por consecuencia y con test en lazo cerrado, no con más mIoU.

**29. ¿Cómo mides el sim2real gap?**
Conduces la misma trayectoria con las mismas entradas en campo y en sim, y comparas: trayectoria ejecutada, salidas de percepción, señales crudas de sensor. La divergencia lo cuantifica. Luego calibras los modelos de sensor y de dinámica contra datos reales hasta bajar de un umbral. Sin esa medida, la simulación es un acto de fe.

**30. ¿Qué es cobertura de escenarios sin un estándar tipo OpenDRIVE?**
Parametrizas el espacio: terreno, pendiente, vegetación, meteorología, visibilidad, tipo de obstáculo, velocidad, payload, sensores degradados, plataforma. Generas combinaciones por muestreo o búsqueda dirigida al fallo, y mides qué fracción has ejercitado y dónde están los huecos. El vocabulario viene de OpenSCENARIO DSL —que, por cierto, es un estándar independiente de OpenSCENARIO XML, no su siguiente versión—. Para off-road no hay equivalente a OpenDRIVE: se trabaja con heightmaps, terreno procedural y una ontología propia. Ese hueco es parte del problema.

**31. ¿Cómo sabes que es seguro?**
No puedes probar que lo es. Puedes demostrar que has reducido sistemáticamente lo desconocido. El marco de SOTIF ayuda: cuatro áreas según conocido/desconocido × seguro/inseguro; el trabajo consiste en mover el área 3 —peligros que ni sabes que existen— al área 2, y mitigar el 2 hacia el 1. Off-road el área 3 es enorme, así que el argumento de seguridad se apoya tanto en la cobertura como en los mecanismos de degradación segura y en el humano en el bucle.

---

## E. Datos y anotación (32–35)

**32. ¿Cómo montas un proceso de anotación desde cero?**
*(Guion de 5 min — ver Dossier 5, sección 3: auditar → arreglar la fuente (metadata, calibración versionada, política de grabación por eventos) → ontología partiendo de GOOSE + guía + herramienta on-premise + QA desde el primer día → escalar con auto-labeling, active learning y honeypots, cerrando el bucle con las intervenciones del teleoperador.)*

**33. Los datos no pueden salir de la empresa. ¿Qué cambia?**
Todo lo operativo. Herramienta self-hosted (CVAT), anotadores internos autorizados, infraestructura de cómputo on-premise, y por tanto un coste por frame mucho mayor. Eso hace que **la curación y el auto-labeling dejen de ser optimizaciones y pasen a ser la estrategia**: si cada etiqueta cuesta tres veces más, seleccionar bien qué anotas triplica tu presupuesto efectivo. Y empuja fuerte hacia la traversability auto-supervisada, que no necesita anotadores.

**34. ¿Cómo aseguras la calidad sin revisarlo todo?**
Golden set anotado por experto, honeypots invisibles inyectados en el flujo normal, solapamiento deliberado de un porcentaje de tareas para medir acuerdo inter-anotador (kappa, Krippendorff's alpha, mIoU entre anotadores), y revisión por muestreo estadístico con umbral definido de antemano. Y el punto clave: **los desacuerdos recurrentes indican una ontología mal definida, no anotadores malos** — auditar la guía a partir de ellos es un mecanismo de mejora.

**35. ¿Cuál es el error de partición train/test típico en robótica?**
Partir por frame. Frames consecutivos son casi idénticos, así que el test acaba lleno de casi-copias del train y la métrica sale inflada; te enteras en campo. Hay que partir por sesión, por localización y, si se puede, por estación del año.

---

## F. Senioridad, proceso y freelance (36–40)

**36. Tus primeros 30/60/90 días.** ⭐ *La pregunta que decide.*
- **1–30: escuchar y medir.** Auditar el stack, los bags existentes y su metadata, la infraestructura de calibración y sincronización. Entregable: documento de arquitectura y riesgos, más un baseline de métricas donde hoy no hay ninguna. Y una **victoria rápida visible**: teleoperación asistida con veto de obstáculos y limitación de velocidad por terreno — mejora la seguridad, reduce la carga del operador, no exige que nadie confíe todavía en la autonomía, y empieza a generar dataset.
- **31–60:** pipeline de datos funcionando, banco de simulación mínimo con replay de bags en CI, y traversability geométrica en el vehículo con métricas y tests de regresión automatizados.
- **61–90:** capa semántica o auto-supervisada entrenada con la primera tanda de datos, integrada con la planificación local; primeras misiones de waypoints supervisadas en campo restringido; metodología documentada y transferida.

**37. ¿Cómo convences al equipo de una decisión con la que no están de acuerdo?**
Primero entender por qué discrepan — normalmente saben algo del contexto que yo no. Después, convertir la discusión en algo decidible: definir el criterio *antes* de discutir la opción, y si el desacuerdo persiste, hacer un experimento acotado en vez de un debate. Documentar la decisión con las alternativas descartadas (un ADR) para que dentro de seis meses nadie tenga que reconstruirla. Y aceptar que a veces la decisión reversible mal tomada rápido vale más que la perfecta tarde.

**38. ¿Cómo aseguras la transferencia sabiendo que te vas en 12 meses?**
Nada de componentes de los que solo yo sepa. Documentación de decisiones (ADRs), no solo de código. Tests como especificación ejecutable. Pairing sistemático en lo nuevo. Y una regla que aplico: cada cosa que construyo la construyo con alguien del equipo, aunque sea más lento. La métrica de éxito de un freelance senior no es lo que entrega, es lo que el equipo puede seguir haciendo sin él.

**39. ¿Por qué freelance y no en plantilla?**
*(Prepara tu versión honesta. Marco útil: encaja con proyectos de transformación acotados donde el valor está en instalar método y capacidad, no en mantener. Y menciona que trabajas con más de un cliente — importa por Scheinselbständigkeit.)*

**40. Tarifa y disponibilidad.**
Ten una cifra y un mínimo decididos **antes** de la conversación, y dilos sin titubear ni justificarte de más. Investiga rangos actuales en Freelancermap o GULP para perfiles senior de autonomía/ML en defensa en Alemania. Ten claro también: la logística y el coste del día presencial en Múnich, si los gastos van aparte, y el riesgo de **Scheinselbständigkeit** — jornada completa, 9–12 meses, un solo cliente y presencia semanal es exactamente el patrón que la Deutsche Rentenversicherung examina. Poder hablarlo con naturalidad (contrato de servicio bien redactado, sin integración en la jerarquía, capacidad de tener otros clientes) te hace parecer un profesional establecido, no un empleado encubierto.

---

## Vocabulario alemán imprescindible

*La entrevista pide "Deutsch und Englisch". Aunque lo técnico vaya en inglés, prepara 2 minutos de autopresentación en alemán.*

| Alemán | Español |
|---|---|
| **Regelung** vs **Steuerung** | control en lazo cerrado vs mando en lazo abierto — **la distinción que delata a quien no ha trabajado técnicamente en alemán** |
| Umfelderfassung | percepción del entorno |
| Befahrbarkeit | transitabilidad (traversability) |
| Geländeoberflächenerfassung | detección de la superficie del terreno |
| Hinderniserkennung | detección de obstáculos |
| Sensordatenfusion | fusión de datos de sensores |
| Zustandsschätzung | estimación de estado |
| Bahnplanung / Trajektorienplanung | planificación de trayectorias |
| Ausweichmanöver | maniobra evasiva |
| Simulationsumgebung | entorno de simulación |
| Datenannotation / Beschriftung | anotación de datos |
| Qualitätssicherung | aseguramiento de la calidad |
| Wissenstransfer | transferencia de conocimiento |
| Kettenfahrzeug / Radfahrzeug | vehículo de orugas / de ruedas |
| Fernsteuerung / Teleoperation | control remoto / teleoperación |
| unstrukturiertes Gelände | terreno no estructurado |
| Sicherheitsüberprüfung (Ü1/Ü2/Ü3) | habilitación de seguridad |
| Scheinselbständigkeit | falsa autonomía laboral |
