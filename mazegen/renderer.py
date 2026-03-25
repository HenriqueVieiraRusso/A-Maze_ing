"""Terminal rendering for the A-Maze-ing project."""


def render(
    grid: list[list[int]],
    entry: tuple[int, int],
    exit: tuple[int, int],
    path: str,
    show_path: bool,
    wall_color: str,
) -> None:
    """Render the maze to the terminal.

    Draws the maze grid with optional path overlay using ANSI colors.

    Args:
        grid: A 2D list of integers encoding wall presence per cell
            using bitflags (N=1, E=2, S=4, W=8).
        entry: Tuple of (row, col) for the maze entry point.
        exit: Tuple of (row, col) for the maze exit point.
        path: A NESW string representing the solution path.
        show_path: Whether to overlay the solution path on the maze.
        wall_color: ANSI color name or code for rendering walls.

    Returns:
        None
    """
    pass


def show_menu() -> int:
    """Display the interactive menu and return the user's choice.

    Presents options such as generating a new maze, solving, rendering,
    and exiting the program.

    Returns:
        An integer corresponding to the menu option selected by the user.
    """
    pass
