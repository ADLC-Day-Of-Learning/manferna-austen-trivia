import json
import unittest
from pathlib import Path

try:
    import jsonschema
except ImportError:
    jsonschema = None

QUESTIONS_FILE = Path(__file__).resolve().parent / "questions.json"
SCHEMA_FILE = Path(__file__).resolve().parent / "questions.schema.json"


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
        required_fields = ["question", "answer", "category", "subcategory"]
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
                if field != "subcategory":
                    self.assertTrue(
                        len(item[field].strip()) > 0,
                        f"Field '{field}' in item {index} cannot be empty",
                    )

    def test_questions_subcategory_schema(self):
        """Verify subcategory field presence and value rules across questions."""
        for index, item in enumerate(self.questions):
            self.assertIn(
                "subcategory",
                item,
                f"Item at index {index} missing 'subcategory' field",
            )
            self.assertIsInstance(
                item["subcategory"],
                str,
                f"Field 'subcategory' in item {index} must be a string",
            )
            if item.get("category") == "Pride and Prejudice":
                self.assertEqual(
                    item.get("subcategory"),
                    "Characters",
                    f"Expected subcategory 'Characters' for Pride and Prejudice at index {index}",
                )
            elif item.get("category") == "Jane Austen":
                self.assertEqual(
                    item.get("subcategory"),
                    "facts",
                    f"Expected subcategory 'facts' for Jane Austen at index {index}",
                )
            else:
                self.assertEqual(
                    item.get("subcategory"),
                    "",
                    f"Expected empty subcategory for category '{item.get('category')}' at index {index}",
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
        category = "Pride and Prejudice"
        subcategory = "Characters"
        character_questions = [
            q
            for q in self.questions
            if q.get("category") == category and q.get("subcategory") == subcategory
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
            self.assertEqual(item.get("subcategory"), subcategory)

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

    def test_jane_austen_adult_life_questions(self):
        """Verify presence and schema of 10 questions on Jane Austen adult life."""
        category = "Jane Austen"
        subcategory = "facts"
        austen_facts = [
            q
            for q in self.questions
            if q.get("category") == category
            and q.get("subcategory") == subcategory
        ]

        self.assertGreaterEqual(
            len(austen_facts),
            10,
            f"Expected at least 10 questions, found {len(austen_facts)}",
        )
        for item in austen_facts:
            self.assertIsInstance(item.get("question"), str)
            self.assertTrue(len(item["question"].strip()) > 0)
            self.assertIsInstance(item.get("answer"), str)
            self.assertTrue(len(item["answer"].strip()) > 0)
            self.assertEqual(item.get("category"), category)
            self.assertEqual(item.get("subcategory"), subcategory)


class TestQuestionsSchemaFile(unittest.TestCase):
    """Test suite for questions JSON schema specification."""

    def setUp(self):
        self.schema_file = SCHEMA_FILE
        self.assertTrue(
            self.schema_file.is_file(), "questions.schema.json must exist"
        )
        with open(self.schema_file, "r", encoding="utf-8") as f:
            self.schema = json.load(f)

    def test_schema_file_exists_and_defines_taxonomy(self):
        """Verify that questions.schema.json exists and specifies required fields and categories."""
        schema_path = Path("questions.schema.json")
        if not schema_path.is_file():
            schema_path = self.schema_file
        self.assertTrue(
            schema_path.is_file(), "questions.schema.json must exist"
        )

        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)

        item_props = schema.get("items", {}).get(
            "properties", schema.get("properties", {})
        )
        for expected_prop in ("question", "answer", "category", "subcategory"):
            self.assertIn(expected_prop, item_props)

    def test_schema_is_valid_json_schema(self):
        """Verify that the schema conforms to the JSON Schema Draft 7 meta-schema."""
        if jsonschema is None:
            self.skipTest("jsonschema package not available")
        jsonschema.Draft7Validator.check_schema(self.schema)
        self.assertEqual(self.schema.get("type"), "array")
        self.assertIn("$schema", self.schema)
        self.assertGreaterEqual(self.schema.get("minItems", 0), 18)

    def test_schema_specifies_categories(self):
        """Verify schema specifies category count and category names."""
        category_prop = (
            self.schema.get("items", {}).get("properties", {}).get("category", {})
        )
        expected_categories = [
            "Publication Year",
            "Adaptations",
            "Pride and Prejudice",
        ]
        self.assertIn("enum", category_prop)
        self.assertEqual(len(category_prop["enum"]), 3)
        self.assertEqual(set(category_prop["enum"]), set(expected_categories))

        metadata_cats = (
            self.schema.get("metadata", {}).get("categories", {})
        )
        self.assertEqual(metadata_cats.get("count"), 3)
        self.assertEqual(
            set(metadata_cats.get("names", [])), set(expected_categories)
        )

    def test_schema_specifies_subcategories(self):
        """Verify schema specifies subcategories count and names."""
        subcat_prop = (
            self.schema.get("items", {})
            .get("properties", {})
            .get("subcategory", {})
        )
        self.assertIn("enum", subcat_prop)
        self.assertIn("Characters", subcat_prop["enum"])
        self.assertIn("", subcat_prop["enum"])

        metadata_subcats = (
            self.schema.get("metadata", {}).get("subcategories", {})
        )
        self.assertEqual(metadata_subcats.get("count"), 1)
        self.assertIn("Characters", metadata_subcats.get("names", []))

    def test_schema_specifies_question_counts(self):
        """Verify schema specifies total and per-category question counts."""
        metadata = self.schema.get("metadata", {})
        self.assertEqual(metadata.get("totalQuestions"), 18)

        breakdown = {
            item["name"]: item["questionCount"]
            for item in metadata.get("categories", {}).get("breakdown", [])
        }
        self.assertEqual(breakdown.get("Publication Year"), 6)
        self.assertEqual(breakdown.get("Adaptations"), 5)
        self.assertEqual(breakdown.get("Pride and Prejudice"), 7)

    def _create_valid_dataset(self):
        """Generate a valid 18-question dataset matching the taxonomy specification."""
        dataset = []
        for i in range(6):
            dataset.append(
                {
                    "question": f"Publication question {i + 1}?",
                    "answer": f"Answer {i + 1}",
                    "category": "Publication Year",
                    "subcategory": "",
                }
            )
        for i in range(5):
            dataset.append(
                {
                    "question": f"Adaptation question {i + 1}?",
                    "answer": f"Answer {i + 1}",
                    "category": "Adaptations",
                    "subcategory": "",
                }
            )
        for i in range(7):
            dataset.append(
                {
                    "question": f"Character question {i + 1}?",
                    "answer": f"Character {i + 1}",
                    "category": "Pride and Prejudice",
                    "subcategory": "Characters",
                }
            )
        return dataset

    def test_schema_validates_sample_questions(self):
        """Verify schema items definition validates individual question objects."""
        if jsonschema is None:
            self.skipTest("jsonschema package not available")

        sample_data = [
            {
                "question": "In what year was Sense and Sensibility published?",
                "answer": "1811",
                "category": "Publication Year",
                "subcategory": "",
            },
            {
                "question": "Who played Mr. Darcy in the 1995 BBC television adaptation?",
                "answer": "Colin Firth",
                "category": "Adaptations",
                "subcategory": "",
            },
            {
                "question": "Who is the protagonist of Pride and Prejudice?",
                "answer": "Elizabeth Bennet",
                "category": "Pride and Prejudice",
                "subcategory": "Characters",
            },
        ]
        validator = jsonschema.Draft7Validator(self.schema["items"])
        for sample in sample_data:
            errors = list(validator.iter_errors(sample))
            self.assertEqual(len(errors), 0, f"Validation errors: {errors}")

    def test_schema_validates_full_dataset(self):
        """Verify schema directly validates a full 18-question dataset without overriding minItems."""
        if jsonschema is None:
            self.skipTest("jsonschema package not available")

        full_dataset = self._create_valid_dataset()
        validator = jsonschema.Draft7Validator(self.schema)
        errors = list(validator.iter_errors(full_dataset))
        self.assertEqual(
            len(errors), 0, f"Validation errors on full dataset: {errors}"
        )

    def test_schema_rejects_fewer_than_min_items(self):
        """Verify schema rejects datasets with fewer than minItems (18) questions."""
        if jsonschema is None:
            self.skipTest("jsonschema package not available")

        validator = jsonschema.Draft7Validator(self.schema)
        dataset_too_short = self._create_valid_dataset()[:17]
        errors = list(validator.iter_errors(dataset_too_short))
        self.assertGreater(
            len(errors), 0, "Schema must reject datasets with fewer than 18 items"
        )

    def test_schema_rejects_missing_required_properties(self):
        """Verify schema rejects question objects missing required properties."""
        if jsonschema is None:
            self.skipTest("jsonschema package not available")

        item_validator = jsonschema.Draft7Validator(self.schema["items"])
        for required_prop in ("question", "answer", "category", "subcategory"):
            invalid_item = {
                "question": "In what year was Sense and Sensibility published?",
                "answer": "1811",
                "category": "Publication Year",
                "subcategory": "",
            }
            del invalid_item[required_prop]
            errors = list(item_validator.iter_errors(invalid_item))
            self.assertGreater(
                len(errors),
                0,
                f"Schema must reject item missing required property '{required_prop}'",
            )

    def test_schema_rejects_unknown_categories(self):
        """Verify schema rejects question objects with unknown categories."""
        if jsonschema is None:
            self.skipTest("jsonschema package not available")

        item_validator = jsonschema.Draft7Validator(self.schema["items"])
        invalid_item = {
            "question": "In what year was Sense and Sensibility published?",
            "answer": "1811",
            "category": "Unknown Category",
            "subcategory": "",
        }
        errors = list(item_validator.iter_errors(invalid_item))
        self.assertGreater(
            len(errors), 0, "Schema must reject unknown category"
        )

    def test_schema_rejects_category_subcategory_mismatches(self):
        """Verify schema rejects category-subcategory mismatches."""
        if jsonschema is None:
            self.skipTest("jsonschema package not available")

        item_validator = jsonschema.Draft7Validator(self.schema["items"])
        pnp_mismatch = {
            "question": "Who is the protagonist of Pride and Prejudice?",
            "answer": "Elizabeth Bennet",
            "category": "Pride and Prejudice",
            "subcategory": "",
        }
        errors = list(item_validator.iter_errors(pnp_mismatch))
        self.assertGreater(
            len(errors),
            0,
            "Schema must reject Pride and Prejudice with empty subcategory",
        )

        adaptations_mismatch = {
            "question": "Who played Mr. Darcy in the 1995 BBC television adaptation?",
            "answer": "Colin Firth",
            "category": "Adaptations",
            "subcategory": "Characters",
        }
        errors = list(item_validator.iter_errors(adaptations_mismatch))
        self.assertGreater(
            len(errors),
            0,
            "Schema must reject Adaptations with Characters subcategory",
        )

        pub_year_mismatch = {
            "question": "In what year was Sense and Sensibility published?",
            "answer": "1811",
            "category": "Publication Year",
            "subcategory": "Characters",
        }
        errors = list(item_validator.iter_errors(pub_year_mismatch))
        self.assertGreater(
            len(errors),
            0,
            "Schema must reject Publication Year with Characters subcategory",
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
        assert isinstance(q.get("subcategory"), str)
        if q.get("category") == "Pride and Prejudice":
            assert q.get("subcategory") == "Characters"
        elif q.get("category") == "Jane Austen":
            assert q.get("subcategory") == "facts"
        else:
            assert q.get("subcategory") == ""


if __name__ == "__main__":
    unittest.main()
