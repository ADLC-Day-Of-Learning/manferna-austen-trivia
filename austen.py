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


def play_question(question_item: dict) -> bool:
    """Ask a question, read the player's answer, and output correct or incorrect."""
    print(question_item["question"])
    try:
        user_answer = input("Your answer: ")
    except (EOFError, KeyboardInterrupt):
        print("\nExiting.")
        return False

    if check_answer(user_answer, question_item["answer"]):
        print("Correct!")
        return True
    else:
        print(f"Incorrect. The answer is {question_item['answer']}.")
        return False


def build_parser():
    """Build the argument parser for CLI commands."""
    parser = argparse.ArgumentParser(description="Jane Austen Trivia CLI")
    parser.add_argument(
        "-q",
        "--question",
        action="store_true",
        help="Retrieve and ask a trivia question",
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

    question = random.choice(questions)
    play_question(question)
    return 0


if __name__ == "__main__":
    sys.exit(main())
