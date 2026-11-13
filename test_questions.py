import json
import unittest
from pathlib import Path

QUESTIONS_FILE = Path(__file__).resolve().parent / "questions.json"


class TestQuestionsData(unittest.TestCase):
    """Test suite for trivia questions data."""

    def setUp(self):
        self.assertTrue(QUESTIONS_FILE.is_file(), "questions.json must exist")
        with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
            self.questions = json.load(f)

    def test_questions_is_list(self):
        self.assertIsInstance(self.questions, list)
        self.assertGreaterEqual(len(self.questions), 6)

    def test_questions_schema(self):
        required_fields = ["question", "answer", "category"]
        for index, item in enumerate(self.questions):
            self.assertIsInstance(
                item, dict, f"Item at index {index} should be a dictionary"
            )
            for field in required_fields:
                self.assertIn(
                    field,
                    item,
                    f"Item at index {index} missing required field '{field}'",
                )
                self.assertIsInstance(
                    item[field],
                    str,
                    f"Field '{field}' in item {index} must be a string",
                )
                self.assertTrue(
                    len(item[field].strip()) > 0,
                    f"Field '{field}' in item {index} cannot be empty",
                )

    def test_novels_publication_years_covered(self):
        expected_novels = [
            "Sense and Sensibility",
            "Pride and Prejudice",
            "Mansfield Park",
            "Emma",
            "Northanger Abbey",
            "Persuasion",
        ]
        all_questions_text = " ".join(q["question"] for q in self.questions)
        for novel in expected_novels:
            self.assertIn(
                novel,
                all_questions_text,
                f"Expected novel '{novel}' to be mentioned in questions",
            )

    def test_adaptations_category_questions(self):
        category = "Adaptations"
        adaptation_questions = [
            q for q in self.questions if q.get("category") == category
        ]
        self.assertGreaterEqual(
            len(adaptation_questions),
            5,
            f"Expected at least 5 questions in category '{category}'",
        )
        for item in adaptation_questions:
            self.assertIsInstance(item.get("question"), str)
            self.assertTrue(len(item["question"].strip()) > 0)
            self.assertIsInstance(item.get("answer"), str)
            self.assertTrue(len(item["answer"].strip()) > 0)
            self.assertEqual(item.get("category"), category)

    def test_pride_and_prejudice_characters_category(self):
        category = "Characters from Pride and Prejudice"
        character_questions = [
            q for q in self.questions if q.get("category") == category
        ]
        self.assertEqual(
            len(character_questions),
            7,
            f"Expected 7 questions in category '{category}'",
        )
        self.assertGreaterEqual(
            len(character_questions),
            3,
            f"Expected at least 3 questions in category '{category}'",
        )
        for item in character_questions:
            self.assertIsInstance(item.get("question"), str)
            self.assertTrue(len(item["question"].strip()) > 0)
            self.assertIsInstance(item.get("answer"), str)
            self.assertTrue(len(item["answer"].strip()) > 0)
            self.assertEqual(item.get("category"), category)

        expected_characters = [
            "Elizabeth Bennet",
            "Fitzwilliam Darcy",
            "Jane Bennet",
            "Charles Bingley",
            "Mr. Collins",
            "George Wickham",
            "Lady Catherine de Bourgh",
        ]
        all_answers = [q["answer"] for q in character_questions]
        for character in expected_characters:
            self.assertIn(
                character,
                all_answers,
                f"Expected character '{character}' to be an answer in category '{category}'",
            )


def test_questions_data():
    """Triage proposed test case compatibility function."""
    path = Path("questions.json")
    if not path.is_file():
        path = QUESTIONS_FILE
    assert path.is_file(), "questions.json must exist"
    with open(path, "r", encoding="utf-8") as f:
        questions = json.load(f)
    assert isinstance(questions, list) and len(questions) >= 6
    for q in questions:
        assert isinstance(q.get("question"), str) and len(q["question"]) > 0
        assert str(q.get("answer", "")).strip() != ""
        assert isinstance(q.get("category"), str) and len(q["category"]) > 0


if __name__ == "__main__":
    unittest.main()
