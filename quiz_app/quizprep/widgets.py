"""Widgets reutilizables: renderizado de Markdown y filas de opción."""

from __future__ import annotations

import html
import re

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

# --------------------------------------------------------------------------
# Markdown mínimo -> HTML, para poder darle estilo con CSS del documento.
# --------------------------------------------------------------------------

_FENCE = re.compile(r"```[a-zA-Z0-9_+\-]*\n(.*?)```", re.DOTALL)

# QLabel no aplica la hoja de estilo del documento, así que el estilo del
# código en línea se inyecta como atributo `style`.
_CODE_STYLE = "font-family: monospace; color: #5b8def;"
_COLOURS = {"ok": "#5fd08a", "bad": "#f0736a", "warn": "#e3b341", "muted": "#9aa1b1"}


def configure(palette) -> None:
    """Ajusta los colores usados en el texto enriquecido de los QLabel."""
    global _CODE_STYLE
    from .theme import MONO

    _CODE_STYLE = f"font-family: {MONO}; color: {palette.accent};"
    _COLOURS.update(
        ok=palette.ok, bad=palette.bad, warn=palette.warn, muted=palette.muted
    )


def _inline(text: str) -> str:
    """Renderiza énfasis, código y delimitadores LaTeX habituales del LLM."""
    token = re.compile(r"(`[^`]+`|\\\((?:.|\n)*?\\\)|\\\[(?:.|\n)*?\\\])")
    pieces: list[str] = []
    last = 0
    for match in token.finditer(text):
        pieces.append(_format_emphasis(html.escape(text[last:match.start()])))
        value = match.group(0)
        if value.startswith("`"):
            pieces.append(f'<span style="{_CODE_STYLE}">{html.escape(value[1:-1])}</span>')
        else:
            pieces.append(_math_to_html(value[2:-2]))
        last = match.end()
    pieces.append(_format_emphasis(html.escape(text[last:])))
    return "".join(pieces)


def _format_emphasis(text: str) -> str:
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    return re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<i>\1</i>", text)


def _math_to_html(expression: str) -> str:
    """Convierte un subconjunto de LaTeX a HTML soportado por QTextDocument."""
    value = html.escape(expression.strip())
    # Fracciones sencillas; las complejas siguen siendo legibles como (a)/(b).
    value = re.sub(r"\\frac\{([^{}]+)\}\{([^{}]+)\}", r"(\1)/(\2)", value)
    value = re.sub(r"\\(?:mathrm|text|operatorname)\{([^{}]+)\}", r"\1", value)
    symbols = {
        r"\cdot": "·", r"\times": "×", r"\leq": "≤", r"\le": "≤",
        r"\geq": "≥", r"\ge": "≥", r"\neq": "≠", r"\approx": "≈",
        r"\rightarrow": "→", r"\leftarrow": "←", r"\infty": "∞",
        r"\sum": "∑", r"\prod": "∏", r"\sqrt": "√",
        r"\alpha": "α", r"\beta": "β", r"\gamma": "γ", r"\delta": "δ",
        r"\epsilon": "ε", r"\lambda": "λ", r"\mu": "μ", r"\sigma": "σ",
        r"\theta": "θ", r"\pi": "π",
    }
    for latex, symbol in symbols.items():
        value = value.replace(latex, symbol)
    value = re.sub(r"\^\{([^{}]+)\}", r"<sup>\1</sup>", value)
    value = re.sub(r"_\{([^{}]+)\}", r"<sub>\1</sub>", value)
    value = re.sub(r"\^([A-Za-z0-9+-])", r"<sup>\1</sup>", value)
    value = re.sub(r"_([A-Za-z0-9+-])", r"<sub>\1</sub>", value)
    value = value.replace(r"\,", " ").replace(r"\;", " ")
    return f'<span style="font-family: serif; font-style: italic;">{value}</span>'


def _block(text: str) -> str:
    # QTextDocument no ejecuta MathJax. Conservamos cada fórmula de bloque como
    # una unidad y la renderizamos con el mismo conversor ligero que las inline.
    text = re.sub(
        r"\\\[(.*?)\\\]",
        lambda match: r"\[" + " ".join(match.group(1).splitlines()) + r"\]",
        text,
        flags=re.DOTALL,
    )
    out: list[str] = []
    in_list = False
    for raw_line in text.split("\n"):
        line = raw_line.rstrip()
        stripped = line.strip()
        bullet = re.match(r"^[-*+]\s+(.*)$", stripped) or re.match(
            r"^\d+[.)]\s+(.*)$", stripped
        )
        if bullet:
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{_inline(bullet.group(1))}</li>")
            continue
        if in_list:
            out.append("</ul>")
            in_list = False
        if not stripped:
            continue
        heading = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if heading:
            level = min(len(heading.group(1)) + 1, 6)
            out.append(f"<h{level}>{_inline(heading.group(2))}</h{level}>")
        elif stripped.startswith(">"):
            out.append(f"<blockquote>{_inline(stripped[1:].strip())}</blockquote>")
        else:
            out.append(f"<p>{_inline(stripped)}</p>")
    if in_list:
        out.append("</ul>")
    return "".join(out)


def md_to_html(text: str) -> str:
    """Convierte un subconjunto de Markdown (código, listas, énfasis) a HTML."""
    pieces: list[str] = []
    last = 0
    for match in _FENCE.finditer(text):
        pieces.append(_block(text[last : match.start()]))
        code = html.escape(match.group(1).rstrip("\n"))
        pieces.append(f"<pre><code>{code}</code></pre>")
        last = match.end()
    pieces.append(_block(text[last:]))
    return "".join(pieces) or "<p></p>"


class MarkdownView(QTextBrowser):
    """QTextBrowser que se ajusta a la altura de su contenido."""

    def __init__(self, css: str, plain: bool = False, parent: QWidget | None = None):
        super().__init__(parent)
        if plain:
            self.setObjectName("Plain")
        self.setOpenExternalLinks(True)
        self.setReadOnly(True)
        self.document().setDefaultStyleSheet(css)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFrameShape(QFrame.Shape.NoFrame if plain else QFrame.Shape.StyledPanel)
        self.document().documentLayout().documentSizeChanged.connect(self._fit)

    def set_markdown(self, text: str) -> None:
        self.setHtml(md_to_html(text))
        self._fit()

    def _fit(self, *_) -> None:
        doc = self.document()
        doc.setTextWidth(max(self.viewport().width(), 50))
        height = int(doc.size().height() + 2 * doc.documentMargin() + 6)
        self.setFixedHeight(max(height, 28))

    def resizeEvent(self, event) -> None:  # noqa: N802 (API de Qt)
        super().resizeEvent(event)
        self._fit()


class OptionRow(QFrame):
    """Una opción de respuesta: casilla + texto con ajuste de línea."""

    toggled = Signal(int, bool)

    def __init__(self, index: int, text: str, parent: QWidget | None = None):
        super().__init__(parent)
        self.index = index
        self.setObjectName("Option")
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 10, 12, 10)
        outer.setSpacing(6)

        row = QHBoxLayout()
        row.setSpacing(10)
        self.check = QCheckBox()
        self.check.setCursor(Qt.CursorShape.PointingHandCursor)
        self.check.toggled.connect(self._on_toggled)
        row.addWidget(self.check, 0, Qt.AlignmentFlag.AlignTop)

        self.label = QLabel(md_to_html(text))
        self.label.setTextFormat(Qt.TextFormat.RichText)
        self.label.setWordWrap(True)
        self.label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        row.addWidget(self.label, 1)
        outer.addLayout(row)

        self.verdict = QLabel()
        self.verdict.setWordWrap(True)
        self.verdict.setTextFormat(Qt.TextFormat.RichText)
        self.verdict.setObjectName("Muted")
        self.verdict.hide()
        outer.addWidget(self.verdict)

    # -- interacción -------------------------------------------------------
    def mousePressEvent(self, event) -> None:  # noqa: N802 (API de Qt)
        if self.check.isEnabled():
            self.check.toggle()
        super().mousePressEvent(event)

    def _on_toggled(self, on: bool) -> None:
        self._restyle("OptionSel" if on else "Option")
        self.toggled.emit(self.index, on)

    def _restyle(self, name: str) -> None:
        self.setObjectName(name)
        self.style().unpolish(self)
        self.style().polish(self)

    def set_checked(self, value: bool) -> None:
        self.check.blockSignals(True)
        self.check.setChecked(value)
        self.check.blockSignals(False)
        self._restyle("OptionSel" if value else "Option")

    # -- modo revisión -----------------------------------------------------
    def show_review(self, chosen: bool, correct: bool, explanation: str) -> None:
        self.check.setEnabled(False)
        self.setCursor(Qt.CursorShape.ArrowCursor)
        if correct and chosen:
            name, tag, tone = "OptionOk", "✓ Correcta — la marcaste", "ok"
        elif correct and not chosen:
            name, tag, tone = "OptionMissed", "✓ Correcta — no la marcaste", "warn"
        elif chosen:
            name, tag, tone = "OptionBad", "✗ Incorrecta — la marcaste", "bad"
        else:
            name, tag, tone = "Option", "✗ Incorrecta", "muted"
        self._restyle(name)
        detail = f" · {_inline(explanation)}" if explanation else ""
        self.verdict.setText(
            f'<b style="color: {_COLOURS[tone]};">{tag}</b>'
            f'<span style="color: {_COLOURS["muted"]};">{detail}</span>'
        )
        self.verdict.show()
