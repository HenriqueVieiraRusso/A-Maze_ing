"""A-Maze-ing: entry point for the maze generator application."""

import sys  # noqa: F401

from mazegen.config import parse_config  # noqa: F401
from mazegen.generator import MazeGenerator  # noqa: F401
from mazegen.renderer import render, show_menu  # noqa: F401


def main() -> None:
    """Run the A-Maze-ing maze generator application.

    Reads a config file path from sys.argv[1], parses the configuration,
    generates the maze, writes the output, and renders it to the terminal.

    Args:
        None (reads sys.argv[1] as the config file path).

    Returns:
        None
    """
    pass


if __name__ == "__main__":
    main()
