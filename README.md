# manferna-austen-trivia

A trivia game about Jane Austen books.

## Usage

### Play Trivia

Run `austen.py` with the `--question` (or `-q`) flag to play trivia questions with score tracking:

```bash
python3 austen.py --question
```

or directly:

```bash
./austen.py -q
```

When prompted, type your answer and press Enter. Answers are evaluated case-insensitively with leading and trailing whitespace trimmed. The game keeps track of correct and incorrect answers, resetting the counters to 0 after 10 questions:

```text
In what year was Pride and Prejudice published?
Your answer: 1813
Correct!
Score: 1 correct, 0 incorrect
```

To exit the session, send EOF (`Ctrl+D`) or interrupt (`Ctrl+C`).

### Survival Mode

Run `austen.py` with the `--survival` (or `-s`) flag to play in survival mode. In this mode, the game finishes when the player answers incorrectly:

```bash
python3 austen.py --survival
```

or directly:

```bash
./austen.py -s
```

### Duel Mode

Run `austen.py` with the `--duel` (or `-d`) flag to play in duel mode:

```bash
python3 austen.py --duel
```

or directly:

```bash
./austen.py -d
```

In this mode, two players take turns answering questions (one question at a time). Each player receives 10 questions for a total of 20 questions in the session. The game tracks correct and incorrect answers for each player independently. After all 20 questions are completed, the session finishes and displays the final scores:

```text
Player 1:
In what year was Pride and Prejudice published?
Your answer: 1813
Correct!
Player 1 Score: 1 correct, 0 incorrect

Player 2:
Who wrote Sense and Sensibility?
Your answer: Jane Austen
Correct!
Player 2 Score: 1 correct, 0 incorrect
```

### Help

To view available command-line options:

```bash
python3 austen.py --help
```

## Testing

Run unit and integration tests using Python's standard `unittest` module:

```bash
python3 -m unittest discover
```

