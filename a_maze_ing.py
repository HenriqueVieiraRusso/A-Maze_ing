"""A-Maze-ing: entry point for the maze generator application."""

import sys
import random

from mazegen.config import parse_config, MazeConfig
from mazegen.generator import MazeGenerator
from mazegen.solver import MazeSolver
from mazegen.renderer import render, show_menu, COLORS


def _build_maze(
    config: MazeConfig,
    seed: int | None,
) -> tuple[MazeGenerator, list[list[int]], str]:
    """Create a generator, generate the grid, and solve."""
    gen = MazeGenerator(
        width=config.width,
        height=config.height,
        seed=seed,
        perfect=config.perfect,
        entry=config.entry,
        exit_=config.exit,
    )
    grid = gen.generate()
    path = "".join(MazeSolver(gen).solve())
    return gen, grid, path


def _write_output(
    config: MazeConfig,
    grid: list[list[int]],
    path: str,
) -> None:
    """Write the maze to the output file.

    Format (IV.5):
      - One hex digit per cell, row by row, one row per line.
      - An empty line.
      - Entry coordinates as 'x,y'.
      - Exit coordinates as 'x,y'.
      - Solution path as a NESW string.
    All lines end with a newline.

    Args:
        config: Parsed maze configuration (holds output_file).
        grid:   2D list of wall-encoded integers per cell.
        path:   Solution path as a NESW string.
    """
    ex, ey = config.entry
    xx, xy = config.exit
    with open(config.output_file, 'w') as f:
        for row in grid:
            f.write(
                ''.join(format(cell, 'X') for cell in row)
            )
            f.write('\n')
        f.write('\n')
        f.write(f'{ex},{ey}\n')
        f.write(f'{xx},{xy}\n')
        f.write(f'{path}\n')
    print(f"Maze written to '{config.output_file}'.")


def _change_color(wall_color: str) -> str:
    """Prompt the user for a new wall color."""
    print("Available colors:")
    for name in COLORS:
        print(f"  - {name}")
    new = input("Enter color: ").strip()
    if new in COLORS:
        print(f"Color set to {new}.")
        return new
    print("Unknown color, keeping current.")
    return wall_color


def _show_info(
    config: MazeConfig,
    gen: MazeGenerator,
    path: str,
) -> None:
    """Print maze information."""
    print(f"  Size:      {config.width}x{config.height}")
    print(f"  Entry:     {config.entry}")
    print(f"  Exit:      {config.exit}")
    print(f"  Perfect:   {config.perfect}")
    print(f"  Seed:      {gen.seed}")
    print(f"  Algorithm: {config.algorithm}")
    if path:
        print(f"  Path:      {len(path)} steps")
    else:
        print("  Path:      no solution found")


def main() -> None:
    """Run the A-Maze-ing maze generator application.

    Reads a config file path from sys.argv[1], parses it,
    generates the maze, solves it, and presents an
    interactive menu for display and exploration.
    """
    if len(sys.argv) < 2:
        print("Usage: python a_maze_ing.py <config>")
        sys.exit(1)

    try:
        config = parse_config(sys.argv[1])
    except FileNotFoundError:
        print(f"Error: file '{sys.argv[1]}' not found.")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: invalid config — {e}")
        sys.exit(1)

    try:
        gen, grid, path = _build_maze(config, config.seed)
        _write_output(config, grid, path)
    except ValueError as e:
        print(f"Error: could not generate maze — {e}")
        sys.exit(1)
    except OSError as e:
        print(f"Error: could not write output file — {e}")
        sys.exit(1)

    wall_color = "cyan"
    pat42 = frozenset(gen.patterns.stamp42)

    while True:
        choice = show_menu()

        if choice == 1:
            render(
                grid, config.entry, config.exit,
                path, False, wall_color, pat42,
            )
        elif choice == 2:
            render(
                grid, config.entry, config.exit,
                path, True, wall_color, pat42,
            )
        elif choice == 3:
            wall_color = _change_color(wall_color)
        elif choice == 4:
            seed = random.randint(0, 99999)
            gen, grid, path = _build_maze(config, seed)
            _write_output(config, grid, path)
            pat42 = frozenset(gen.patterns.stamp42)
            print(f"New maze generated (seed={seed}).")
        elif choice == 5:
            _show_info(config, gen, path)
        elif choice == 6:
            print("Goodbye!")
            break


if __name__ == "__main__":
    main()
