"""Catálogo de temas y enlace con los apuntes locales del repo."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

# Raíz del repo: quiz_app/quizprep/topics.py -> quiz_app -> repo
REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Topic:
    key: str
    label: str
    brief: str
    notes: tuple[str, ...] = field(default=())

    def notes_paths(self) -> list[Path]:
        return [p for p in (REPO_ROOT / n for n in self.notes) if p.is_file()]

    def load_notes(self, max_chars: int = 40_000) -> str:
        chunks: list[str] = []
        for path in self.notes_paths():
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            chunks.append(f"### Apuntes: {path.name}\n{text}")
        joined = "\n\n".join(chunks)
        return joined[:max_chars]


TOPICS: tuple[Topic, ...] = (
    Topic(
        key="cpp",
        label="C++ moderno (C++11/14/17/20)",
        brief=(
            "C++ moderno: RAII, semántica de movimiento, punteros inteligentes, "
            "plantillas, STL y algoritmos, lambdas, constexpr, concurrencia "
            "(std::thread, atomics, memory model), rendimiento y gestión de memoria."
        ),
        notes=("cpp_moderno.md",),
    ),
    Topic(
        key="python",
        label="Ingeniería de software en Python",
        brief=(
            "Python de nivel ingeniería: modelo de datos, decoradores, generadores, "
            "GIL y concurrencia (threading/multiprocessing/asyncio), typing, "
            "gestión de memoria, empaquetado, testing, numpy y rendimiento."
        ),
    ),
    Topic(
        key="cv",
        label="Computer Vision (teoría y algoritmos)",
        brief=(
            "Visión por computador: formación de imagen, filtrado y convolución, "
            "detección de bordes y esquinas, features (SIFT/ORB), homografías y "
            "geometría epipolar, calibración de cámara, estéreo, tracking, "
            "segmentación y fundamentos de deep learning para visión."
        ),
    ),
    Topic(
        key="opencv",
        label="OpenCV (C++ / Python)",
        brief=(
            "API de OpenCV: cv::Mat y gestión de memoria, tipos y canales, "
            "acceso a píxeles, operaciones aritméticas y ROI, filtros, contornos, "
            "transformaciones geométricas, módulo dnn, VideoCapture y buenas "
            "prácticas de rendimiento."
        ),
        notes=("openCV C++.md",),
    ),
    Topic(
        key="jetson",
        label="NVIDIA Jetson / CUDA / TensorRT",
        brief=(
            "Plataforma Jetson: arquitectura y memoria unificada, JetPack, "
            "modos de energía y nvpmodel/jetson_clocks, CUDA básico, TensorRT "
            "(engines, precisión FP16/INT8, calibración), DeepStream, GStreamer, "
            "cámaras CSI y optimización de pipelines de inferencia embebida."
        ),
        notes=("jetson_ros2_QA.md",),
    ),
    Topic(
        key="ros2",
        label="ROS 2",
        brief=(
            "ROS 2: nodos, topics, services, actions, DDS y QoS, executors y "
            "callback groups, lifecycle nodes, parámetros, tf2, launch files, "
            "composición de nodos y depuración con ros2 CLI."
        ),
        notes=("jetson_ros2_QA.md",),
    ),
    Topic(
        key="ml",
        label="Machine Learning (conceptos y algoritmos)",
        brief=(
            "Conceptos y algoritmos de machine learning: aprendizaje supervisado y "
            "no supervisado, regresión y clasificación, árboles y ensembles, SVM, "
            "k-NN, clustering, reducción de dimensionalidad, sesgo-varianza, "
            "regularización, selección de características, métricas, validación "
            "cruzada, data leakage, optimización y fundamentos de redes neuronales."
        ),
    ),
    Topic(
        key="mixed",
        label="Mixto (entrevista completa)",
        brief=(
            "Mezcla equilibrada de C++ moderno, Python, machine learning, computer "
            "vision, OpenCV, Jetson/TensorRT y ROS 2, como en una entrevista técnica real."
        ),
        notes=("cpp_moderno.md", "openCV C++.md", "jetson_ros2_QA.md"),
    ),
)

TOPICS_BY_KEY = {t.key: t for t in TOPICS}

DIFFICULTIES: tuple[tuple[str, str], ...] = (
    ("junior", "Junior — fundamentos"),
    ("media", "Media — perfil con experiencia"),
    ("senior", "Senior — casos límite y detalles finos"),
    ("experto", "Experto — trampas y comportamiento indefinido"),
)
