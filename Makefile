.PHONY: install test lint format clean

install:
	pip install -e ".[dev]"

test:
	pytest

lint:
	ruff check src/ tests/

format:
	ruff format src/ tests/

check-format:
	ruff format --check src/ tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
