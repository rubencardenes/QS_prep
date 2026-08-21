# Dossier ARX Robotics — lo esencial para la entrevista

*Verificado en agosto de 2026. Todo lleva fuente. Lo que no pude confirmar está marcado como tal — no lo afirmes.*

---

## 1. Quiénes son, en cinco líneas

Fundada en **2022** como spin-off de las Fuerzas Armadas alemanas por tres ex-Bundeswehr: **Marc Wietfeld** (CEO), **Maximilian Wied** (CFO) y **Stefan Röbel** (COO). Sede registrada en **Oberding, Baviera** (aunque comunican "Múnich"). CTO desde 2025: **Ciaran Murphy**. Financiación total verificada: **€42M** — pre-seed €1,15M (Project A), seed €9M (**NATO Innovation Fund**), Serie A €31M (HV Capital, abr-2025) y extensión de €11M (Speedinvest). Se posicionan como **"neo prime" europeo**. ([inversores](https://www.arx-robotics.com/investors), [about](https://www.arx-robotics.com/about))

En junio de 2026 anunciaron nueva sede y planta en Múnich (capacidad ×5 a fin de año), oficina en Berlín, y operaciones ampliadas en Ucrania y Reino Unido. Planean **duplicar plantilla** a finales de 2026. ([expansión](https://www.arx-robotics.com/article/arx-robotics-enters-next-phase-of-expansion-with-industrial-scale-up-and-new-brand-identity), [Army Technology](https://www.army-technology.com/news/arx-robotics-growth-strategy/))

---

## 2. Producto — los tres nombres que tienes que saber

**GEREON** — UGV mediano de orugas. 500 kg de carga, 15 km/h, 40 km de autonomía, 72 h de operación, **control hasta 4 km**, cámaras térmicas, modos manual y autónomo, sistema modular de accesorios. Es el producto en volumen: producción en serie con DEUTZ en Ulm desde julio de 2026, primeras entregas a Ucrania a finales de verano de 2026. ([Gereon](https://www.arx-robotics.com/gereon), [DEUTZ](https://www.deutz.com/en/news/press-releases/news-detail/deutz-and-arx-robotics-launch-first-series-production-of-the-unmanned-ground-system-gereon/))

**HECTOR** — UGV rodado de clase media, **opcionalmente tripulado**. Combustión: 70 km/h, 100 km (500 extendido), 1.000 kg de carga; eléctrico: 70 km/h, 500 kg. Interfaces de payload abiertas. Construido **sobre Mithra OS**, y su ficha usa el término **"supervised autonomy"**. ([Hector](https://www.arx-robotics.com/hector))

**MITHRA OS** — *este es el nombre que más importa*. Es su capa de software "defense defined by software": convierte flotas heredadas y modernas en plataformas conectadas mediante un **Autonomy Kit** retrofit (cámaras + sensores + cómputo) que se monta sobre camiones militares existentes. Capacidades declaradas: fusión de sensores, conciencia situacional, **actualizaciones OTA**, "Legacy Autonomy Framework", interconectividad y swarming. ([Mithra OS](https://www.arx-robotics.com/mithra-os), [TechCrunch](https://techcrunch.com/2024/12/05/arx-launches-firestick-like-platform-to-make-military-trucks-autonomous))

**Su tesis de negocio en una frase:** *escalar no reemplazando sistemas, sino actualizándolos por software.* Si entiendes esto, entiendes por qué contratan un perfil de autonomía: Mithra OS solo vale lo que valga la autonomía que corre encima.

**Nivel de autonomía real:** no publican ningún nivel formal (ni SAE ni NATO ACL). Lo verificable: manual + autónomo, teleoperación hasta 4 km, y "supervised autonomy" en Hector. Términos como "swarming", "manned-unmanned teaming" y "battle-proven autonomy" son marketing sin evidencia técnica pública. **Esto confirma exactamente la premisa de la oferta:** hoy operan mayoritariamente teleoperados y el salto a autonomía está por hacer. Tú vas a ese salto.

---

## 3. El stack técnico real (deducido de sus ofertas de empleo)

Esto es lo más accionable del dossier. Sus vacantes en Greenhouse son inusualmente explícitas ([bolsa de empleo](https://job-boards.eu.greenhouse.io/arxroboticsgmbh)):

| Área | Lo que piden literalmente |
|---|---|
| **Núcleo** | **C++ + ROS 2 + Linux**; Python; **Rust "beneficial"** |
| **Localización** | EKF, UKF, filtros de partículas, **SLAM basado en factor graphs**, odometría visual, navegación inercial, entornos **GPS-denied** |
| **Sensores** | LiDAR, cámaras, **radar**, IMU, GNSS, magnetómetros |
| **Percepción** | **PyTorch, TensorRT, OpenCV, PCL, Open3D**; clasificación de terreno, segmentación, **traversability estimation off-road** (textual) |
| **Navegación** | **Behavior trees / máquinas de estado**, occupancy grids, cost maps, planners global y local |
| **Infra** | **Docker, CI/CD, CUDA**, optimización edge, CAN / Ethernet / TCP-UDP / serie |

**El hallazgo más útil:** existe un departamento llamado **"Autonomy & VVT"** (Verification, Validation & Test) con ~16 vacantes, entre ellas **Robotics SiL Simulation Engineer**, **Senior Data Engineer Simulation & Synthetic** y **Staff Engineer Data Loop**.

Traducción: **ya han decidido** que su estrategia es *simulación software-in-the-loop + un data loop de reentrenamiento*. No tienes que venderles la idea — tienes que demostrar que sabes construirla. Habla de *data loop* y de *SiL* con esas palabras: son las suyas.

**No verificado:** ningún anuncio nombra explícitamente **Jetson** (solo "edge computing" + CUDA) ni **qué simulador** usan (Isaac Sim / Gazebo / CARLA / Unreal). Son dos preguntas excelentes para hacerles tú.

**Trampa de GitHub:** la organización `github.com/ARXroboticsX` **no es esta empresa** — es ARX (Beijing) Technology, de brazos robóticos. ARX Robotics GmbH **no tiene repos públicos**. No menciones haber mirado su código.

---

## 4. Socios y contratos (para citar con precisión)

- **Helsing** — alianza estratégica ISR-strike (sep-2025); después demostraron una cadena Recce-Strike completa **GEREON + munición merodeadora HX-2** en el ejercicio Haraka Storm en Kenia con fuerzas británicas. ([Helsing](https://helsing.ai/newsroom/helsing-and-arx-robotics-announce-strategic-partnership))
- **DEUTZ** — producción en serie de GEREON en Ulm (jul-2026). También anunció en oct-2025 intención de entrar como inversor líder; **el cierre de esa ronda no está confirmado públicamente**.
- **RENK** — movilidad + Mithra OS para digitalizar flotas. **Daimler Truck** — alianza *planeada* (mar-2025). **Supacat (UK)** — MoU de teaming tripulado-no tripulado.
- **Roboneers (Ucrania)** — JV **ARX Industries** (jun-2026) para producir el UGV **Rys Pro** en plantas alemanas y ucranianas.
- **UK MoD / Task Force RAPSTONE** — **contrato confirmado** de GEREON en configuración ISR para el British Army (abr-2026); inversión de £45M y planta en el suroeste de Inglaterra con objetivo de 1.800 vehículos/año.
- **Ucrania** — contrato para varios cientos de GEREON adicionales. Afirman ser "el mayor proveedor de UGV occidentales a Ucrania" (afirmación propia).
- **EDA / HEDI** y **US Army Project Convergence Capstone 6** (Fort Irwin, ago-2026).

**⚠️ Dos cosas que NO debes dar por hechas:**
1. **No hay contrato Bundeswehr confirmado.** Lo único documentado es que están *en carrera* por una adquisición de drones de €900M del BMVg. Si dices "vuestro contrato con la Bundeswehr", quedas mal.
2. **Ni Rheinmetall ni KNDS** son socios suyos. Sus tier-1 son DEUTZ, RENK, Daimler Truck y Supacat.

---

## 5. Qué significa todo esto para tu candidatura

**Por qué existe este puesto (tu hipótesis de trabajo):** están escalando producción muy rápido (Ucrania, UK, US) con un producto cuyo diferencial declarado es el software, pero cuya autonomía real es todavía teleoperación + funciones asistidas. Tienen ~50 vacantes abiertas y no pueden esperar a contratar en plantilla. Traen un freelance senior para **acelerar el salto de autonomía y dejar método instalado** — de ahí lo de "Wissenstransfer" y los 9-12 meses.

**Tus tres ángulos más fuertes con ellos:**

1. **El data loop desde la flota desplegada.** Tienen cientos de GEREON operando en Ucrania y en ejercicios reales, teleoperados. Eso es un volumen de datos de campo en condiciones auténticas que casi nadie tiene. La pregunta correcta no es "¿cómo entrenamos un modelo?" sino "¿cómo cerramos el bucle desde el vehículo desplegado hasta el reentrenamiento, con datos que no pueden salir del perímetro?". Ya tienen un *Staff Engineer Data Loop* buscado — hablas su idioma.
2. **GPS-denied + off-road.** Sus vacantes lo piden explícitamente. Ucrania es un entorno de jamming intensivo. Prepara bien LiDAR-inertial odometry, factor graphs y detección de deriva.
3. **Multi-plataforma es su problema estructural.** Mithra OS tiene que correr sobre GEREON (orugas, 15 km/h), HECTOR (ruedas, 70 km/h), Rys Pro y camiones retrofitados. Eso convierte la **abstracción de plataforma** en un problema de arquitectura de primer orden: el mismo stack de percepción y comportamiento debe parametrizarse por cinemática, dinámica, sensórica y perfil de misión. Muy poca gente les hablará de esto, y es exactamente lo que espera un cliente que busca a alguien que "impulse decisiones de arquitectura".

**Cinco datos para citar y quedar bien** (uno basta, no los sueltes todos):
- Mithra OS y el concepto de Autonomy Kit retrofit sobre flotas heredadas.
- El contraste GEREON (500 kg, 15 km/h, orugas) vs HECTOR (1.000 kg, 70 km/h, ruedas, opcionalmente tripulado) como reto de generalización del stack.
- La cadena Recce-Strike con Helsing en Haraka Storm.
- Producción en serie con DEUTZ en Ulm y el contrato RAPSTONE del UK MoD.
- Que respaldó la seed el **NATO Innovation Fund**.

---

## 6. Preguntas específicas para hacerles a ellos

1. ¿Mithra OS corre el mismo stack de autonomía en GEREON y en HECTOR, o hay ramas por plataforma? ¿Cómo gestionáis la abstracción de cinemática y sensórica?
2. ¿En qué distro de ROS 2 estáis? Con Kilted en EOL en diciembre, ¿hay plan de migración a Lyrical?
3. ¿Qué simulador usáis en el equipo de Autonomy & VVT, y para qué exactamente — percepción, dinámica, o regresión en CI?
4. Con flota desplegada en Ucrania: ¿qué datos vuelven realmente al ciclo de desarrollo, y con qué restricciones de clasificación?
5. ¿Anotáis internamente o con proveedor externo? ¿Los datos pueden salir del perímetro?
6. ¿Cuál es el objetivo concreto de autonomía a 12 meses — waypoint following supervisado, convoy following, retorno autónomo, exploración?
7. ¿Cómo se reparte hoy el equipo entre percepción, planificación y VVT, y dónde está el cuello de botella?
8. ¿El puesto requiere Sicherheitsüberprüfung, y hay restricciones para trabajar en remoto con datos de programa?
9. ¿Qué acceso tendré a hardware y con qué frecuencia hay ventanas de test en campo?
10. ¿Cómo medís hoy si una función autónoma está lista para desplegarse?
