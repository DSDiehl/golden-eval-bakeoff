.PHONY: install lint format test eval iac-validate check all clean demo

install:
	pip install -e ".[dev]"

lint:
	ruff check src/ tests/ eval/ examples/
	mypy src/

format:
	ruff format src/ tests/ eval/ examples/
	ruff check --fix src/ tests/ eval/ examples/

test:
	pytest -v tests/

eval:
	pytest -v eval/

iac-validate:
	terraform -chdir=terraform init -backend=false
	terraform -chdir=terraform validate

check: lint test eval

all: lint test eval iac-validate

demo:
	python3 examples/run_bakeoff_demo.py

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache .ruff_cache .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
