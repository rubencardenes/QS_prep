# Material de estudio — Entrevista ARX Robotics
### Senior ML/Autonomy Engineer — Perception & Behavior/Control

Confirmado: **el cliente es ARX Robotics** (Oberding / Múnich). Todo el material está reorientado a ellos.

---

## Cómo usar este material

| Archivo | Qué es | Cuándo leerlo |
|---|---|---|
| `01_dossier_ARX.md` | Brief de empresa: producto, stack real deducido de sus ofertas, socios, trampas | **Primero, hoy mismo.** Cambia cómo preparas todo lo demás |
| `02_percepcion_offroad.md` | Dossier de estudio: traversability, sensores, calibración, incertidumbre | Día 2 |
| `03_ros2_arquitectura.md` | Dossier: ROS 2 senior + arquitectura de stack de autonomía | Día 3 |
| `04_behavior_control.md` | Dossier: behavior trees, planners, MPPI, control de orugas | Día 4 |
| `05_simulacion_validacion.md` | Dossier: simuladores, SiL, verificación por escenarios, SOTIF | Día 5 |
| `06_datos_labeling.md` | Dossier: pipeline de anotación, QA, data loop | Día 6 |
| `07_biblioteca.md` | Biblioteca de enlaces verificados, priorizada, con tiempos de lectura | Consulta continua |
| `08_preguntas_respuestas.md` | 40 preguntas con guion de respuesta, para practicar en voz alta | Día 7 y repaso |

**Regla de uso:** los dossiers son autocontenidos — puedes estudiar solo con ellos. La biblioteca es para profundizar donde te sientas flojo. No intentes leerlo todo; con menos de una semana, la lectura pasiva rinde menos que decir las respuestas en voz alta.

---

## Correcciones al plan inicial (verificadas esta semana)

Tres datos del plan de 7 días que conviene actualizar antes de citarlos en la entrevista:

1. **ROS 2:** la LTS activa a día de hoy (ago-2026) es **Lyrical Luth** (release 22-may-2026, EOL may-2031, Ubuntu 26.04). Jazzy (EOL may-2029) sigue siendo la LTS "madura" y la más probable en producción. **Kilted muere en diciembre de 2026** — eso convierte "¿en qué distro estáis y cuál es el plan de migración?" en una pregunta con filo real.
2. **Isaac Sim:** la versión actual es **6.0.1 GA** (jun-2026), con Isaac Lab 2.3.2. No digas "5.x".
3. **Bundeswehr:** *no hay contrato confirmado públicamente* con ARX. Sí hay UK MoD, Ucrania, EDA y US Army (Project Convergence). No des por hecho lo contrario — ver dossier ARX.

---

## Las tres frases que quiero que sepas decir sin pensar

1. *"Vuestra teleoperación ya es vuestro dataset: cada intervención del operador es un caso límite auto-etiquetado, y cada trayectoria conducida es una demostración de terreno transitable."*
2. *"El objetivo no es detectar objetos, es estimar transitabilidad con incertidumbre — y que la capa de comportamiento reaccione explícitamente a esa incertidumbre."*
3. *"Validar autonomía es un problema de cobertura de escenarios, no de demos: hay que medir qué fracción del espacio de condiciones has ejercitado."*
