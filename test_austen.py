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


class TestScoreTracking(unittest.TestCase):
    """Unit tests for ScoreTracker and score tracking integration."""

    def test_score_tracker_initial_state(self):
        tracker = austen.ScoreTracker()
        self.assertEqual(tracker.correct, 0)
        self.assertEqual(tracker.incorrect, 0)
        self.assertEqual(tracker.total, 0)

    def test_counters_increment_and_reset_at_ten(self):
        tracker = austen.ScoreTracker()
        self.assertEqual((tracker.correct, tracker.incorrect), (0, 0))

        # Record 6 correct and 3 incorrect answers
        for _ in range(6):
            tracker.record_answer(is_correct=True)
        for _ in range(3):
            tracker.record_answer(is_correct=False)

        self.assertEqual(tracker.correct, 6)
        self.assertEqual(tracker.incorrect, 3)
        self.assertEqual(tracker.total, 9)

        # 10th answer completes the set and triggers reset condition
        reset_triggered = tracker.record_answer(is_correct=True)
        self.assertTrue(reset_triggered)
        self.assertEqual(tracker.correct, 7)
        self.assertEqual(tracker.incorrect, 3)
        self.assertEqual(tracker.total, 10)
        tracker.reset()
        self.assertEqual(tracker.correct, 0)
        self.assertEqual(tracker.incorrect, 0)
        self.assertEqual(tracker.total, 0)

    def test_counters_reset_on_tenth_incorrect_answer(self):
        tracker = austen.ScoreTracker()
        for _ in range(9):
            tracker.record_answer(is_correct=True)
        self.assertEqual(tracker.correct, 9)
        self.assertEqual(tracker.incorrect, 0)

        reset_triggered = tracker.record_answer(is_correct=False)
        self.assertTrue(reset_triggered)
        self.assertEqual(tracker.correct, 9)
        self.assertEqual(tracker.incorrect, 1)
        tracker.reset()
        self.assertEqual(tracker.correct, 0)
        self.assertEqual(tracker.incorrect, 0)

    def test_score_tracker_manual_reset(self):
        tracker = austen.ScoreTracker()
        tracker.record_answer(True)
        tracker.record_answer(False)
        tracker.reset()
        self.assertEqual(tracker.correct, 0)
        self.assertEqual(tracker.incorrect, 0)

    def test_score_tracker_custom_max_questions(self):
        tracker = austen.ScoreTracker(max_questions=3)
        tracker.record_answer(True)
        tracker.record_answer(False)
        reset = tracker.record_answer(True)
        self.assertTrue(reset)
        self.assertEqual(tracker.correct, 2)
        self.assertEqual(tracker.incorrect, 1)
        tracker.reset()
        self.assertEqual(tracker.correct, 0)
        self.assertEqual(tracker.incorrect, 0)

    def test_play_question_with_tracker_records_answers(self):
        tracker = austen.ScoreTracker()
        question_item = {
            "question": "In what year was Pride and Prejudice published?",
            "answer": "1813",
            "category": "Publication Year",
        }
        with patch("builtins.input", return_value="1813"):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                res = austen.play_question(question_item, tracker=tracker)
                output = mock_stdout.getvalue()
        self.assertTrue(res)
        self.assertEqual(tracker.correct, 1)
        self.assertEqual(tracker.incorrect, 0)
        self.assertIn("Score: 1 correct, 0 incorrect", output)

        with patch("builtins.input", return_value="1820"):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                res = austen.play_question(question_item, tracker=tracker)
                output = mock_stdout.getvalue()
        self.assertFalse(res)
        self.assertEqual(tracker.correct, 1)
        self.assertEqual(tracker.incorrect, 1)
        self.assertIn("Score: 1 correct, 1 incorrect", output)

    def test_play_question_with_tracker_reset_message(self):
        tracker = austen.ScoreTracker()
        for _ in range(9):
            tracker.record_answer(True)
        question_item = {
            "question": "In what year was Pride and Prejudice published?",
            "answer": "1813",
            "category": "Publication Year",
        }
        with patch("builtins.input", return_value="1813"):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                res = austen.play_question(question_item, tracker=tracker)
                output = mock_stdout.getvalue()
        self.assertTrue(res)
        self.assertEqual(tracker.correct, 0)
        self.assertEqual(tracker.incorrect, 0)
        self.assertIn("Score: 10 correct, 0 incorrect", output)
        self.assertIn("Counters reset to 0 after 10 questions.", output)

    def test_play_question_with_custom_max_questions(self):
        tracker = austen.ScoreTracker(max_questions=3)
        tracker.record_answer(True)
        tracker.record_answer(False)
        question_item = {
            "question": "In what year was Pride and Prejudice published?",
            "answer": "1813",
            "category": "Publication Year",
        }
        with patch("builtins.input", return_value="1813"):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                res = austen.play_question(question_item, tracker=tracker)
                output = mock_stdout.getvalue()
        self.assertTrue(res)
        self.assertEqual(tracker.correct, 0)
        self.assertEqual(tracker.incorrect, 0)
        self.assertIn("Score: 2 correct, 1 incorrect", output)
        self.assertIn("Counters reset to 0 after 3 questions.", output)


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

    def test_cli_multi_question_session_with_scoring(self):
        """Verify CLI tracks scores across consecutive questions and exits cleanly on EOF."""
        repo_root = Path(__file__).resolve().parent
        script_path = repo_root / "austen.py"

        # Provide two answers followed by EOF
        result = subprocess.run(
            [sys.executable, str(script_path), "--question"],
            input="1813\nwronganswer\n",
            capture_output=True,
            text=True,
            timeout=5,
            cwd=str(repo_root),
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("Score:", result.stdout)
        self.assertIn("Exiting", result.stdout)


if __name__ == "__main__":
    unittest.main()
