"""Persistencia SQLite del histórico, preguntas vistas y revisiones."""

from __future__ import annotations

import json
import re
import sqlite3
from datetime import datetime
from pathlib import Path

from .models import Quiz

APP_DIR = Path.home() / ".quantum-prep-quiz"
DB_FILE = APP_DIR / "history.db"
LEGACY_HISTORY_FILE = APP_DIR / "history.json"
REVISIONS_DIR = Path(__file__).resolve().parents[1]
MAX_ASKED = 300


def _connect() -> sqlite3.Connection:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_FILE)
    connection.row_factory = sqlite3.Row
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS asked_questions (
            topic_key TEXT NOT NULL, question TEXT NOT NULL,
            asked_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (topic_key, question)
        );
        CREATE TABLE IF NOT EXISTS test_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            taken_at TEXT NOT NULL, topic_key TEXT NOT NULL DEFAULT '',
            topic TEXT NOT NULL, difficulty TEXT NOT NULL,
            question_count INTEGER NOT NULL, points REAL NOT NULL,
            perfect_count INTEGER NOT NULL, percentage REAL NOT NULL,
            elapsed_seconds INTEGER, language TEXT, model TEXT,
            source_path TEXT UNIQUE, review_markdown TEXT NOT NULL DEFAULT ''
        );
        CREATE INDEX IF NOT EXISTS idx_results_topic ON test_results(topic_key);
        CREATE INDEX IF NOT EXISTS idx_results_taken_at ON test_results(taken_at);
        """
    )
    return connection


def _topic_key(topic: str) -> str:
    from .topics import TOPICS

    return next((item.key for item in TOPICS if item.label == topic), "")


def _parse_revision(path: Path) -> dict | None:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    expressions = {
        "topic": r"^# Resultado del test — (.+)$",
        "taken_at": r"^- Fecha: (.+)$",
        "difficulty": r"^- Nivel: (.+)$",
        "score": r"^- Puntuación: \*\*([\d.,]+)%\*\* \(([\d.,]+)/([\d.,]+) puntos\)$",
        "perfect": r"^- Preguntas perfectas: (\d+)/(\d+)$",
    }
    matches = {key: re.search(value, text, re.MULTILINE) for key, value in expressions.items()}
    if not all(matches.values()):
        return None
    topic_match, date_match = matches["topic"], matches["taken_at"]
    difficulty_match, score, perfect = matches["difficulty"], matches["score"], matches["perfect"]
    assert topic_match and date_match and difficulty_match and score and perfect
    topic = topic_match.group(1).strip()
    return {
        "taken_at": date_match.group(1).strip().replace(" ", "T", 1),
        "topic_key": _topic_key(topic), "topic": topic,
        "difficulty": difficulty_match.group(1).strip(),
        "question_count": int(perfect.group(2)),
        "points": float(score.group(2).replace(",", ".")),
        "perfect_count": int(perfect.group(1)),
        "percentage": float(score.group(1).replace(",", ".")),
        "source_path": str(path.resolve()), "review_markdown": text,
    }


def initialize() -> None:
    """Crea el esquema e importa de forma idempotente JSON y revisiones Markdown."""
    with _connect() as connection:
        if LEGACY_HISTORY_FILE.is_file():
            try:
                legacy = json.loads(LEGACY_HISTORY_FILE.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                legacy = {}
            for topic_key, questions in legacy.get("asked", {}).items():
                for question in questions:
                    connection.execute(
                        "INSERT OR IGNORE INTO asked_questions(topic_key, question) VALUES (?, ?)",
                        (topic_key, question),
                    )
            for index, result in enumerate(legacy.get("results", [])):
                source = f"legacy-json:{index}:{result.get('when', '')}"
                total = result.get("total", 0)
                percentage = result.get("percentage", 0)
                connection.execute(
                    """INSERT OR IGNORE INTO test_results
                       (taken_at, topic_key, topic, difficulty, question_count, points,
                        perfect_count, percentage, source_path) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (result.get("when", ""), result.get("topic_key", ""), result.get("topic", ""),
                     result.get("difficulty", ""), total, percentage * total / 100,
                     result.get("correct", 0), percentage, source),
                )
        for path in sorted(REVISIONS_DIR.glob("revision_test_*.md")):
            row = _parse_revision(path)
            if row:
                existing = connection.execute(
                    "SELECT id FROM test_results WHERE source_path = ?", (row["source_path"],)
                ).fetchone()
                if existing:
                    continue
                legacy_match = connection.execute(
                    """SELECT id FROM test_results
                       WHERE substr(taken_at, 1, 16) = substr(:taken_at, 1, 16)
                         AND topic = :topic AND question_count = :question_count
                         AND review_markdown = '' LIMIT 1""",
                    row,
                ).fetchone()
                if legacy_match:
                    connection.execute(
                        """UPDATE test_results SET topic_key=:topic_key, points=:points,
                           perfect_count=:perfect_count, percentage=:percentage,
                           source_path=:source_path, review_markdown=:review_markdown
                           WHERE id=:id""",
                        {**row, "id": legacy_match["id"]},
                    )
                    continue
                connection.execute(
                    """INSERT OR IGNORE INTO test_results
                       (taken_at, topic_key, topic, difficulty, question_count, points,
                        perfect_count, percentage, source_path, review_markdown)
                       VALUES (:taken_at, :topic_key, :topic, :difficulty, :question_count,
                               :points, :perfect_count, :percentage, :source_path, :review_markdown)""",
                    row,
                )


def asked_questions(topic_key: str) -> list[str]:
    initialize()
    with _connect() as connection:
        rows = connection.execute(
            "SELECT question FROM asked_questions WHERE topic_key=? ORDER BY asked_at DESC LIMIT ?",
            (topic_key, MAX_ASKED),
        ).fetchall()
    return [row["question"] for row in rows]


def remember_questions(topic_key: str, questions: list[str]) -> None:
    initialize()
    with _connect() as connection:
        for question in questions:
            stem = question.strip().split("\n")[0][:220]
            if stem:
                connection.execute(
                    """INSERT INTO asked_questions(topic_key, question, asked_at) VALUES (?, ?, ?)
                       ON CONFLICT(topic_key, question) DO UPDATE SET asked_at=excluded.asked_at""",
                    (topic_key, stem, datetime.now().isoformat(timespec="seconds")),
                )


def record_result(topic_key: str, quiz: Quiz, *, elapsed: int | None = None,
                  language: str = "", model: str = "") -> None:
    initialize()
    with _connect() as connection:
        connection.execute(
            """INSERT INTO test_results
               (taken_at, topic_key, topic, difficulty, question_count, points,
                perfect_count, percentage, elapsed_seconds, language, model, review_markdown)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (datetime.now().isoformat(timespec="seconds"), topic_key, quiz.topic,
             quiz.difficulty, quiz.total, quiz.points(), quiz.perfect_count(),
             round(quiz.percentage(), 1), elapsed, language, model, quiz_to_markdown(quiz)),
        )


def results(topic_key: str = "", difficulty: str = "", limit: int | None = None) -> list[dict]:
    initialize()
    clauses: list[str] = []
    values: list[object] = []
    if topic_key:
        clauses.append("topic_key = ?")
        values.append(topic_key)
    if difficulty:
        clauses.append("difficulty = ?")
        values.append(difficulty)
    sql = "SELECT * FROM test_results"
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY taken_at DESC, id DESC"
    if limit is not None:
        sql += " LIMIT ?"
        values.append(limit)
    with _connect() as connection:
        return [dict(row) for row in connection.execute(sql, values).fetchall()]


def recent_results(limit: int = 10) -> list[dict]:
    rows = results(limit=limit)
    for row in rows:
        row["when"] = row["taken_at"]
        row["total"] = row["question_count"]
        row["correct"] = row["perfect_count"]
    return rows


def clear_history() -> None:
    with _connect() as connection:
        connection.execute("DELETE FROM asked_questions")
        connection.execute("DELETE FROM test_results")


def quiz_to_markdown(quiz: Quiz, analysis: str = "") -> str:
    lines = [f"# Resultado del test — {quiz.topic}", "",
             f"- Fecha: {datetime.now():%Y-%m-%d %H:%M}", f"- Nivel: {quiz.difficulty}",
             f"- Puntuación: **{quiz.percentage():.0f}%** ({quiz.points():.2f}/{quiz.total} puntos)",
             f"- Preguntas perfectas: {quiz.perfect_count()}/{quiz.total}", ""]
    if analysis:
        lines += ["## Diagnóstico del tutor", "", analysis, ""]
    lines.append("## Revisión pregunta a pregunta")
    for i, question in enumerate(quiz.questions, 1):
        mark = "✅" if question.is_perfect else ("⚠️" if question.score() > 0 else "❌")
        lines += ["", f"### {mark} Pregunta {i} — {question.topic}", "", question.question, ""]
        for j, option in enumerate(question.options):
            chosen, flag = ("x" if j in question.selected else " "), ("correcta" if option.correct else "incorrecta")
            lines.append(f"- [{chosen}] **{option.text}** — _{flag}_: {option.explanation}")
        if question.explanation:
            lines += ["", f"> {question.explanation}"]
        if question.reference:
            lines.append(f">\n> Repasar: `{question.reference}`")
    return "\n".join(lines) + "\n"
