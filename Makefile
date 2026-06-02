install:
	uv sync

build:
	uv build

package-install:
	uv tool install --force dist/*.whl

test:
	uv run pytest

test-coverage:
	uv run pytest --cov=src --cov=scripts --cov-report xml

lint:
	uv run ruff check

check-content:
	uv run validate-content

check: test lint

tg-run:
	uv run src/presentation/entrypoint_telegram.py

vk-run:
	uv run src/presentation/entrypoint_vk.py

.PHONY: install build package-install test test-coverage lint check-content check tg-run vk-run
