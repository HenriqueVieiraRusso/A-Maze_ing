# A-Maze-ing

A Python maze generator with hex wall encoding, BFS solver, and terminal
visual renderer — 42 school project.

## Description

A-Maze-ing generates perfect or imperfect mazes of configurable dimensions
using a recursive backtracker algorithm. Walls are encoded as bitflags per
cell (N=1, E=2, S=4, W=8), the maze can be solved with BFS, and results
are rendered directly in the terminal with optional path overlay.

## Instructions

```bash
make install   # create virtualenv and install dependencies
make run       # run with default config.txt
make debug     # run under pdb debugger
make lint      # run flake8 linter
make lint-strict  # run flake8 with stricter settings
make clean     # remove build artifacts and virtualenv
```

## Resources

- [Maze generation algorithms — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Recursive backtracker — Jamis Buck](https://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracking)
- [BFS shortest path — Wikipedia](https://en.wikipedia.org/wiki/Breadth-first_search)

## Config Format

Configuration is read from a plain-text file with `KEY=VALUE` pairs:

```
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42
ALGORITHM=recursive_backtracker
```

## Algorithm

The default algorithm is **recursive backtracker** (depth-first search with
backtracking). Each cell tracks open passages using bitflags:

| Bit | Direction |
|-----|-----------|
|  1  | North     |
|  2  | East      |
|  4  | South     |
|  8  | West      |

## Reusable Module

The `mazegen` package can be imported independently:

```python
from mazegen.config import parse_config
from mazegen.generator import MazeGenerator
from mazegen.solver import solve
from mazegen.renderer import render
```

## Team

- [cs50fran](https://github.com/cs50fran)
