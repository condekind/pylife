
install:
	python3 -m venv .venv
	source .venv/bin/activate && poetry install

check:
	source .venv/bin/activate && ruff check
	source .venv/bin/activate && mypy pylife --check-untyped-defs
