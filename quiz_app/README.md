# Quantum Prep — Test de entrevista técnica

Aplicación de escritorio (PySide6) que genera tests tipo CoderPad con ChatGPT (por defecto) o Claude,
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

Por defecto usa **GPT-5.6 Sol** mediante `codex exec`, reutilizando tu sesión
de ChatGPT Pro. No necesita una clave API: consume los límites de Codex de tu
suscripción. Instala un Codex CLI actualizado y autentícate:

```bash
npm install -g @openai/codex
codex login
codex login status
```

Elige iniciar sesión con ChatGPT. La aplicación fuerza esta autenticación y no
usa las variables `OPENAI_API_KEY` / `CODEX_API_KEY`. Cada petición se ejecuta
en un directorio temporal, en modo de solo lectura, sin cargar la configuración
personal de Codex. Solo se recoge su respuesta final.

Edita `quiz_app/settings.yaml` y reinicia la aplicación:

```yaml
provider: chatgpt  # cambia a claude para usar Claude Code
timeout: 420
chatgpt:
  model: gpt-5.6-sol
  planning_model: gpt-5.6-sol
  binary: codex
claude:
  model: sonnet
  planning_model: haiku
  binary: claude
```

`model` es el modelo seleccionado inicialmente en la interfaz y también se usa
para el diagnóstico; `planning_model` diseña los subtemas. Puedes poner otro
identificador al que tu cuenta tenga acceso. `binary` admite una ruta absoluta.
El YAML se busca junto a `main.py`, independientemente del directorio de ejecución.
Si no existe, se usan los valores predeterminados de ChatGPT.

Para Claude necesitas `claude` en el PATH y su sesión iniciada. Se conserva la
invocación de Claude Code con su suscripción, sin `ANTHROPIC_API_KEY`.

Documentación oficial: [autenticación de Codex](https://learn.chatgpt.com/docs/auth),
[modo no interactivo](https://learn.chatgpt.com/docs/non-interactive-mode) y
[GPT-5.6 Sol](https://developers.openai.com/api/docs/models/gpt-5.6-sol).

## Flujo

1. **Configuración** — tema, nivel, número de preguntas, idioma y modelo.
2. **Generación** — dos fases:
   - el modelo de planificación configurado propone *N* subtemas distintos entre sí, usando
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
| `quizprep/llm.py` | invocación de Codex/Claude, cancelación y errores |
| `settings.yaml` / `quizprep/settings.py` | proveedor, modelos y carga de configuración |
| `quizprep/generator.py` | prompts, plan de subtemas, bloques paralelos, parseo |
| `quizprep/models.py` | `Question` / `Quiz` y la puntuación parcial |
| `quizprep/topics.py` | catálogo de temas y enlace con los apuntes |
| `quizprep/ui.py` | páginas de configuración, test y resultados |
| `quizprep/widgets.py` | Markdown → HTML y filas de opción |
| `quizprep/theme.py` | paleta y hoja de estilos (claro/oscuro) |
| `quizprep/store.py` | histórico local y exportación a Markdown |

## Verificación

```bash
PYTHONPATH=. .venv/bin/python -m unittest discover -s tests -v
```

Las pruebas usan procesos simulados y no consumen la suscripción.
