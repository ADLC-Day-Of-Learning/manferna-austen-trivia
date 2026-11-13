import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import austen


class TestAustenFunctions(unittest.TestCase):
    """Unit tests for individual functions in austen.py."""

    def test_load_questions_default(self):
        questions = austen.load_questions()
        self.assertIsInstance(questions, list)
        self.assertGreaterEqual(len(questions), 1)
        self.assertIn("question", questions[0])
        self.assertIn("answer", questions[0])

    def test_load_questions_nonexistent_file(self):
        with self.assertRaises(FileNotFoundError):
            austen.load_questions("nonexistent_questions_file.json")

    def test_load_questions_invalid_json_format(self):
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as f:
            f.write(json.dumps({"not": "a list"}))
            temp_path = f.name
        try:
            with self.assertRaises(ValueError):
                austen.load_questions(temp_path)
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_load_questions_empty_list(self):
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as f:
            f.write(json.dumps([]))
            temp_path = f.name
        try:
            with self.assertRaises(ValueError):
                austen.load_questions(temp_path)
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_check_answer_exact_match(self):
        self.assertTrue(austen.check_answer("1813", "1813"))

    def test_check_answer_case_insensitive(self):
        self.assertTrue(
            austen.check_answer("pride and prejudice", "Pride and Prejudice")
        )

    def test_check_answer_whitespace_trimmed(self):
        self.assertTrue(austen.check_answer("  1813 \n", "1813"))

    def test_check_answer_incorrect(self):
        self.assertFalse(austen.check_answer("1811", "1813"))

    @patch("builtins.input", return_value="1813")
    def test_play_question_correct(self, mock_input):
        question_item = {
            "question": "In what year was Pride and Prejudice published?",
            "answer": "1813",
            "category": "Publication Year",
            "subcategory": "",
        }
        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            result = austen.play_question(question_item)
            output = mock_stdout.getvalue()
        self.assertTrue(result)
        self.assertIn("Correct!", output)
        self.assertNotIn("Incorrect", output)

    @patch("builtins.input", return_value="1820")
    def test_play_question_incorrect(self, mock_input):
        question_item = {
            "question": "In what year was Pride and Prejudice published?",
            "answer": "1813",
            "category": "Publication Year",
            "subcategory": "",
        }
        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            result = austen.play_question(question_item)
            output = mock_stdout.getvalue()
        self.assertFalse(result)
        self.assertIn("Incorrect", output)
        self.assertIn("1813", output)

    @patch("builtins.input", side_effect=EOFError)
    def test_play_question_eof(self, mock_input):
        question_item = {
            "question": "In what year was Pride and Prejudice published?",
            "answer": "1813",
            "category": "Publication Year",
            "subcategory": "",
        }
        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            result = austen.play_question(question_item)
            output = mock_stdout.getvalue()
        self.assertFalse(result)
        self.assertIn("Exiting", output)

    def test_parse_args_with_question_flag(self):
        args = austen.parse_args(["--question"])
        self.assertTrue(args.question)

        args_short = austen.parse_args(["-q"])
        self.assertTrue(args_short.question)

    def test_parse_args_without_question_flag(self):
        args = austen.parse_args([])
        self.assertFalse(args.question)

    def test_main_without_args_prints_help(self):
        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            exit_code = austen.main([])
            output = mock_stdout.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn("Jane Austen Trivia CLI", output)
        self.assertIn("--question", output)

    @patch("austen.load_questions", side_effect=FileNotFoundError("missing file"))
    def test_main_error_loading_questions(self, mock_load):
        with patch("sys.stderr", new_callable=io.StringIO) as mock_stderr:
            exit_code = austen.main(["--question"])
            err_output = mock_stderr.getvalue()
        self.assertEqual(exit_code, 1)
        self.assertIn("Error:", err_output)


class TestAustenCLI(unittest.TestCase):
    """End-to-end and subprocess CLI tests."""

    def test_cli_question_triage_case(self):
        """Triage test case: run with --question and provide stdin answer."""
        repo_root = Path(__file__).resolve().parent
        script_path = repo_root / "austen.py"

        result = subprocess.run(
            [sys.executable, str(script_path), "--question"],
            input="1813\n",
            capture_output=True,
            text=True,
            timeout=5,
            cwd=str(repo_root),
        )
        self.assertEqual(result.returncode, 0)
        output = result.stdout.lower()
        self.assertTrue(
            "correct" in output or "incorrect" in output,
            f"Expected 'correct' or 'incorrect' in output: {result.stdout}",
        )

    def test_cli_executable_direct(self):
        """Verify austen.py can be invoked directly as a script."""
        repo_root = Path(__file__).resolve().parent
        script_path = repo_root / "austen.py"

        result = subprocess.run(
            [str(script_path), "--question"],
            input="nonsense\n",
            capture_output=True,
            text=True,
            timeout=5,
            cwd=str(repo_root),
        )
        self.assertEqual(result.returncode, 0)
        output = result.stdout.lower()
        self.assertTrue(
            "correct" in output or "incorrect" in output,
            f"Expected 'correct' or 'incorrect' in output: {result.stdout}",
        )

    def test_cli_help_flag(self):
        """Verify --help flag displays usage."""
        repo_root = Path(__file__).resolve().parent
        script_path = repo_root / "austen.py"

        result = subprocess.run(
            [sys.executable, str(script_path), "--help"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=str(repo_root),
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("--question", result.stdout)


if __name__ == "__main__":
    unittest.main()
