"""Paleta y hoja de estilos, adaptada a modo claro u oscuro del sistema."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

ASSETS = Path(__file__).resolve().parents[1] / "assets"
CHECK_ICON = (ASSETS / "check.svg").as_posix()


@dataclass(frozen=True)
class Palette:
    bg: str
    surface: str
    surface_alt: str
    border: str
    text: str
    muted: str
    accent: str
    accent_text: str
    ok: str
    ok_bg: str
    bad: str
    bad_bg: str
    warn: str
    warn_bg: str
    code_bg: str


DARK = Palette(
    bg="#16181d",
    surface="#1e2128",
    surface_alt="#242832",
    border="#333844",
    text="#e6e8ee",
    muted="#9aa1b1",
    accent="#5b8def",
    accent_text="#ffffff",
    ok="#5fd08a",
    ok_bg="#1c3226",
    bad="#f0736a",
    bad_bg="#3a2020",
    warn="#e3b341",
    warn_bg="#3a3020",
    code_bg="#12141a",
)

LIGHT = Palette(
    bg="#f4f5f8",
    surface="#ffffff",
    surface_alt="#f0f2f6",
    border="#d8dce4",
    text="#1d2128",
    muted="#646b7a",
    accent="#2f6fdc",
    accent_text="#ffffff",
    ok="#1c8c50",
    ok_bg="#e4f6ec",
    bad="#c0392b",
    bad_bg="#fdeceb",
    warn="#9a7212",
    warn_bg="#fbf3dd",
    code_bg="#f1f3f7",
)

MONO = "'JetBrains Mono', 'SF Mono', 'Menlo', 'Consolas', monospace"


def stylesheet(p: Palette) -> str:
    return f"""
    QWidget {{
        background-color: {p.bg};
        color: {p.text};
        font-size: 14px;
    }}
    QScrollArea, QScrollArea > QWidget > QWidget {{ background: transparent; border: none; }}
    QLabel, QCheckBox {{ background: transparent; }}

    QLabel#Title {{ font-size: 26px; font-weight: 700; }}
    QLabel#Subtitle {{ color: {p.muted}; font-size: 14px; }}
    QLabel#SectionTitle {{ font-size: 16px; font-weight: 600; }}
    QLabel#Muted {{ color: {p.muted}; }}
    QLabel#Score {{ font-size: 46px; font-weight: 700; }}
    QLabel#Chip {{
        background: {p.surface_alt}; color: {p.muted};
        border: 1px solid {p.border}; border-radius: 10px;
        padding: 3px 10px; font-size: 12px;
    }}

    QFrame#Card {{
        background-color: {p.surface};
        border: 1px solid {p.border};
        border-radius: 12px;
    }}
    QFrame#Option {{
        background-color: {p.surface};
        border: 1px solid {p.border};
        border-radius: 10px;
    }}
    QFrame#Option:hover {{ border-color: {p.accent}; }}
    QFrame#OptionSel {{
        background-color: {p.surface_alt};
        border: 1px solid {p.accent};
        border-radius: 10px;
    }}
    QFrame#OptionOk {{
        background-color: {p.ok_bg}; border: 1px solid {p.ok}; border-radius: 10px;
    }}
    QFrame#OptionBad {{
        background-color: {p.bad_bg}; border: 1px solid {p.bad}; border-radius: 10px;
    }}
    QFrame#OptionMissed {{
        background-color: {p.warn_bg}; border: 1px dashed {p.warn}; border-radius: 10px;
    }}

    QTextBrowser {{
        background-color: {p.surface_alt};
        border: 1px solid {p.border};
        border-radius: 10px;
        padding: 6px 10px;
    }}
    QTextBrowser#Plain {{
        background: transparent; border: none; padding: 0px;
    }}

    QPushButton {{
        background-color: {p.surface_alt};
        border: 1px solid {p.border};
        border-radius: 8px;
        padding: 8px 16px;
    }}
    QPushButton:hover {{ border-color: {p.accent}; }}
    QPushButton:disabled {{ color: {p.muted}; border-color: {p.border}; }}
    QPushButton#Primary {{
        background-color: {p.accent}; color: {p.accent_text};
        border: 1px solid {p.accent}; font-weight: 600;
        padding: 10px 22px;
    }}
    QPushButton#Primary:disabled {{ background-color: {p.border}; color: {p.muted}; }}
    QPushButton#Danger {{ color: {p.bad}; }}

    QComboBox, QSpinBox {{
        background-color: {p.surface};
        border: 1px solid {p.border};
        border-radius: 8px;
        padding: 6px 10px;
        min-height: 20px;
    }}
    QComboBox::drop-down {{ border: none; width: 22px; }}
    QComboBox QAbstractItemView {{
        background-color: {p.surface};
        border: 1px solid {p.border};
        selection-background-color: {p.accent};
        selection-color: {p.accent_text};
        outline: none;
    }}

    QCheckBox::indicator {{
        width: 18px; height: 18px;
        border: 1px solid {p.border}; border-radius: 5px;
        background: {p.surface_alt};
    }}
    QCheckBox::indicator:checked {{
        background: {p.accent};
        border-color: {p.accent};
        image: url({CHECK_ICON});
    }}
    QCheckBox::indicator:disabled {{ opacity: 0.7; }}

    QProgressBar {{
        background-color: {p.surface_alt};
        border: none; border-radius: 4px;
        height: 8px; text-align: center; color: transparent;
    }}
    QProgressBar::chunk {{ background-color: {p.accent}; border-radius: 4px; }}

    QListWidget {{
        background-color: {p.surface};
        border: 1px solid {p.border};
        border-radius: 10px;
        padding: 4px;
    }}
    QScrollBar:vertical {{
        background: transparent; width: 10px; margin: 2px;
    }}
    QScrollBar::handle:vertical {{
        background: {p.border}; border-radius: 5px; min-height: 30px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
    """


def document_css(p: Palette) -> str:
    """CSS aplicado al documento interno de los QTextBrowser."""
    return f"""
    body {{ color: {p.text}; }}
    p {{ margin: 4px 0; }}
    code {{
        font-family: {MONO}; font-size: 13px;
        background-color: {p.code_bg}; color: {p.accent};
        padding: 1px 4px; border-radius: 4px;
    }}
    pre {{
        font-family: {MONO}; font-size: 13px;
        background-color: {p.code_bg};
        padding: 8px; border-radius: 8px;
        white-space: pre-wrap;
    }}
    pre code {{ background: transparent; color: {p.text}; padding: 0; }}
    h1, h2, h3 {{ margin: 8px 0 4px 0; }}
    ul, ol {{ margin: 4px 0 4px 18px; }}
    blockquote {{ color: {p.muted}; margin: 6px 0; }}
    """
