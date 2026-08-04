"""Persistencia local: histórico de preguntas y resultados, y exportación."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from .models import Quiz

APP_DIR = Path.home() / ".quantum-prep-quiz"
HISTORY_FILE = APP_DIR / "history.json"
MAX_ASKED = 300


def _load() -> dict:
    if not HISTORY_FILE.is_file():
        return {"asked": {}, "results": []}
    try:
        data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"asked": {}, "results": []}
    data.setdefault("asked", {})
    data.setdefault("results", [])
    return data


def _save(data: dict) -> None:
    try:
        APP_DIR.mkdir(parents=True, exist_ok=True)
        HISTORY_FILE.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    except OSError:
        pass  # el histórico es un extra, nunca debe romper la app


def asked_questions(topic_key: str) -> list[str]:
    return _load()["asked"].get(topic_key, [])


def remember_questions(topic_key: str, questions: list[str]) -> None:
    data = _load()
    bucket = data["asked"].setdefault(topic_key, [])
    for q in questions:
        stem = q.strip().split("\n")[0][:220]
        if stem and stem not in bucket:
            bucket.append(stem)
    data["asked"][topic_key] = bucket[-MAX_ASKED:]
    _save(data)


def record_result(topic_key: str, quiz: Quiz) -> None:
    data = _load()
    data["results"].append(
        {
            "when": datetime.now().isoformat(timespec="seconds"),
            "topic_key": topic_key,
            "topic": quiz.topic,
            "difficulty": quiz.difficulty,
            "total": quiz.total,
            "correct": quiz.perfect_count(),
            "percentage": round(quiz.percentage(), 1),
        }
    )
    data["results"] = data["results"][-200:]
    _save(data)


def recent_results(limit: int = 10) -> list[dict]:
    return list(reversed(_load()["results"][-limit:]))


def clear_history() -> None:
    _save({"asked": {}, "results": []})


def quiz_to_markdown(quiz: Quiz, analysis: str = "") -> str:
    lines = [
        f"# Resultado del test — {quiz.topic}",
        "",
        f"- Fecha: {datetime.now():%Y-%m-%d %H:%M}",
        f"- Nivel: {quiz.difficulty}",
        f"- Puntuación: **{quiz.percentage():.0f}%** "
        f"({quiz.points():.2f}/{quiz.total} puntos)",
        f"- Preguntas perfectas: {quiz.perfect_count()}/{quiz.total}",
        "",
    ]
    if analysis:
        lines += ["## Diagnóstico del tutor", "", analysis, ""]

    lines.append("## Revisión pregunta a pregunta")
    for i, q in enumerate(quiz.questions, 1):
        mark = "✅" if q.is_perfect else ("⚠️" if q.score() > 0 else "❌")
        lines += ["", f"### {mark} Pregunta {i} — {q.topic}", "", q.question, ""]
        for j, opt in enumerate(q.options):
            chosen = "x" if j in q.selected else " "
            flag = "correcta" if opt.correct else "incorrecta"
            lines.append(f"- [{chosen}] **{opt.text}** — _{flag}_: {opt.explanation}")
        if q.explanation:
            lines += ["", f"> {q.explanation}"]
        if q.reference:
            lines.append(f">\n> Repasar: `{q.reference}`")
    return "\n".join(lines) + "\n"
