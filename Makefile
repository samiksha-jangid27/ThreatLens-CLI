.PHONY: install test compile check benchmark docker-build docker-help

install:
	python -m pip install ".[dev]"

test:
	pytest -q

compile:
	python -m compileall src

check:
	pytest -q
	python -m compileall src

benchmark:
	threatlens benchmark

docker-build:
	docker build -t threatlens .

docker-help:
	docker run --rm threatlens --help
