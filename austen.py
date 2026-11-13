#!/usr/bin/env python3
"""Jane Austen Trivia CLI."""

import argparse
import json
import random
import sys
from pathlib import Path

QUESTIONS_FILE = Path(__file__).resolve().parent / "questions.json"


def load_questions(filepath=None):
    """Load trivia questions from a JSON file."""
    if filepath is None:
        filepath = QUESTIONS_FILE
    path = Path(filepath)
    if not path.is_file():
        raise FileNotFoundError(f"Questions file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list) or not data:
        raise ValueError("Questions file must contain a non-empty list of questions")

    return data


def check_answer(user_answer: str, expected_answer: str) -> bool:
    """Validate whether the user's answer matches the expected answer."""
    return user_answer.strip().lower() == expected_answer.strip().lower()


class ScoreTracker:
    """Tracks correct and incorrect question counts, resetting after max_questions."""

    def __init__(self, max_questions: int = 10):
        self.max_questions = max_questions
        self.correct = 0
        self.incorrect = 0

    @property
    def total(self) -> int:
        """Total questions answered in the current round."""
        return self.correct + self.incorrect

    def reset(self):
        """Reset counters to zero."""
        self.correct = 0
        self.incorrect = 0

    def record_answer(self, is_correct: bool) -> bool:
        """Record an answer and return True when reaching max_questions."""
        if is_correct:
            self.correct += 1
        else:
            self.incorrect += 1

        return self.total >= self.max_questions


def play_question(
    question_item: dict, tracker: ScoreTracker | None = None
) -> bool | None:
    """Ask a question, read the player's answer, and output correct or incorrect."""
    print(question_item["question"])
    try:
        user_answer = input("Your answer: ")
    except (EOFError, KeyboardInterrupt):
        print("\nExiting.")
        return None

    if check_answer(user_answer, question_item["answer"]):
        print("Correct!")
        is_correct = True
    else:
        print(f"Incorrect. The answer is {question_item['answer']}.")
        is_correct = False

    if tracker is not None:
        reset = tracker.record_answer(is_correct)
        print(f"Score: {tracker.correct} correct, {tracker.incorrect} incorrect")
        if reset:
            print(f"Counters reset to 0 after {tracker.max_questions} questions.")
            tracker.reset()

    return is_correct


def build_parser():
    """Build the argument parser for CLI commands."""
    parser = argparse.ArgumentParser(description="Jane Austen Trivia CLI")
    parser.add_argument(
        "-q",
        "--question",
        action="store_true",
        help="Retrieve and play trivia questions with score tracking",
    )
    return parser


def parse_args(args=None):
    """Parse command line arguments."""
    return build_parser().parse_args(args)


def main(args=None):
    """Entrypoint for the CLI game."""
    parsed_args = parse_args(args)

    if not parsed_args.question:
        build_parser().print_help()
        return 0

    try:
        questions = load_questions()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    tracker = ScoreTracker()
    first = True
    while True:
        if not first:
            print()
        first = False
        question = random.choice(questions)
        result = play_question(question, tracker=tracker)
        if result is None:
            break

    return 0


if __name__ == "__main__":
    sys.exit(main())
