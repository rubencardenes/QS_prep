"""Modelo de datos del test."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Option:
    text: str
    correct: bool
    explanation: str = ""


@dataclass
class Question:
    question: str
    options: list[Option]
    topic: str = ""
    difficulty: str = ""
    explanation: str = ""
    reference: str = ""
    selected: set[int] = field(default_factory=set)

    @property
    def correct_indices(self) -> set[int]:
        return {i for i, o in enumerate(self.options) if o.correct}

    @property
    def multi(self) -> bool:
        return len(self.correct_indices) > 1

    def score(self) -> float:
        """Puntuación parcial en [0, 1].

        Aciertos menos falsos positivos, normalizado por el número de
        respuestas correctas. Marcarlo todo no puntúa.
        """
        correct = self.correct_indices
        if not correct:
            return 0.0
        hits = len(self.selected & correct)
        misses = len(self.selected - correct)
        return max(0.0, min(1.0, (hits - misses) / len(correct)))

    @property
    def answered(self) -> bool:
        return bool(self.selected)

    @property
    def is_perfect(self) -> bool:
        return self.selected == self.correct_indices


@dataclass
class Quiz:
    topic: str
    difficulty: str
    questions: list[Question]
    index: int = 0

    @property
    def current(self) -> Question:
        return self.questions[self.index]

    @property
    def total(self) -> int:
        return len(self.questions)

    def points(self) -> float:
        return sum(q.score() for q in self.questions)

    def percentage(self) -> float:
        return 100.0 * self.points() / self.total if self.total else 0.0

    def perfect_count(self) -> int:
        return sum(1 for q in self.questions if q.is_perfect)

    def failed(self) -> list[Question]:
        return [q for q in self.questions if not q.is_perfect]
