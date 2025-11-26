install:
	pip install -e .

lint:
	ruff han

test:
	pytest -q

run-demo:
	python experiments/run_experiment.py --config configs/env.yaml
