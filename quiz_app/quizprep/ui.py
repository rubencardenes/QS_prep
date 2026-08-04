"""Interfaz PySide6 de la aplicación de tests de entrevista."""

from __future__ import annotations

import time

from PySide6.QtCore import Qt, QThread, QTimer, Signal
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from . import store
from .generator import (
    ANALYSIS_SYSTEM,
    build_analysis_prompt,
    generate_quiz,
)
from .llm import MODELS, ClaudeCLI, CancelledError, LLMError
from .models import Quiz
from .theme import DARK, LIGHT, Palette, document_css, stylesheet
from .topics import DIFFICULTIES, TOPICS, TOPICS_BY_KEY
from .widgets import MarkdownView, OptionRow, configure as configure_widgets


class Worker(QThread):
    """Ejecuta una función lenta fuera del hilo de la interfaz."""

    done = Signal(object)
    failed = Signal(str)
    progress = Signal(str)

    def __init__(self, fn, parent=None):
        super().__init__(parent)
        self._fn = fn
        self._cancelled = False

    def cancel(self) -> None:
        self._cancelled = True

    def is_cancelled(self) -> bool:
        return self._cancelled

    def run(self) -> None:  # noqa: D102
        try:
            result = self._fn(self.is_cancelled, self.progress.emit)
        except CancelledError:
            return
        except LLMError as exc:
            self.failed.emit(str(exc))
            return
        except Exception as exc:  # red de seguridad: nunca matar el hilo en silencio
            self.failed.emit(f"Error inesperado: {exc}")
            return
        if not self._cancelled:
            self.done.emit(result)


def _card() -> QFrame:
    frame = QFrame()
    frame.setObjectName("Card")
    return frame


# ---------------------------------------------------------------------------
# Página 1 — configuración
# ---------------------------------------------------------------------------


class SetupPage(QWidget):
    start_requested = Signal(dict)
    cancel_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(40, 32, 40, 32)
        root.setSpacing(18)

        title = QLabel("Preparación de entrevista técnica")
        title.setObjectName("Title")
        subtitle = QLabel(
            "Tests de opción múltiple generados con Claude. "
            "Ojo: una pregunta puede tener varias respuestas correctas."
        )
        subtitle.setObjectName("Subtitle")
        subtitle.setWordWrap(True)
        root.addWidget(title)
        root.addWidget(subtitle)

        card = _card()
        form = QFormLayout(card)
        form.setContentsMargins(24, 24, 24, 24)
        form.setSpacing(14)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.topic = QComboBox()
        for topic in TOPICS:
            self.topic.addItem(topic.label, topic.key)
        self.topic.currentIndexChanged.connect(self._on_topic_changed)

        self.difficulty = QComboBox()
        for key, label in DIFFICULTIES:
            self.difficulty.addItem(label, key)
        self.difficulty.setCurrentIndex(1)

        self.count = QSpinBox()
        self.count.setRange(3, 25)
        self.count.setValue(10)

        self.language = QComboBox()
        self.language.addItem("Español", "es")
        self.language.addItem("Inglés", "en")

        self.model = QComboBox()
        for key, label in MODELS:
            self.model.addItem(label, key)

        form.addRow("Tema", self.topic)
        form.addRow("Nivel", self.difficulty)
        form.addRow("Nº de preguntas", self.count)
        form.addRow("Idioma", self.language)
        form.addRow("Modelo", self.model)

        self.use_notes = QCheckBox("Usar mis apuntes del repo como contexto")
        self.use_notes.setChecked(True)
        self.avoid_repeats = QCheckBox("Evitar preguntas que ya me han salido")
        self.avoid_repeats.setChecked(True)
        form.addRow("", self.use_notes)
        form.addRow("", self.avoid_repeats)
        root.addWidget(card)

        self.start = QPushButton("Generar test")
        self.start.setObjectName("Primary")
        self.start.clicked.connect(self._emit_start)

        self.cancel = QPushButton("Cancelar")
        self.cancel.clicked.connect(self.cancel_requested.emit)
        self.cancel.hide()

        buttons = QHBoxLayout()
        buttons.addWidget(self.start)
        buttons.addWidget(self.cancel)
        buttons.addStretch(1)
        root.addLayout(buttons)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.hide()
        self.status = QLabel("")
        self.status.setObjectName("Muted")
        self.status.setWordWrap(True)
        root.addWidget(self.progress)
        root.addWidget(self.status)

        self.history = QLabel("")
        self.history.setObjectName("Muted")
        self.history.setWordWrap(True)
        root.addWidget(self.history)
        root.addStretch(1)

        self._on_topic_changed()
        self.refresh_history()

    def _on_topic_changed(self) -> None:
        topic = TOPICS_BY_KEY[self.topic.currentData()]
        files = topic.notes_paths()
        if files:
            names = ", ".join(p.name for p in files)
            self.use_notes.setEnabled(True)
            self.use_notes.setText(f"Usar mis apuntes como contexto ({names})")
        else:
            self.use_notes.setEnabled(False)
            self.use_notes.setText("Sin apuntes locales para este tema")

    def refresh_history(self) -> None:
        results = store.recent_results(5)
        if not results:
            self.history.setText("")
            return
        lines = [
            f"· {r['when'][:16].replace('T', ' ')} — {r['topic']} "
            f"({r['difficulty']}): {r['percentage']}%"
            for r in results
        ]
        self.history.setText("Últimos tests:\n" + "\n".join(lines))

    def _emit_start(self) -> None:
        self.start_requested.emit(
            {
                "topic_key": self.topic.currentData(),
                "difficulty": self.difficulty.currentData(),
                "count": self.count.value(),
                "language": self.language.currentData(),
                "model": self.model.currentData(),
                "use_notes": self.use_notes.isEnabled()
                and self.use_notes.isChecked(),
                "avoid_repeats": self.avoid_repeats.isChecked(),
            }
        )

    def set_busy(self, busy: bool, message: str = "") -> None:
        self.start.setEnabled(not busy)
        self.cancel.setVisible(busy)
        self.progress.setVisible(busy)
        for widget in (
            self.topic,
            self.difficulty,
            self.count,
            self.language,
            self.model,
        ):
            widget.setEnabled(not busy)
        self.status.setText(message)


# ---------------------------------------------------------------------------
# Página 2 — test
# ---------------------------------------------------------------------------


class QuizPage(QWidget):
    finish_requested = Signal()
    abort_requested = Signal()

    def __init__(self, css: str, parent=None):
        super().__init__(parent)
        self._css = css
        self.quiz: Quiz | None = None
        self._rows: list[OptionRow] = []

        root = QVBoxLayout(self)
        root.setContentsMargins(32, 24, 32, 24)
        root.setSpacing(14)

        header = QHBoxLayout()
        self.counter = QLabel()
        self.counter.setObjectName("SectionTitle")
        self.chip = QLabel()
        self.chip.setObjectName("Chip")
        self.clock = QLabel()
        self.clock.setObjectName("Muted")
        header.addWidget(self.counter)
        header.addWidget(self.chip)
        header.addStretch(1)
        header.addWidget(self.clock)
        root.addLayout(header)

        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        root.addWidget(self.progress)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        self.body = QVBoxLayout(content)
        self.body.setContentsMargins(0, 8, 8, 8)
        self.body.setSpacing(12)
        scroll.setWidget(content)
        root.addWidget(scroll, 1)

        self.question_view = MarkdownView(css)
        self.body.addWidget(self.question_view)

        self.hint = QLabel("Puede haber más de una respuesta correcta.")
        self.hint.setObjectName("Muted")
        self.body.addWidget(self.hint)

        self.options_box = QVBoxLayout()
        self.options_box.setSpacing(8)
        self.body.addLayout(self.options_box)
        self.body.addStretch(1)

        nav = QHBoxLayout()
        self.abort = QPushButton("Abandonar")
        self.abort.setObjectName("Danger")
        self.abort.clicked.connect(self.abort_requested.emit)
        self.prev = QPushButton("◀  Anterior")
        self.prev.clicked.connect(self.go_prev)
        self.next = QPushButton("Siguiente  ▶")
        self.next.setObjectName("Primary")
        self.next.clicked.connect(self.go_next)
        self.pending = QLabel()
        self.pending.setObjectName("Muted")
        nav.addWidget(self.abort)
        nav.addStretch(1)
        nav.addWidget(self.pending)
        nav.addWidget(self.prev)
        nav.addWidget(self.next)
        root.addLayout(nav)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._started = 0.0

        QShortcut(QKeySequence(Qt.Key.Key_Right), self, activated=self.go_next)
        QShortcut(QKeySequence(Qt.Key.Key_Left), self, activated=self.go_prev)
        for n in range(1, 6):
            QShortcut(
                QKeySequence(str(n)),
                self,
                activated=lambda i=n - 1: self._toggle_by_key(i),
            )

    # -- ciclo de vida -----------------------------------------------------
    def start(self, quiz: Quiz) -> None:
        self.quiz = quiz
        quiz.index = 0
        self._started = time.monotonic()
        self._timer.start(1000)
        self._tick()
        self.render()

    def stop_timer(self) -> None:
        self._timer.stop()

    def elapsed(self) -> int:
        return int(time.monotonic() - self._started)

    def _tick(self) -> None:
        seconds = self.elapsed()
        self.clock.setText(f"⏱  {seconds // 60:02d}:{seconds % 60:02d}")

    # -- render ------------------------------------------------------------
    def render(self) -> None:
        quiz = self.quiz
        if quiz is None:
            return
        question = quiz.current
        self.counter.setText(f"Pregunta {quiz.index + 1} de {quiz.total}")
        self.chip.setText(question.topic or quiz.topic)
        self.progress.setRange(0, quiz.total)
        self.progress.setValue(quiz.index + 1)
        self.question_view.set_markdown(question.question)

        while self.options_box.count():
            item = self.options_box.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self._rows = []

        for i, option in enumerate(question.options):
            row = OptionRow(i, option.text)
            row.set_checked(i in question.selected)
            row.toggled.connect(self._on_toggle)
            self.options_box.addWidget(row)
            self._rows.append(row)

        self.prev.setEnabled(quiz.index > 0)
        last = quiz.index == quiz.total - 1
        self.next.setText("Corregir test  ✓" if last else "Siguiente  ▶")
        unanswered = sum(1 for q in quiz.questions if not q.answered)
        self.pending.setText(
            "" if not unanswered else f"{unanswered} sin responder"
        )

    def _on_toggle(self, index: int, checked: bool) -> None:
        if self.quiz is None:
            return
        selected = self.quiz.current.selected
        if checked:
            selected.add(index)
        else:
            selected.discard(index)
        unanswered = sum(1 for q in self.quiz.questions if not q.answered)
        self.pending.setText("" if not unanswered else f"{unanswered} sin responder")

    def _toggle_by_key(self, index: int) -> None:
        if 0 <= index < len(self._rows):
            self._rows[index].check.toggle()

    # -- navegación --------------------------------------------------------
    def go_next(self) -> None:
        if self.quiz is None:
            return
        if self.quiz.index >= self.quiz.total - 1:
            self.finish_requested.emit()
            return
        self.quiz.index += 1
        self.render()

    def go_prev(self) -> None:
        if self.quiz is None or self.quiz.index == 0:
            return
        self.quiz.index -= 1
        self.render()


# ---------------------------------------------------------------------------
# Página 3 — resultados
# ---------------------------------------------------------------------------


class ResultsPage(QWidget):
    new_quiz_requested = Signal()
    analysis_requested = Signal()
    export_requested = Signal()

    def __init__(self, css: str, palette: Palette, parent=None):
        super().__init__(parent)
        self._css = css
        self._palette = palette
        self.quiz: Quiz | None = None
        self.analysis_text = ""
        self._analysis_card: QFrame | None = None

        root = QVBoxLayout(self)
        root.setContentsMargins(32, 24, 32, 24)
        root.setSpacing(14)

        head = _card()
        head_layout = QHBoxLayout(head)
        head_layout.setContentsMargins(24, 18, 24, 18)
        self.score = QLabel("—")
        self.score.setObjectName("Score")
        summary_box = QVBoxLayout()
        self.summary = QLabel()
        self.summary.setObjectName("SectionTitle")
        self.detail = QLabel()
        self.detail.setObjectName("Muted")
        self.detail.setWordWrap(True)
        summary_box.addWidget(self.summary)
        summary_box.addWidget(self.detail)
        head_layout.addWidget(self.score)
        head_layout.addSpacing(20)
        head_layout.addLayout(summary_box, 1)
        root.addWidget(head)

        self.analysis_status = QLabel()
        self.analysis_status.setObjectName("Muted")
        self.analysis_status.hide()
        root.addWidget(self.analysis_status)

        self._scroll = scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self._content = QWidget()
        self.cards = QVBoxLayout(self._content)
        self.cards.setContentsMargins(0, 4, 8, 8)
        self.cards.setSpacing(14)
        scroll.setWidget(self._content)
        root.addWidget(scroll, 1)

        buttons = QHBoxLayout()
        self.analysis_btn = QPushButton("Diagnóstico del tutor")
        self.analysis_btn.clicked.connect(self.analysis_requested.emit)
        self.export_btn = QPushButton("Exportar a Markdown")
        self.export_btn.clicked.connect(self.export_requested.emit)
        self.new_btn = QPushButton("Nuevo test")
        self.new_btn.setObjectName("Primary")
        self.new_btn.clicked.connect(self.new_quiz_requested.emit)
        buttons.addWidget(self.analysis_btn)
        buttons.addWidget(self.export_btn)
        buttons.addStretch(1)
        buttons.addWidget(self.new_btn)
        root.addLayout(buttons)

    def show_results(self, quiz: Quiz, elapsed: int) -> None:
        self.quiz = quiz
        self.analysis_text = ""
        self._analysis_card = None
        self.analysis_status.hide()
        self.analysis_btn.setEnabled(True)

        pct = quiz.percentage()
        colour = (
            self._palette.ok
            if pct >= 75
            else (self._palette.warn if pct >= 50 else self._palette.bad)
        )
        self.score.setText(f"{pct:.0f}%")
        self.score.setStyleSheet(f"color: {colour};")
        self.summary.setText(
            f"{quiz.perfect_count()} de {quiz.total} preguntas perfectas · "
            f"{quiz.points():.2f} puntos"
        )
        self.detail.setText(
            f"{quiz.topic} · nivel {quiz.difficulty} · "
            f"tiempo {elapsed // 60:02d}:{elapsed % 60:02d}. "
            "La puntuación es parcial: cada acierto suma y cada marca errónea "
            "resta dentro de la misma pregunta."
        )

        while self.cards.count():
            item = self.cards.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        for i, question in enumerate(quiz.questions, 1):
            self.cards.addWidget(self._build_card(i, question))
        self.cards.addStretch(1)

    def _build_card(self, number: int, question) -> QFrame:
        card = _card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        if question.is_perfect:
            mark, colour = "✓ Correcta", self._palette.ok
        elif question.score() > 0:
            mark, colour = "◐ Parcial", self._palette.warn
        else:
            mark, colour = "✗ Fallada", self._palette.bad

        header = QHBoxLayout()
        title = QLabel(f"Pregunta {number}")
        title.setObjectName("SectionTitle")
        verdict = QLabel(mark)
        verdict.setStyleSheet(f"color: {colour}; font-weight: 600;")
        chip = QLabel(question.topic or "")
        chip.setObjectName("Chip")
        header.addWidget(title)
        header.addWidget(verdict)
        header.addStretch(1)
        if question.topic:
            header.addWidget(chip)
        layout.addLayout(header)

        view = MarkdownView(self._css)
        view.set_markdown(question.question)
        layout.addWidget(view)

        for i, option in enumerate(question.options):
            row = OptionRow(i, option.text)
            row.set_checked(i in question.selected)
            row.show_review(i in question.selected, option.correct, option.explanation)
            layout.addWidget(row)

        if question.explanation:
            note = MarkdownView(self._css, plain=True)
            note.set_markdown(f"> {question.explanation}")
            layout.addWidget(note)
        if question.reference:
            ref = QLabel(f"Repasar: {question.reference}")
            ref.setObjectName("Chip")
            ref.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
            layout.addWidget(ref)
        return card

    def set_analysis_busy(self, busy: bool, message: str = "") -> None:
        self.analysis_btn.setEnabled(not busy)
        self.analysis_status.setVisible(bool(message))
        self.analysis_status.setText(message)

    def set_analysis(self, text: str) -> None:
        """Inserta el diagnóstico como primera tarjeta del área con scroll."""
        self.analysis_text = text
        if self._analysis_card is not None:
            self.cards.removeWidget(self._analysis_card)
            self._analysis_card.deleteLater()

        card = _card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)
        title = QLabel("Diagnóstico del tutor")
        title.setObjectName("SectionTitle")
        layout.addWidget(title)
        view = MarkdownView(self._css, plain=True)
        view.set_markdown(text)
        layout.addWidget(view)

        self.cards.insertWidget(0, card)
        self._analysis_card = card
        self.analysis_status.hide()
        self._scroll.verticalScrollBar().setValue(0)


# ---------------------------------------------------------------------------
# Ventana principal
# ---------------------------------------------------------------------------


class MainWindow(QMainWindow):
    def __init__(self, palette: Palette):
        super().__init__()
        self.setWindowTitle("Quantum Prep — Test de entrevista")
        self.resize(1040, 800)
        self.setMinimumSize(880, 640)

        self._palette = palette
        self._css = document_css(palette)
        self._worker: Worker | None = None
        self._ticker: QTimer | None = None
        self._config: dict = {}
        self._elapsed = 0

        self.stack = QStackedWidget()
        self.setup_page = SetupPage()
        self.quiz_page = QuizPage(self._css)
        self.results_page = ResultsPage(self._css, palette)
        for page in (self.setup_page, self.quiz_page, self.results_page):
            self.stack.addWidget(page)
        self.setCentralWidget(self.stack)

        self.setup_page.start_requested.connect(self.start_generation)
        self.setup_page.cancel_requested.connect(self.cancel_generation)
        self.quiz_page.finish_requested.connect(self.finish_quiz)
        self.quiz_page.abort_requested.connect(self.abort_quiz)
        self.results_page.new_quiz_requested.connect(self.go_setup)
        self.results_page.analysis_requested.connect(self.request_analysis)
        self.results_page.export_requested.connect(self.export_markdown)

    # -- generación --------------------------------------------------------
    def start_generation(self, config: dict) -> None:
        try:
            client = ClaudeCLI(model=config["model"])
        except LLMError as exc:
            QMessageBox.critical(self, "Falta el CLI de Claude", str(exc))
            return

        self._config = config
        avoid = (
            store.asked_questions(config["topic_key"])
            if config["avoid_repeats"]
            else []
        )

        started = time.monotonic()
        self.setup_page.set_busy(True, "Generando preguntas…")

        state = {"detail": "Preparando la petición…"}
        ticker = QTimer(self)

        def tick() -> None:
            seconds = int(time.monotonic() - started)
            self.setup_page.status.setText(
                f"Generando {config['count']} preguntas con Claude · "
                f"{state['detail']} · {seconds // 60:02d}:{seconds % 60:02d}"
            )

        ticker.timeout.connect(tick)
        ticker.start(1000)
        self._ticker = ticker
        tick()

        def job(cancel, report):
            return generate_quiz(
                client,
                topic_key=config["topic_key"],
                difficulty=config["difficulty"],
                count=config["count"],
                language=config["language"],
                use_notes=config["use_notes"],
                avoid=avoid,
                cancel=cancel,
                report=report,
            )

        worker = Worker(job, self)
        self._worker = worker

        def cleanup() -> None:
            self._stop_ticker()
            self.setup_page.set_busy(False, "")
            self._worker = None

        def on_done(quiz: Quiz) -> None:
            cleanup()
            store.remember_questions(
                config["topic_key"], [q.question for q in quiz.questions]
            )
            self.quiz_page.start(quiz)
            self.stack.setCurrentWidget(self.quiz_page)

        def on_failed(message: str) -> None:
            cleanup()
            QMessageBox.critical(self, "No se pudo generar el test", message)

        def on_progress(message: str) -> None:
            state["detail"] = message
            tick()

        worker.progress.connect(on_progress)
        worker.done.connect(on_done)
        worker.failed.connect(on_failed)
        worker.finished.connect(worker.deleteLater)
        worker.start()

    def _stop_ticker(self) -> None:
        if self._ticker is not None:
            self._ticker.stop()
            self._ticker.deleteLater()
            self._ticker = None

    def cancel_generation(self) -> None:
        if self._worker is not None:
            self._worker.cancel()
            self._stop_ticker()
            self.setup_page.set_busy(False, "Generación cancelada.")
            self._worker = None

    # -- test --------------------------------------------------------------
    def finish_quiz(self) -> None:
        quiz = self.quiz_page.quiz
        if quiz is None:
            return
        unanswered = sum(1 for q in quiz.questions if not q.answered)
        if unanswered:
            answer = QMessageBox.question(
                self,
                "Preguntas sin responder",
                f"Quedan {unanswered} preguntas sin responder y contarán como "
                "falladas. ¿Corregir de todos modos?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return
        self.quiz_page.stop_timer()
        self._elapsed = self.quiz_page.elapsed()
        store.record_result(self._config.get("topic_key", ""), quiz)
        self.setup_page.refresh_history()
        self.results_page.show_results(quiz, self._elapsed)
        self.stack.setCurrentWidget(self.results_page)

    def abort_quiz(self) -> None:
        answer = QMessageBox.question(
            self,
            "Abandonar test",
            "Se perderán las respuestas de este test. ¿Seguro?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            self.quiz_page.stop_timer()
            self.go_setup()

    def go_setup(self) -> None:
        self.setup_page.refresh_history()
        self.stack.setCurrentWidget(self.setup_page)

    # -- diagnóstico -------------------------------------------------------
    def request_analysis(self) -> None:
        quiz = self.results_page.quiz
        if quiz is None or self._worker is not None:
            return
        try:
            client = ClaudeCLI(model=self._config.get("model", "sonnet"))
        except LLMError as exc:
            QMessageBox.critical(self, "Falta el CLI de Claude", str(exc))
            return

        prompt = build_analysis_prompt(quiz, self._config.get("language", "es"))
        self.results_page.set_analysis_busy(True, "Pidiendo el diagnóstico a Claude…")

        def job(cancel, _report):
            return client.complete(ANALYSIS_SYSTEM, prompt, cancel=cancel)

        worker = Worker(job, self)
        self._worker = worker

        def on_done(text: str) -> None:
            self._worker = None
            self.results_page.set_analysis_busy(False)
            self.results_page.set_analysis(text)

        def on_failed(message: str) -> None:
            self._worker = None
            self.results_page.set_analysis_busy(False)
            QMessageBox.critical(self, "No se pudo obtener el diagnóstico", message)

        worker.done.connect(on_done)
        worker.failed.connect(on_failed)
        worker.finished.connect(worker.deleteLater)
        worker.start()

    # -- exportación -------------------------------------------------------
    def export_markdown(self) -> None:
        quiz = self.results_page.quiz
        if quiz is None:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Guardar revisión", "revision_test.md", "Markdown (*.md)"
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(
                    store.quiz_to_markdown(quiz, self.results_page.analysis_text)
                )
        except OSError as exc:
            QMessageBox.critical(self, "Error al guardar", str(exc))
            return
        QMessageBox.information(self, "Guardado", f"Revisión guardada en:\n{path}")

    def closeEvent(self, event) -> None:  # noqa: N802 (API de Qt)
        if self._worker is not None:
            self._worker.cancel()
            self._worker.wait(3000)
        super().closeEvent(event)


def run() -> int:
    app = QApplication.instance() or QApplication([])
    app.setApplicationName("Quantum Prep Quiz")
    dark = app.palette().window().color().lightness() < 128
    palette = DARK if dark else LIGHT
    app.setStyleSheet(stylesheet(palette))
    configure_widgets(palette)
    window = MainWindow(palette)
    window.show()
    return app.exec()
