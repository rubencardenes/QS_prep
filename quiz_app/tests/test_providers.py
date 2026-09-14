import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from quizprep.llm import CodexCLI, ClaudeCLI, LLMError, CancelledError, _communicate
from quizprep.settings import load_settings


class ProvidersTest(unittest.TestCase):
    def test_settings(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'settings.yaml'
            self.assertEqual(load_settings(path).model, 'gpt-5.6-sol')
            path.write_text('provider: claude\nclaude:\n  model: opus\n')
            settings = load_settings(path)
            self.assertEqual(settings.planning_model, 'haiku')
            with patch('quizprep.llm.shutil.which', return_value='/bin/claude'):
                self.assertIsInstance(settings.client(), ClaudeCLI)
                self.assertEqual(settings.client().model, 'opus')
            for invalid in ('[]', 'provider: other', 'timeout: false', 'chatgpt: []', 'chatgpt:\n  model: null', '['):
                path.write_text(invalid)
                with self.subTest(invalid=invalid), self.assertRaises(LLMError):
                    load_settings(path)

    @patch('quizprep.llm.shutil.which', return_value='/bin/codex')
    def test_codex_final_message_and_auth(self, _which):
        def launch(command, **kwargs):
            self.assertEqual(command[1], 'exec')
            self.assertIn('forced_login_method="chatgpt"', command)
            self.assertNotIn('OPENAI_API_KEY', kwargs['env'])
            self.assertNotIn('CODEX_API_KEY', kwargs['env'])
            Path(command[command.index('--output-last-message') + 1]).write_text('{"questions": []}')
            class Process:
                returncode = 0
                def communicate(self, input=None, timeout=None):
                    self.request = input
                    return 'irrelevant log', ''
            return Process()
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test', 'CODEX_API_KEY': 'test'}), patch('quizprep.llm.subprocess.Popen', side_effect=launch):
            self.assertEqual(CodexCLI().complete('system', 'prompt'), '{"questions": []}')

    def test_generation_uses_selected_planner(self):
        from unittest.mock import Mock
        from quizprep.generator import generate_quiz
        from quizprep.topics import TOPICS_BY_KEY
        planner = Mock()
        planner.complete.return_value = json.dumps({"subtopics": ["a", "b", "c", "d"]})
        client = Mock()
        client.complete.side_effect = [json.dumps({"questions": [
            {"question": f"Question {i}", "options": [
                {"text": "yes", "correct": True},
                {"text": "no", "correct": False},
            ]} for i in indices
        ]}) for indices in ([1, 2], [3, 4])]
        quiz = generate_quiz(client, next(iter(TOPICS_BY_KEY)), "media", 4,
                             planning_client=planner)
        self.assertEqual(quiz.total, 4)
        planner.complete.assert_called_once()
        self.assertEqual(client.complete.call_count, 2)

    def test_stdin_survives_polling(self):
        proc = subprocess.Popen(['python3', '-c', 'import sys,time; s=sys.stdin.read(); time.sleep(.35); print(s)'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.assertEqual(_communicate(proc, 3, None, 'hello')[0].strip(), 'hello')

    def test_cancel_and_timeout(self):
        from unittest.mock import Mock
        proc = Mock()
        proc.communicate.side_effect = subprocess.TimeoutExpired('codex', .25)
        with self.assertRaises(CancelledError):
            _communicate(proc, 1, lambda: True)
        with self.assertRaises(TimeoutError):
            _communicate(proc, 1, None)

    @patch('quizprep.llm.shutil.which', return_value=None)
    def test_missing_binary(self, _which):
        with self.assertRaises(LLMError):
            CodexCLI()


if __name__ == '__main__':
    unittest.main()
