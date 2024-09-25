
install:
	python3 -m venv .venv
	. .venv/bin/activate && poetry install

check:
	. .venv/bin/activate && ruff check
	. .venv/bin/activate && mypy python_game_of_life --check-untyped-defs
