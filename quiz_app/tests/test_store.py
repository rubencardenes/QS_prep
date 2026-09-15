import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from quizprep import store
from quizprep.models import Option, Question, Quiz
from quizprep.widgets import md_to_html


class StoreTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        root = Path(self.folder.name)
        self.patches = [
            patch.object(store, "APP_DIR", root),
            patch.object(store, "DB_FILE", root / "history.db"),
            patch.object(store, "LEGACY_HISTORY_FILE", root / "history.json"),
        ]
        for item in self.patches:
            item.start()

    def tearDown(self):
        for item in reversed(self.patches):
            item.stop()
        self.folder.cleanup()

    def test_imports_saved_revisions_and_filters(self):
        rows = store.results()
        revision_count = len(list(store.REVISIONS_DIR.glob("revision_test_*.md")))
        self.assertEqual(len(rows), revision_count)
        self.assertGreater(sum(row["question_count"] for row in rows), 0)
        self.assertEqual(len(store.results(topic_key="cv")), 6)
        # Volver a inicializar no duplica las importaciones.
        store.initialize()
        self.assertEqual(len(store.results()), revision_count)

    def test_migrates_json_and_records_full_result(self):
        store.LEGACY_HISTORY_FILE.write_text(json.dumps({
            "asked": {"python": ["Pregunta antigua"]},
            "results": [{"when": "2025-01-01T10:00:00", "topic_key": "python",
                         "topic": "Python", "difficulty": "junior", "total": 5,
                         "correct": 3, "percentage": 60}],
        }))
        self.assertEqual(store.asked_questions("python"), ["Pregunta antigua"])
        quiz = Quiz("Machine Learning (conceptos y algoritmos)", "media", [
            Question("¿Qué es overfitting?", [Option("Sobreajuste", True)], selected={0})
        ])
        store.record_result("ml", quiz, elapsed=42, language="es", model="test")
        row = store.results(topic_key="ml")[0]
        self.assertEqual(row["question_count"], 1)
        self.assertEqual(row["elapsed_seconds"], 42)
        self.assertIn("overfitting", row["review_markdown"])

    def test_renders_latex_delimiters_and_common_symbols(self):
        rendered = md_to_html(r"La pérdida es \(L = \frac{1}{n}\sum_i x_i^2\).")
        self.assertNotIn(r"\(", rendered)
        self.assertNotIn(r"\frac", rendered)
        self.assertIn("∑", rendered)
        self.assertIn("<sup>2</sup>", rendered)


if __name__ == "__main__":
    unittest.main()
