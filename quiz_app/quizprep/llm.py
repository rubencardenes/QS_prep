"""Proveedores CLI autenticados con suscripción; peticiones cancelables."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


class LLMError(RuntimeError):
    pass


class LLMClient(Protocol):
    def complete(self, system: str, prompt: str, cancel=None) -> str: ...


@dataclass
class CodexCLI:
    model: str = "gpt-5.6-sol"
    binary: str = "codex"
    timeout: int = 420

    def __post_init__(self) -> None:
        resolved = shutil.which(self.binary)
        if resolved is None:
            raise LLMError(f"No se encuentra «{self.binary}». Instala Codex CLI y ejecuta codex login con tu cuenta de ChatGPT.")
        self.binary = resolved

    def complete(self, system: str, prompt: str, cancel=None) -> str:
        env = os.environ.copy()
        env["NO_COLOR"] = "1"
        for key in ("OPENAI_API_KEY", "CODEX_API_KEY"):
            env.pop(key, None)
        with tempfile.TemporaryDirectory(prefix="quizprep-codex-") as workdir:
            output = Path(workdir) / "response.txt"
            command = [
                self.binary, "exec", "--ignore-user-config", "--ephemeral",
                "--skip-git-repo-check", "--sandbox", "read-only",
                "--color", "never", "--model", self.model,
                "-c", 'forced_login_method="chatgpt"',
                "-c", 'model_provider="openai"',
                "-c", "model_reasoning_effort=\"low\"",
                "--output-last-message", str(output), "-",
            ]
            request = system + "\n\nResponde directamente sin usar herramientas.\n\n" + prompt
            try:
                proc = subprocess.Popen(command, stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        text=True, cwd=workdir, env=env)
            except OSError as exc:
                raise LLMError(f"No se pudo lanzar Codex: {exc}") from exc
            try:
                stdout, stderr = _communicate(proc, self.timeout, cancel, request)
            except (TimeoutError, _Cancelled) as exc:
                proc.kill()
                proc.communicate()
                if isinstance(exc, _Cancelled):
                    raise
                raise LLMError(f"La generación superó el tiempo límite ({self.timeout}s).") from None
            if proc.returncode != 0:
                detail = (stderr or stdout or "").strip()[:1500]
                raise LLMError(f"Codex terminó con código {proc.returncode}. Comprueba codex login y el acceso a {self.model}.\n{detail}")
            try:
                result = output.read_text(encoding="utf-8").strip()
            except OSError as exc:
                raise LLMError("Codex no escribió la respuesta final.") from exc
            if not result:
                raise LLMError("Codex devolvió una respuesta vacía.")
            return result


@dataclass
class ClaudeCLI:
    model: str = "sonnet"
    binary: str = "claude"
    timeout: int = 420

    def __post_init__(self) -> None:
        resolved = shutil.which(self.binary)
        if resolved is None:
            raise LLMError(
                f"No se encuentra el ejecutable «{self.binary}» en el PATH.\n"
                "Instala Claude Code o ajusta la ruta en los ajustes."
            )
        self.binary = resolved

    def _build_command(self, system: str, prompt: str) -> list[str]:
        return [
            self.binary,
            "-p",
            prompt,
            "--system-prompt",
            system,
            "--model",
            self.model,
            "--output-format",
            "json",
            "--allowed-tools",
            "",
            "--no-session-persistence",
            "--strict-mcp-config",
            "--mcp-config",
            '{"mcpServers": {}}',
        ]

    def complete(self, system: str, prompt: str, cancel=None) -> str:
        """Ejecuta una petición y devuelve el texto de la respuesta.

        `cancel` es un callable sin argumentos que devuelve True para abortar.
        """
        env = os.environ.copy()
        # Sin colores ni telemetría interactiva en la salida.
        env["NO_COLOR"] = "1"

        # cwd neutro: evita que el CLI cargue el CLAUDE.md del proyecto.
        with tempfile.TemporaryDirectory(prefix="quizprep-") as workdir:
            try:
                proc = subprocess.Popen(
                    self._build_command(system, prompt),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=workdir,
                    env=env,
                )
            except OSError as exc:
                raise LLMError(f"No se pudo lanzar el CLI de Claude: {exc}") from exc

            try:
                stdout, stderr = _communicate(proc, self.timeout, cancel)
            except TimeoutError:
                proc.kill()
                proc.communicate()
                raise LLMError(
                    f"La generación superó el tiempo límite ({self.timeout}s)."
                ) from None
            except _Cancelled:
                proc.kill()
                proc.communicate()
                raise

        if proc.returncode != 0:
            detail = (stderr or stdout or "").strip()[:1500]
            raise LLMError(
                f"El CLI de Claude terminó con código {proc.returncode}.\n{detail}"
            )

        return _extract_result(stdout)


class _Cancelled(Exception):
    """Cancelación solicitada por el usuario."""


CancelledError = _Cancelled


def _communicate(proc: subprocess.Popen, timeout: int, cancel, input_text=None) -> tuple[str, str]:
    """Espera al proceso comprobando periódicamente la cancelación."""
    waited = 0.0
    step = 0.25
    while True:
        try:
            if cancel is not None and cancel():
                raise _Cancelled
            return proc.communicate(input=input_text, timeout=step)
        except subprocess.TimeoutExpired:
            input_text = None
            waited += step
            if cancel is not None and cancel():
                raise _Cancelled from None
            if waited >= timeout:
                raise TimeoutError from None


def _extract_result(stdout: str) -> str:
    stdout = stdout.strip()
    if not stdout:
        raise LLMError("El CLI de Claude no devolvió ninguna salida.")

    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError:
        # Salida inesperada: la devolvemos tal cual para que el parser lo intente.
        return stdout

    if isinstance(payload, dict):
        if payload.get("is_error"):
            raise LLMError(
                payload.get("result")
                or payload.get("api_error_status")
                or "El CLI de Claude devolvió un error."
            )
        result = payload.get("result")
        if isinstance(result, str):
            return result
    raise LLMError("Respuesta del CLI de Claude en un formato inesperado.")
