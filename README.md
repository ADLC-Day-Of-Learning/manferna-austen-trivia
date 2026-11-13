# manferna-austen-trivia

A trivia game about Jane Austen books.

## Usage

### Play Trivia

Run `austen.py` with the `--question` (or `-q`) flag to retrieve and answer a random trivia question:

```bash
python3 austen.py --question
```

or directly:

```bash
./austen.py -q
```

When prompted, type your answer and press Enter. Answers are evaluated case-insensitively with leading and trailing whitespace trimmed:

```text
In what year was Pride and Prejudice published?
Your answer: 1813
Correct!
```

To exit prematurely, send EOF (`Ctrl+D`) or interrupt (`Ctrl+C`).

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

