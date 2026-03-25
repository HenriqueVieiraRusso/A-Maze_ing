PYTHON = python3
VENV   = venv
PIP    = $(VENV)/bin/pip
RUN    = $(VENV)/bin/python
FLAKE8 = $(VENV)/bin/flake8

.PHONY: install run debug clean lint lint-strict

install:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]"

run:
	$(RUN) a_maze_ing.py config.txt

debug:
	$(RUN) -m pdb a_maze_ing.py config.txt

clean:
	rm -rf $(VENV) __pycache__ mazegen/__pycache__ \
		.mypy_cache dist build *.egg-info \
		maze.txt *.pyc

lint:
	$(FLAKE8) --max-line-length=79 a_maze_ing.py mazegen/

lint-strict:
	$(FLAKE8) --max-line-length=79 --max-complexity=10 \
		--extend-select=W,E a_maze_ing.py mazegen/
