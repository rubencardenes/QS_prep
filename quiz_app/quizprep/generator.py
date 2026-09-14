"""Construcción de prompts y parseo de la respuesta del modelo."""

from __future__ import annotations

import json
import math
import random
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

from .llm import LLMClient, CancelledError, LLMError
from .models import Option, Question, Quiz
from .topics import DIFFICULTIES, TOPICS_BY_KEY, Topic

SYSTEM_PROMPT = (
    "Eres un examinador técnico senior que prepara tests tipo CoderPad para "
    "entrevistas de ingeniería de software y visión por computador. "
    "Escribes preguntas precisas, sin ambigüedad y con distractores plausibles. "
    "Respondes EXCLUSIVAMENTE con JSON válido: sin texto introductorio, sin "
    "comentarios y sin vallas de código markdown."
)

_DIFFICULTY_LABEL = dict(DIFFICULTIES)

_JSON_SCHEMA = """{
  "questions": [
    {
      "topic": "subtema concreto, p. ej. 'std::move y valores x'",
      "difficulty": "junior|media|senior|experto",
      "question": "enunciado en Markdown; puede incluir un bloque ```cpp / ```python",
      "options": [
        {
          "text": "texto de la opción",
          "correct": true,
          "explanation": "por qué esta opción es correcta o incorrecta, 1-3 frases"
        }
      ],
      "explanation": "explicación global de la pregunta y del concepto de fondo",
      "reference": "palabra clave o concepto para repasar"
    }
  ]
}"""


# Ejes temáticos: se reparten entre los bloques paralelos para que las
# preguntas no se solapen aunque cada bloque se genere por separado.
ANGLES: tuple[str, ...] = (
    "semántica del lenguaje o de la API: qué hace exactamente cada construcción",
    "rendimiento, uso de memoria y coste de las operaciones",
    "casos límite, errores frecuentes y comportamiento indefinido o sorprendente",
    "diseño y buenas prácticas en código de producción",
    "depuración, herramientas y diagnóstico de problemas reales",
)


PLAN_SYSTEM = (
    "Eres un examinador técnico que diseña el temario de un test de entrevista. "
    "Respondes EXCLUSIVAMENTE con JSON válido, sin markdown ni comentarios."
)


def build_plan_prompt(
    topic: Topic,
    difficulty: str,
    count: int,
    language: str = "es",
    avoid: list[str] | None = None,
    notes: str = "",
) -> str:
    lang_name = {"es": "español", "en": "inglés"}.get(language, "español")
    parts = [
        f"Diseña el temario de un test de {count} preguntas sobre:",
        f"\nÁREA: {topic.label}\nALCANCE: {topic.brief}",
        f"NIVEL: {_DIFFICULTY_LABEL.get(difficulty, difficulty)}",
        f"\nDevuelve exactamente {count} subtemas CONCRETOS y CLARAMENTE "
        "DISTINTOS entre sí (nada de solaparse: si uno cubre la semántica de "
        "copia, ningún otro puede hablar de copias). Cada subtema en una línea "
        f"de 4-12 palabras, en {lang_name}, cubriendo el área de forma amplia y "
        "mezclando conceptos básicos, de rendimiento y trampas conocidas.",
    ]
    if avoid:
        parts.append(
            "\nEvita subtemas de estas preguntas ya usadas:\n"
            + "\n".join(f"- {q}" for q in avoid[:40])
        )
    if notes:
        parts.append(
            "\nEstos son los apuntes del candidato: elige subtemas que encajen "
            "con su enfoque y vocabulario.\n<apuntes>\n" + notes + "\n</apuntes>"
        )
    parts.append('\nFormato: {"subtopics": ["...", "..."]}')
    return "\n".join(parts)


def plan_subtopics(
    client: LLMClient,
    topic: Topic,
    difficulty: str,
    count: int,
    language: str = "es",
    avoid: list[str] | None = None,
    cancel=None,
    notes: str = "",
) -> list[str]:
    """Pide una lista de subtemas distintos para repartir entre los bloques."""
    raw = client.complete(
        PLAN_SYSTEM,
        build_plan_prompt(topic, difficulty, count, language, avoid, notes),
        cancel=cancel,
    )
    payload = _extract_json_object(raw)
    items = payload.get("subtopics")
    if not isinstance(items, list):
        return []
    subtopics = [str(s).strip() for s in items if str(s).strip()]
    return subtopics[:count]


def build_prompt(
    topic: Topic,
    difficulty: str,
    count: int,
    language: str = "es",
    notes: str = "",
    avoid: list[str] | None = None,
    angle: str = "",
    subtopics: list[str] | None = None,
) -> str:
    lang_name = {"es": "español", "en": "inglés"}.get(language, "español")
    parts: list[str] = [
        f"Genera un test de {count} preguntas de opción múltiple sobre este área:",
        f"\nÁREA: {topic.label}\nALCANCE: {topic.brief}",
        f"\nNIVEL: {_DIFFICULTY_LABEL.get(difficulty, difficulty)}",
        f"IDIOMA de todo el contenido: {lang_name}.",
        "\nREGLAS OBLIGATORIAS:",
        "1. Cada pregunta tiene entre 4 y 5 opciones.",
        "2. El número de opciones correctas varía: al menos un 40% de las "
        "preguntas debe tener MÁS DE UNA opción correcta, y alguna pregunta "
        "debe tener una sola. Nunca todas correctas ni todas incorrectas.",
        "3. Los distractores deben ser errores creíbles que cometería un "
        "candidato real, no absurdos.",
        "4. Cada opción lleva su propia `explanation` que justifica por qué es "
        "correcta o por qué falla.",
        "5. `explanation` de la pregunta resume el concepto de fondo y, si "
        "procede, menciona el estándar/versión o la función concreta.",
        "6. Cuando el enunciado incluya código, usa bloques markdown con el "
        "lenguaje indicado y mantenlo corto (máx. ~15 líneas).",
        "7. No numeres las opciones ni uses prefijos tipo 'a)' — solo el texto.",
        "8. Varía los subtemas: no repitas dos veces el mismo concepto.",
    ]

    if subtopics:
        listado = "\n".join(f"{i}. {s}" for i, s in enumerate(subtopics, 1))
        parts.append(
            f"\nSUBTEMAS ASIGNADOS: genera exactamente una pregunta por cada "
            f"uno de estos {len(subtopics)} subtemas, en este orden, y no te "
            f"salgas de ellos:\n{listado}"
        )
    elif angle:
        parts.append(
            f"\nENFOQUE de este bloque de preguntas: {angle}. "
            "Mantente dentro del área indicada, pero mira el tema desde ese ángulo."
        )

    if avoid:
        muestra = "\n".join(f"- {q}" for q in avoid[:40])
        parts.append(
            "\nNO repitas ninguna de estas preguntas ya formuladas "
            f"anteriormente:\n{muestra}"
        )

    if notes:
        parts.append(
            "\nApóyate en estos apuntes del candidato para elegir los "
            "subtemas y el vocabulario (puedes ir más allá de ellos, pero "
            "mantente en su nivel y enfoque):\n"
            "<apuntes>\n" + notes + "\n</apuntes>"
        )

    parts.append(
        "\nDevuelve únicamente un objeto JSON con esta forma exacta:\n" + _JSON_SCHEMA
    )
    return "\n".join(parts)


ANALYSIS_SYSTEM = (
    "Eres un mentor técnico que prepara a un ingeniero para una entrevista. "
    "Eres directo, concreto y accionable. Escribes en Markdown."
)


def build_analysis_prompt(quiz: Quiz, language: str = "es") -> str:
    lang_name = {"es": "español", "en": "inglés"}.get(language, "español")
    lines = [
        f"Un candidato acaba de hacer un test de {quiz.total} preguntas sobre "
        f"«{quiz.topic}» (nivel {quiz.difficulty}) y ha sacado "
        f"{quiz.percentage():.0f}%.",
        f"\nEscribe en {lang_name} un diagnóstico breve (máx. 400 palabras) con:",
        "1. Los patrones de error que ves (no repitas pregunta por pregunta).",
        "2. Los 3-5 conceptos que debe repasar primero, ordenados por prioridad.",
        "3. Una acción concreta de estudio para cada uno.",
        "\nEstos son los fallos:",
    ]
    for i, q in enumerate(quiz.questions, 1):
        if q.is_perfect:
            continue
        chosen = [q.options[j].text for j in sorted(q.selected)] or ["(sin responder)"]
        right = [q.options[j].text for j in sorted(q.correct_indices)]
        lines.append(
            f"\n--- Pregunta {i} [{q.topic}] ---\n"
            f"Enunciado: {q.question}\n"
            f"Marcó: {' | '.join(chosen)}\n"
            f"Correcto: {' | '.join(right)}"
        )
    if quiz.perfect_count() == quiz.total:
        lines.append("\n(No ha fallado ninguna: comenta qué nivel demuestra y "
                     "qué temas avanzados atacar a continuación.)")
    return "\n".join(lines)


def _strip_fences(text: str) -> str:
    text = text.strip()
    fence = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, re.DOTALL)
    if fence:
        return fence.group(1).strip()
    return text


def _extract_json_object(text: str) -> dict:
    text = _strip_fences(text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end > start:
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError as exc:
            raise LLMError(
                "No se pudo interpretar la respuesta del modelo como JSON.\n"
                f"Detalle: {exc}\n\nRespuesta recibida (recortada):\n{text[:800]}"
            ) from exc
    raise LLMError(
        "El modelo no devolvió JSON.\n\nRespuesta recibida (recortada):\n" + text[:800]
    )


def parse_questions(raw: str, shuffle: bool = True) -> list[Question]:
    payload = _extract_json_object(raw)
    items = payload.get("questions")
    if not isinstance(items, list) or not items:
        raise LLMError("El JSON devuelto no contiene una lista «questions».")

    questions: list[Question] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        raw_options = item.get("options")
        if not isinstance(raw_options, list) or len(raw_options) < 2:
            continue
        options = [
            Option(
                text=str(o.get("text", "")).strip(),
                correct=bool(o.get("correct")),
                explanation=str(o.get("explanation", "")).strip(),
            )
            for o in raw_options
            if isinstance(o, dict) and str(o.get("text", "")).strip()
        ]
        n_correct = sum(1 for o in options if o.correct)
        # Descarta preguntas degeneradas: sin correctas o con todas correctas.
        if len(options) < 2 or n_correct == 0 or n_correct == len(options):
            continue
        if shuffle:
            random.shuffle(options)
        questions.append(
            Question(
                question=str(item.get("question", "")).strip(),
                options=options,
                topic=str(item.get("topic", "")).strip(),
                difficulty=str(item.get("difficulty", "")).strip(),
                explanation=str(item.get("explanation", "")).strip(),
                reference=str(item.get("reference", "")).strip(),
            )
        )

    if not questions:
        raise LLMError("No se obtuvo ninguna pregunta válida del modelo.")
    return questions


MAX_PARALLEL_BLOCKS = 6
QUESTIONS_PER_BLOCK = 3


def batch_sizes(count: int) -> list[int]:
    """Reparte `count` preguntas en bloques que se generarán en paralelo."""
    if count <= QUESTIONS_PER_BLOCK:
        return [count]
    blocks = min(MAX_PARALLEL_BLOCKS, math.ceil(count / QUESTIONS_PER_BLOCK))
    base, extra = divmod(count, blocks)
    return [base + (1 if i < extra else 0) for i in range(blocks)]


def _stem(text: str) -> str:
    return re.sub(r"\W+", " ", text.lower()).strip()[:70]


def generate_quiz(
    client: LLMClient,
    topic_key: str,
    difficulty: str,
    count: int,
    language: str = "es",
    use_notes: bool = False,
    avoid: list[str] | None = None,
    cancel=None,
    report=None,
    planning_client: LLMClient | None = None,
) -> Quiz:
    """Genera un test. Con muchas preguntas lanza varios bloques en paralelo."""
    topic = TOPICS_BY_KEY[topic_key]
    notes = topic.load_notes() if use_notes else ""
    sizes = batch_sizes(count)

    # Fase 1: repartir subtemas distintos para que los bloques no se solapen.
    # Los apuntes solo van aquí: el plan resultante ya traslada su enfoque a
    # cada bloque, y así no se reenvía un contexto enorme N veces.
    plan: list[str] = []
    if count > QUESTIONS_PER_BLOCK:
        if report is not None:
            report("Planificando subtemas…")
        try:
            plan = plan_subtopics(
                planning_client or client,
                topic,
                difficulty,
                count,
                language,
                avoid,
                cancel,
                notes,
            )
        except CancelledError:
            raise
        except LLMError:
            plan = []  # sin plan seguimos con los ángulos temáticos

    # Con plan, los bloques no necesitan los apuntes completos.
    block_notes = "" if plan else notes

    offsets: list[int] = []
    running = 0
    for size in sizes:
        offsets.append(running)
        running += size

    def prompt_for(index: int, size: int) -> str:
        chunk = plan[offsets[index] : offsets[index] + size] if plan else []
        angle = ANGLES[index % len(ANGLES)] if len(sizes) > 1 else ""
        # Si el plan vino corto, el bloque pide tantas preguntas como subtemas
        # tenga asignados para no contradecirse dentro del propio prompt.
        wanted = len(chunk) if chunk else size
        return build_prompt(
            topic, difficulty, wanted, language, block_notes, avoid, angle, chunk
        )

    def notify(done: int) -> None:
        if report is None:
            return
        if len(sizes) == 1:
            report("Redactando las preguntas…")
        else:
            report(f"Bloques completados: {done}/{len(sizes)}")

    notify(0)
    raws: list[str] = []
    errors: list[str] = []

    if len(sizes) == 1:
        raws.append(client.complete(SYSTEM_PROMPT, prompt_for(0, sizes[0]), cancel))
    else:
        with ThreadPoolExecutor(max_workers=len(sizes)) as pool:
            futures = [
                pool.submit(
                    client.complete, SYSTEM_PROMPT, prompt_for(i, size), cancel
                )
                for i, size in enumerate(sizes)
            ]
            done = 0
            for future in as_completed(futures):
                try:
                    raws.append(future.result())
                except CancelledError:
                    for pending in futures:
                        pending.cancel()
                    raise
                except LLMError as exc:
                    errors.append(str(exc))
                done += 1
                notify(done)

    questions: list[Question] = []
    seen: set[str] = set()
    for raw in raws:
        try:
            batch = parse_questions(raw)
        except LLMError as exc:
            errors.append(str(exc))
            continue
        for question in batch:
            key = _stem(question.question)
            if key in seen:
                continue
            seen.add(key)
            questions.append(question)

    if not questions:
        raise LLMError(
            "No se pudo generar ninguna pregunta.\n\n"
            + ("\n---\n".join(errors) if errors else "Respuesta vacía del modelo.")
        )

    random.shuffle(questions)
    return Quiz(topic=topic.label, difficulty=difficulty, questions=questions[:count])
