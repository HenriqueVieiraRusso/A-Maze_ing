"""Configuration parsing for the A-Maze-ing project."""

from dataclasses import dataclass


@dataclass
class MazeConfig:
    """Configuration settings for the maze generator.

    Attributes:
        width: Number of columns in the maze.
        height: Number of rows in the maze.
        entry: Tuple of (row, col) for the maze entry point.
        exit: Tuple of (row, col) for the maze exit point.
        output_file: Path to the file where the maze will be written.
        perfect: Whether to generate a perfect maze (no loops).
        seed: Random seed for reproducible generation.
        algorithm: Name of the maze generation algorithm to use.
    """

    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int
    algorithm: str


def parse_config(filepath: str) -> MazeConfig:
    """Parse a maze configuration file and return a MazeConfig object.

    Reads key=value pairs from the specified file and maps them to the
    corresponding MazeConfig fields.

    Args:
        filepath: Path to the configuration file to parse.

    Returns:
        A MazeConfig instance populated with values from the file.
    """
    pass
