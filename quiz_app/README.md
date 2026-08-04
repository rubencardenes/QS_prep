# Quantum Prep — Test de entrevista técnica

Aplicación de escritorio (PySide6) que genera tests tipo CoderPad con Claude,
los corrige y explica cada fallo.

## Uso

```bash
./run.sh          # crea el venv la primera vez y abre la app
```

O a mano:

```bash
uv venv .venv && uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python main.py
```

## Cómo llama al modelo

No usa `ANTHROPIC_API_KEY`: lanza el CLI de Claude Code en modo no interactivo

```
claude -p <prompt> --system-prompt … --output-format json --allowed-tools "" …
```

con lo que consume tu **suscripción de Claude**, sin coste por token ni claves.
Requisito: tener `claude` en el `PATH` y la sesión iniciada.

## Flujo

1. **Configuración** — tema, nivel, número de preguntas, idioma y modelo.
2. **Generación** — dos fases:
   - un modelo rápido (Haiku) propone *N* subtemas distintos entre sí, usando
     tus apuntes del repo como referencia;
   - los subtemas se reparten en bloques que se generan **en paralelo** con el
     modelo elegido (~2 min para 10 preguntas). Se descartan las preguntas
     degeneradas y las duplicadas.
3. **Test** — una pregunta por pantalla, **varias respuestas pueden ser
   correctas**. Se puede navegar adelante y atrás; nada se corrige hasta el
   final. Atajos: `←` / `→` para navegar, `1`–`5` para marcar opciones.
4. **Resultados** — puntuación con crédito parcial (cada acierto suma, cada
   marca errónea resta dentro de la misma pregunta), revisión pregunta a
   pregunta con la justificación de **cada** opción, y botón de *diagnóstico
   del tutor* (segunda llamada al modelo) que resume patrones de error y qué
   estudiar primero. Exportable a Markdown.

## Temas

C++ moderno · Python · Computer Vision · OpenCV · Jetson/CUDA/TensorRT · ROS 2 ·
Mixto. Los temas con apuntes en el repo (`cpp_moderno.md`, `openCV C++.md`,
`jetson_ros2_QA.md`) pueden usarlos como contexto para ajustar el vocabulario y
el enfoque de las preguntas.

## Estado local

`~/.quantum-prep-quiz/history.json` guarda los enunciados ya vistos (para no
repetirlos) y el histórico de puntuaciones. Se puede borrar sin problema.

## Estructura

| Archivo | Contenido |
|---|---|
| `quizprep/llm.py` | invocación del CLI de Claude, cancelación y errores |
| `quizprep/generator.py` | prompts, plan de subtemas, bloques paralelos, parseo |
| `quizprep/models.py` | `Question` / `Quiz` y la puntuación parcial |
| `quizprep/topics.py` | catálogo de temas y enlace con los apuntes |
| `quizprep/ui.py` | páginas de configuración, test y resultados |
| `quizprep/widgets.py` | Markdown → HTML y filas de opción |
| `quizprep/theme.py` | paleta y hoja de estilos (claro/oscuro) |
| `quizprep/store.py` | histórico local y exportación a Markdown |
