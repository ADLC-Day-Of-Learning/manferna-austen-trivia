# Agent Guidelines

## Testing
- CLI & logic tests: `python3 -m unittest test_austen.py`
- Question schema & category tests: `python3 -m unittest test_questions.py`
- Note: `python3 -m unittest discover` runs both suites; ensure `test_questions.py` failures are not confused with CLI regressions.

## Tooling & Linters
- Python standard library only (Python 3.10+).
- No external linters or formatters (`ruff`, `flake8`, `black`, `pre-commit`) are configured.
- Secret scanning (`scan-secrets`) runs in agent environments before commit.

## Commit Conventions
- Use Conventional Commits with issue references:
  - `fix(#<issue>): <imperative summary>`
  - `feat(#<issue>): <imperative summary>`
