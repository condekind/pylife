
install:
	python3 -m venv .venv
	. .venv/bin/activate && poetry install

check:
	. .venv/bin/activate && ruff check
	. .venv/bin/activate && mypy game_of_life_cli --check-untyped-defs
