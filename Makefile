PY  = .venv/bin/python3
PIP = .venv/bin/pip

.PHONY: install run debug lint lint-strict pack clean

install:
	python3 -m venv .venv
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]"

run:
	$(PY) a_maze_ing.py config.txt

debug:
	$(PY) -m pdb a_maze_ing.py config.txt

lint:
	$(PY) -m flake8 . --exclude .venv
	$(PY) -m mypy . --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	$(PY) -m flake8 . --exclude .venv
	$(PY) -m mypy . --strict

pack:
	$(PIP) install build -q
	$(PY) -m build
	cp dist/mazegen-*.tar.gz dist/mazegen-*-none-any.whl .

clean:
	rm -rf __pycache__ mazegen/__pycache__ \
		.mypy_cache build dist *.egg-info \
		*.pyc maze.txt
