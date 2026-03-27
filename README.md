*This project has been created as part of the 42 curriculum by fdinis-d, hevieira.*

# A-Maze-ing

## Description

A-Maze-ing is a Python project that generates, solves, and visually renders
mazes entirely in the terminal. The project was built as part of the 42 school
Python piscine, with a focus on clean code structure, modular design, and
reusability.

Each cell in the maze stores its walls as a bitmask (N=1, E=2, S=4, W=8),
which allows the full maze to be serialised into a compact hex-encoded text
file. The maze can then be solved with a BFS (breadth-first search) algorithm,
and the result is rendered with Unicode box-drawing characters and ANSI colours
directly in the terminal — including an animated reveal of the generation and
the solution path.

**Key features:**

- Configurable maze size, entry/exit points, seed, and perfect/imperfect mode
- Hex-encoded output file (`OUTPUT_FILE`)
- BFS solver returning a `NESW` direction string
- Terminal renderer with box-drawing walls, ANSI colours, and animated rendering
- Visual highlight of the embedded `42` pattern cells
- Interactive menu with colour switching, regeneration, and maze info

---

## Instructions

### Requirements

- Python 3.10 or higher
- A Unix-like terminal (macOS, Linux, WSL)

### Setup

```bash
make install   # creates .venv and installs all dependencies
```

### Running

```bash
make run       # runs with the default config.txt
```

To use a custom config file, run directly:

```bash
.venv/bin/python3 a_maze_ing.py my_config.txt
```

### Other Makefile targets

```bash
make debug        # run under pdb debugger
make lint         # flake8 + mypy with recommended flags
make lint-strict  # flake8 + mypy --strict
make clean        # remove __pycache__, build artefacts, maze.txt
```

---

## Config File

Configuration is read from a plain-text file with `KEY=VALUE` pairs.
Keys are **case-insensitive** and extra whitespace around `=` is ignored.
Lines starting with `#` are treated as comments and skipped.
Lines without an `=` are skipped with a printed warning.

### Full format

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

### Field reference

| Key           | Type    | Required | Description                                      |
|---------------|---------|----------|--------------------------------------------------|
| `WIDTH`       | int > 0 | Yes      | Number of columns                                |
| `HEIGHT`      | int > 0 | Yes      | Number of rows                                   |
| `ENTRY`       | `x,y`   | Yes      | Entry cell, zero-indexed from top-left           |
| `EXIT`        | `x,y`   | Yes      | Exit cell, must differ from `ENTRY`              |
| `OUTPUT_FILE` | string  | Yes      | Path to write the hex-encoded maze file          |
| `PERFECT`     | bool    | Yes      | `True` = no loops (tree), `False` = adds loops   |
| `SEED`        | int > 0 | No       | RNG seed for reproducibility (default: `42`)     |
| `ALGORITHM`   | string  | No       | Generation algorithm (default: `recursive_backtracker`) |

### Validation rules

- `WIDTH` and `HEIGHT` must be positive integers
- `ENTRY` and `EXIT` must be within the maze bounds
- `ENTRY` and `EXIT` cannot be the same cell
- `SEED` must be a positive integer or the word `none` (which defaults to `42`)

---

## Maze Generation Algorithm

The algorithm used is the **recursive backtracker**, a depth-first search
approach where the generator starts from a random cell, carves a passage to an
unvisited neighbour, and backtracks when no unvisited neighbours remain. The
result is a *perfect maze* (exactly one path between any two cells, no loops)
when `PERFECT=True`. When `PERFECT=False`, a configurable number of extra walls
are removed at random to introduce loops.

### Why recursive backtracker?

It was chosen for its simplicity and the quality of mazes it produces.
Compared to algorithms like Kruskal's or Prim's, the recursive backtracker
tends to generate mazes with longer, more winding corridors, which makes the
path harder to guess visually — a desirable property for a maze game. It is
also straightforward to implement incrementally and easy to reason about when
debugging. A second algorithm may be added in a future version.

### Wall encoding

Each cell stores its open passages as a 4-bit integer:

| Bit | Value | Direction |
|-----|-------|-----------|
|  0  |   1   | North     |
|  1  |   2   | East      |
|  2  |   4   | South     |
|  3  |   8   | West      |

A cell with all walls intact is `0xF` (15). A fully open cell is `0x0` (0).
Walls between adjacent cells are always symmetric — opening the north wall of
cell `(x, y)` also opens the south wall of `(x, y-1)`.

---

## Reusable Package

The `mazegen` package is structured to be used independently of the CLI
entry point.

### Install from source

```bash
pip install build
python -m build
pip install ./dist/mazegen-1.0.0.tar.gz
```

### Usage example

```python
from mazegen.generator import MazeGenerator
from mazegen.solver import MazeSolver
from mazegen.config import parse_config, MazeConfig

# Option A — generate directly
gen = MazeGenerator(
    width=20,
    height=15,
    seed=42,
    perfect=True,
    entry=(0, 0),
    exit_=(19, 14),
)
grid = gen.generate()          # 2D list of int bitmasks
path = MazeSolver(gen).solve() # list of direction chars ['N', 'E', ...]

# Option B — generate from a config file
config: MazeConfig = parse_config("config.txt")
gen = MazeGenerator(
    width=config.width,
    height=config.height,
    seed=config.seed,
    perfect=config.perfect,
    entry=config.entry,
    exit_=config.exit,
)
grid = gen.generate()
path = MazeSolver(gen).solve()
```

### Public API

| Symbol | Module | Description |
|--------|--------|-------------|
| `MazeGenerator` | `mazegen.generator` | Generates the maze grid |
| `MazeSolver` | `mazegen.solver` | Solves with BFS, returns `list[str]` |
| `parse_config` | `mazegen.config` | Parses and validates a config file |
| `MazeConfig` | `mazegen.config` | Dataclass holding all config values |
| `render` | `mazegen.renderer` | Renders the maze to the terminal |

---

## Team and Project Management

### Roles

| Member    | Responsibilities                                              |
|-----------|---------------------------------------------------------------|
| `fdinis-d` | Config parsing, Pydantic validation, terminal renderer, animated rendering, interactive menu |
| `hevieira` | Maze generation algorithm, BFS solver, hex output, `42` pattern embedding |

### Planning

We used ChatGPT to help split the project into two independent parts at the
start, which gave us a clean boundary: generation/solving on one side, and
parsing/rendering on the other. In practice it took longer than expected —
mainly because both the parsing and the rendering went through a complete
redesign during the project (see below).

### What worked well

- **Parsing** — the initial implementation worked, but switching to Pydantic
  gave us much cleaner validation with proper error messages and cross-field
  checks (e.g. entry/exit out of bounds).
- **Rendering** — the first version used plain ASCII (`+`, `-`, `|`). Switching
  to Unicode box-drawing characters with computed corner glyphs made the output
  significantly more readable with very little added complexity.
- **Module boundary** — keeping generation and rendering fully separate meant
  both team members could work in parallel without conflicts.

### What could be improved

- **Path animation** — currently the animation shows the final path being drawn
  step by step. It would be more interesting to animate the solver itself as it
  explores cells, showing the BFS frontier expanding until the exit is found.
- **Second algorithm** — only recursive backtracker is implemented. A second
  algorithm (e.g. Kruskal's or Prim's) would add variety and make the
  `ALGORITHM` config key actually meaningful.

### Tools used

- **GitHub** — version control, pull requests, branch-per-feature workflow
- **Claude** — used throughout the project for code generation, refactoring,
  and README writing
- **ChatGPT** — used at the start to split the project into two roles and
  plan the module boundaries

---

## Resources

- [Maze generation algorithms — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Recursive backtracker — Jamis Buck](https://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracking)
- [Breadth-first search — Wikipedia](https://en.wikipedia.org/wiki/Breadth-first_search)
- [Pydantic v2 documentation](https://docs.pydantic.dev/latest/)
- [ANSI escape codes — Wikipedia](https://en.wikipedia.org/wiki/ANSI_escape_code)
- [Unicode box-drawing characters](https://en.wikipedia.org/wiki/Box-drawing_characters)
- [Python dataclasses — docs.python.org](https://docs.python.org/3/library/dataclasses.html)
