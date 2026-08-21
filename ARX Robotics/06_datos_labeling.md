# Dossier 5 — Datos, anotación y data loop

*Es la tarea más explícita de la oferta ("Aufbau, Organisation und Qualitätssicherung von Annotation-Prozessen") y ARX tiene abierta una vacante de **Staff Engineer Data Loop**. Si dominas este bloque, compites en un terreno donde casi nadie se prepara.*

---

## 1. El pipeline completo, de principio a fin

Esta es la respuesta de 5 minutos que debes tener ensayada. Ocho etapas:

### 1. Ingesta
Bags en **MCAP** desde campo → almacenamiento con metadatos obligatorios: vehículo e ID de plataforma, sesión, configuración de sensores, **versión de calibración vigente**, versión de software, ubicación, meteorología, hora, operador, tipo de misión.

**Sin esta metadata el dataset es inútil a los seis meses**, porque no podrás responder "¿qué datos tengo de terreno nevado con el LiDAR nuevo?". Es la parte más aburrida y la que más gente se salta.

Decisión de campo asociada: **no puedes grabar todo**. Un vehículo con LiDAR + varias cámaras genera decenas de GB por hora. Hay que decidir política de grabación: grabación continua de baja tasa + grabación completa disparada por eventos (intervención del operador, e-stop, incertidumbre alta de percepción, discrepancia entre módulos). Esa política es en sí misma una decisión de arquitectura.

### 2. Curación y selección — el paso que todo el mundo se salta
**No anotas lo que recoges; anotas lo que aporta.** Anotar aleatoriamente es tirar dinero: el 95% de los frames de una sesión son casi idénticos al anterior.

Técnicas:
- **Deduplicación por embeddings**: proyectar frames a un espacio de features y eliminar los casi-duplicados.
- **Muestreo por diversidad**: cubrir el espacio de embeddings uniformemente en vez de seguir la distribución natural (que está dominada por lo trivial).
- **Active learning**: priorizar donde el modelo tiene mayor incertidumbre, o donde un ensemble discrepa.
- **Minería de casos límite desde la operación** ⭐: cada **intervención del teleoperador** es una etiqueta gratuita de "aquí el sistema no supo". Cada e-stop, cada discrepancia entre la ruta planificada y la conducida. En ARX, con flota desplegada teleoperada, esta es la mina de oro.

Herramienta de referencia: **FiftyOne (Voxel51)**, con FiftyOne Brain para similaridad, unicidad y *mistakenness* (encontrar etiquetas probablemente erróneas).

📚 [FiftyOne docs](https://docs.voxel51.com/) · [Curación pre-anotación](https://docs.voxel51.com/workflows/curation_pre.html) · [Smart Sample Selection](https://docs.voxel51.com/getting_started/annotation/03_smart_selection.html)

### 3. Ontología / label schema — la decisión más cara de revertir
Reetiquetar 50.000 frames porque la ontología estaba mal es un desastre de seis cifras. Principios:

- **Las clases deben corresponder a diferencias de coste de navegación**, no a categorías botánicas o taxonómicas. La pregunta al definir una clase es: *¿el vehículo hace algo distinto ante esta clase que ante aquella?* Si no, fusiónalas.
- **Definir la ontología con los ingenieros de behavior**, no solo con los de percepción. Es un contrato entre capas.
- **Prever atributos además de clases**: altura de vegetación, densidad, humedad, si oculta lo que hay detrás. Un atributo es mucho más barato de añadir después que una clase nueva.
- **Una clase "unknown/other" bien definida**, con criterio explícito de cuándo usarla — y monitorizar su frecuencia: si crece, tu ontología se está quedando corta.
- **Jerarquía**, para poder agrupar y desagrupar sin reetiquetar.
- **No la inventes desde cero.** Parte de **GOOSE** (Fraunhofer IOSB / UniBw München): 64 clases en 11 grupos, con **labeling policy publicada en PDF** que incluye definiciones, colores, reglas instance-wise y ejemplos visuales de casos ambiguos. Es el estándar de facto europeo para off-road militar. Adoptar y extender una ontología existente te da además compatibilidad con datasets públicos para preentrenar.

📚 [**GOOSE Labeling Policy (PDF)** ⭐](https://goose-dataset.de/docs/resources/labeling_policy.pdf) · [Definiciones de clases](https://goose-dataset.de/docs/class-definitions/)

### 4. Herramientas de anotación
| Herramienta | Nota |
|---|---|
| **CVAT** | Open source, self-hostable, soporta **cuboides 3D sobre nubes de puntos** con modo track e interpolación, y —clave— tiene un **módulo de QA con ground-truth jobs y honeypots**. La opción por defecto en entorno restringido |
| **SUSTechPOINTS** | Específico de nubes 3D para conducción autónoma: cajas 9-DoF, predicción automática de yaw, edición en lote, multi-cámara. Ligero y muy eficaz |
| **Label Studio** | Muy flexible y multi-modal, con backend ML para pre-anotación. ⚠️ Su soporte 3D/nubes de puntos no está confirmado — verifícalo antes de proponerlo para LiDAR |
| Segments.ai, Kognic, Encord, Scale, Deepen | Comerciales, buenos, pero implican mandar datos fuera |

**El criterio decisivo en ARX no es la ergonomía: es que la herramienta sea on-premise y los anotadores estén autorizados.** Datos de operaciones en Ucrania y de programas con el UK MoD no salen del perímetro. Di esto explícitamente — demuestra que entiendes su restricción real antes de que te la cuenten.

📚 [CVAT 3D](https://docs.cvat.ai/docs/annotation/manual-annotation/modes/3d-object-annotation/) · [SUSTechPOINTS](https://github.com/naurril/SUSTechPOINTS)

### 5. Pre-etiquetado y auto-labeling
Reduce coste 3–10×. El humano **corrige, no dibuja desde cero**.

- **Modelo existente como pre-etiquetador**: en cuanto tienes una primera versión, úsala.
- **SAM 2 / SAM 3** para máscaras: SAM 3 (2026) segmenta por **concepto** (una frase de texto corta) y devuelve *todas* las instancias — mucho más útil a escala que SAM 2. ⚠️ Ojo con la licencia: SAM 2 es Apache 2.0, **SAM 3 usa la "SAM License"** con restricciones. Revísala antes de uso comercial en defensa.
- **Propagación temporal** entre frames consecutivos: anota uno, propaga a los N siguientes con tracking.
- **Proyección cruzada 3D↔2D**: anota en la nube y proyecta a las cámaras usando la calibración (o al revés). Etiquetas una vez, obtienes dos dominios. Requiere calibración y sincronización buenas — otra razón más para invertir ahí primero.
- **Auto-labeling desde propiocepción**: como en el Dossier 1, las etiquetas de tracción son gratis.

📚 [SAM 2](https://github.com/facebookresearch/sam2) · [SAM 3](https://github.com/facebookresearch/sam3)

### 6. Aseguramiento de calidad — lo que la oferta pide literalmente

Este es el bloque que debes tener más afilado. Un proceso de QA serio tiene seis componentes:

1. **Guía de anotación versionada**, con ejemplos visuales y —sobre todo— **casos límite resueltos**. Es un documento vivo: cada duda recurrente se resuelve una vez y se añade.
2. **Golden set / ground-truth job**: un subconjunto anotado por un experto y consensuado, contra el que se mide a cada anotador. CVAT lo soporta nativamente.
3. **Honeypots**: tareas del golden set inyectadas de forma invisible en el flujo normal de trabajo, para medir calidad continuamente y sin sesgo de observación.
4. **Acuerdo inter-anotador**: solapar deliberadamente un % de las tareas entre dos o más anotadores y medir. Métricas: **Cohen's kappa** (dos anotadores, categorías), **Fleiss/Krippendorff's alpha** (múltiples anotadores, tolera datos faltantes — el más general), y **mIoU entre anotadores** para segmentación. La referencia canónica y gratuita es el survey de Artstein & Poesio.
5. **Revisión por muestreo estadístico** con umbral de aceptación definido de antemano, en vez de "revisamos lo que podemos".
6. **Bucle de feedback al anotador**, con métricas por persona y sesiones de recalibración.

**El punto que te distingue:** *los desacuerdos recurrentes entre anotadores no indican anotadores malos — indican una ontología mal definida.* Auditar periódicamente la guía a partir de los desacuerdos es un mecanismo de mejora, no un castigo. Dilo así.

📚 [CVAT QA & Analytics](https://docs.cvat.ai/docs/qa-analytics/) · [Auto QA y honeypots](https://docs.cvat.ai/docs/qa-analytics/auto-qa/) · [Artstein & Poesio, *Inter-Coder Agreement* (PDF gratis)](https://aclanthology.org/J08-4004.pdf)

### 7. Versionado y trazabilidad
- **DVC** (versionado tipo Git de datos y modelos, con pipelines) o **lakeFS** (semántica Git sobre el object storage existente, con branches zero-copy — mejor a escala de terabytes).
- Splits **congelados y versionados**.
- **La fuga de datos clásica en robótica**: partir train/test por frame en vez de por sesión y por ubicación. Frames consecutivos son casi idénticos; si unos van a train y otros a test, tu métrica está inflada y no te enterarás hasta el campo. **Se parte por sesión, por localización y, si puedes, por estación del año.** Menciona esto: es un error que comete muchísima gente con experiencia.
- Cada modelo entrenado debe enlazar con su dataset exacto, su código y su configuración.

📚 [DVC](https://doc.dvc.org/) · [lakeFS](https://docs.lakefs.io/)

### 8. Cierre del bucle — el "data loop"
Métricas del modelo por clase y por condición → identificar dónde falla → **dirigir la siguiente campaña de recogida y anotación** hacia esos huecos → reentrenar → desplegar → recoger. 

El bucle completo, para ARX, tiene además un paso que no aparece en los diagramas académicos: **cómo salen los datos del vehículo desplegado y cómo vuelve el modelo actualizado al vehículo** (OTA), con conectividad intermitente y restricciones de clasificación. Ese es el problema real de su *Staff Engineer Data Loop*.

---

## 2. Los tres huecos que casi nadie menciona

1. **La calibración es parte del dataset.** Si la calibración extrínseca cambió a mitad de campaña (y en un vehículo de orugas cambia por vibración), los datos anteriores y posteriores no son comparables y la proyección 3D↔2D deja de ser válida. Hay que versionar la calibración junto con los datos y poder reprocesar.

2. **La deriva de distribución es continua.** Estaciones, biomas, teatros de operaciones distintos (Alemania vs Ucrania vs Kenia — ARX opera en los tres). Necesitas monitorización de deriva en producción, no solo métricas de test: comparar la distribución de embeddings del campo con la del training set y alertar cuando se separan.

3. **El coste de anotación es una variable de diseño, no un dato.** Con presupuesto fijo, la decisión de "¿anoto 10.000 frames con 64 clases o 40.000 con 12 clases?" cambia el resultado. Deberías poder razonar sobre ese trade-off explícitamente y con números.

---

## 3. Respuesta modelo: "¿cómo montarías esto desde cero en ARX?"

Guion de 5 minutos, en cuatro fases:

**Fase 0 — Auditar antes de construir (2 semanas).** ¿Qué bags existen ya, con qué metadata, con qué calidad de calibración y sincronización? ¿Qué fracción es aprovechable? Casi siempre el hallazgo es que hay muchos datos y poca metadata. Entregable: un inventario y un diagnóstico honesto.

**Fase 1 — Arreglar la fuente antes que el proceso (4 semanas).** Metadata obligatoria en la grabación, versionado de calibración, política de grabación disparada por eventos, y una estructura de almacenamiento consultable. Nada de esto es glamuroso y todo lo demás depende de ello.

**Fase 2 — Ontología y primera vuelta (4 semanas).** Adoptar y extender GOOSE. Guía de anotación con casos límite. Herramienta on-premise (CVAT) con QA configurado. Primera tanda pequeña —2.000 frames bien curados— para validar que la ontología funciona *antes* de escalar. Medir acuerdo inter-anotador desde el primer día.

**Fase 3 — Escalar con auto-labeling y cerrar el bucle (continuo).** Pre-etiquetado con el primer modelo + SAM, curación con active learning, honeypots permanentes, versionado con DVC/lakeFS, y minería automática de casos límite desde las intervenciones del teleoperador. En paralelo, arrancar la traversability auto-supervisada, que no necesita anotadores.

**El remate:** *"Y mediría el proceso, no solo el modelo: coste por frame anotado, acuerdo inter-anotador, tiempo de ciclo desde que ocurre un fallo en campo hasta que hay un modelo corregido desplegado. Ese último número es el que de verdad determina la velocidad del equipo."*

---

## 4. Autoevaluación

1. ¿Por qué anotar frames aleatorios es tirar el dinero, y qué haces en su lugar?
2. Diseña la ontología mínima para navegación off-road. Justifica cada clase por su efecto en el comportamiento.
3. ¿Cómo mides la calidad de anotación sin revisarlo todo?
4. ¿Qué es un honeypot y por qué funciona mejor que la revisión anunciada?
5. Explica la fuga de datos por partición incorrecta en robótica.
6. Los datos no pueden salir de la empresa. ¿Cómo cambia tu diseño?
7. ¿Qué haces cuando dos anotadores discrepan sistemáticamente en una clase?
8. Define tres métricas del *proceso* de datos (no del modelo) y por qué importan.
