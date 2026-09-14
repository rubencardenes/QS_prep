"""Configuración de proveedores, relativa a la aplicación y no al cwd."""
from dataclasses import dataclass
from pathlib import Path

import yaml

from .llm import ClaudeCLI, CodexCLI, LLMError

SETTINGS_PATH = Path(__file__).resolve().parents[1] / "settings.yaml"
DEFAULTS = {
    "chatgpt": {"model": "gpt-5.6-sol", "planning_model": "gpt-5.6-sol", "binary": "codex"},
    "claude": {"model": "sonnet", "planning_model": "haiku", "binary": "claude"},
}


@dataclass(frozen=True)
class Settings:
    provider: str = "chatgpt"
    model: str = "gpt-5.6-sol"
    planning_model: str = "gpt-5.6-sol"
    binary: str = "codex"
    timeout: int = 420

    @property
    def label(self) -> str:
        return "ChatGPT" if self.provider == "chatgpt" else "Claude"

    def client(self, model: str | None = None):
        cls = CodexCLI if self.provider == "chatgpt" else ClaudeCLI
        return cls(model=model or self.model, binary=self.binary, timeout=self.timeout)

    def models(self):
        choices = ([('gpt-5.6-sol', 'GPT-5.6 Sol')] if self.provider == 'chatgpt'
                   else [('sonnet', 'Sonnet'), ('opus', 'Opus'), ('haiku', 'Haiku')])
        if self.model not in dict(choices):
            choices.insert(0, (self.model, self.model))
        return choices


def load_settings(path: Path = SETTINGS_PATH) -> Settings:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else {}
    except (OSError, yaml.YAMLError) as exc:
        raise LLMError(f"No se pudo leer {path}: {exc}") from exc
    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise LLMError("settings.yaml debe contener un mapa de configuración.")
    provider = data.get("provider", "chatgpt")
    if not isinstance(provider, str) or provider not in DEFAULTS:
        raise LLMError("provider debe ser 'chatgpt' o 'claude'.")
    config = data.get(provider, {})
    if not isinstance(config, dict):
        raise LLMError(f"La sección {provider} debe ser un mapa.")
    values = {**DEFAULTS[provider], **config}
    for key in ("model", "planning_model", "binary"):
        if not isinstance(values[key], str) or not values[key].strip():
            raise LLMError(f"{provider}.{key} debe ser un texto no vacío.")
    timeout = data.get("timeout", 420)
    if type(timeout) is not int or timeout <= 0:
        raise LLMError("timeout debe ser un entero positivo (segundos).")
    return Settings(provider, values['model'], values['planning_model'], values['binary'], timeout)
