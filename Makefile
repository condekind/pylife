
install:
	python3 -m venv .venv
	. .venv/bin/activate && poetry install

check:
	. .venv/bin/activate && ruff check
	. .venv/bin/activate && mypy python-game-of-life --check-untyped-defs
