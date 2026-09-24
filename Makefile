.PHONY: install train app test

install:
	python3.11 -m pip install -e .

train:
	python3.11 scripts/train.py

app:
	python3.11 scripts/run_app.py

test:
	pytest
