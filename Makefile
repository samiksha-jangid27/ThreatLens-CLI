.PHONY: install test lint format compile check benchmark build demo docker-build docker-help

install:
	python -m pip install ".[dev]"

test:
	python -m pytest -q

lint:
	python -m ruff check src tests scripts
	python -m ruff format --check src tests scripts

format:
	python -m ruff check --fix src tests scripts
	python -m ruff format src tests scripts

compile:
	python -m compileall -q src

check: lint test compile

benchmark:
	python -m threatlens benchmark

build:
	python -m build

demo:
	python scripts/demo.py --output demo-artifacts

docker-build:
	docker build -t threatlens .

docker-help:
	docker run --rm threatlens --help
