"""Terminal rendering for the A-Maze-ing project."""

from .constants import NORTH, EAST, SOUTH, WEST
from .directions import DIRECTIONS

# ── ANSI color codes ──────────────────────────────────

COLORS: dict[str, str] = {
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "bright_red": "\033[91m",
    "bright_green": "\033[92m",
    "bright_yellow": "\033[93m",
    "bright_blue": "\033[94m",
    "bright_magenta": "\033[95m",
    "bright_cyan": "\033[96m",
    "bright_white": "\033[97m",
}
RESET = "\033[0m"
_ENTRY_CLR = "\033[92m"   # bright green
_EXIT_CLR = "\033[91m"    # bright red
_PATH_CLR = "\033[93m"    # bright yellow
_PAT42_CLR = "\033[35m"   # magenta — the 42 pattern cells

# ── Box-drawing helpers ───────────────────────────────

# Corner characters indexed by which walls connect.
# Index = up*8 + right*4 + down*2 + left*1
# Example: up + right = 8+4 = 12 -> "└"
_CORNERS = " ╴╷┐╶─┌┬╵┘│┤└┴├┼"

# Direction arrows for path display
_ARROWS: dict[str, str] = {
    "N": "↑", "E": "→", "S": "↓", "W": "←",
}


def _h_wall(
    grid: list[list[int]],
    cx: int, cy: int,
    w: int, h: int,
) -> bool:
    """Is there a horizontal wall right of corner (cx,cy)?

    Checks the NORTH bit of the cell below, or the SOUTH
    bit of the cell above, depending on position.
    """
    if cx >= w:
        return False
    if cy == 0:
        return bool(grid[0][cx] & NORTH)
    if cy == h:
        return bool(grid[h - 1][cx] & SOUTH)
    return bool(grid[cy][cx] & NORTH)


def _v_wall(
    grid: list[list[int]],
    cx: int, cy: int,
    w: int, h: int,
) -> bool:
    """Is there a vertical wall below corner (cx, cy)?

    Checks the WEST bit of the cell to the right, or the
    EAST bit of the cell to the left, depending on position.
    """
    if cy >= h:
        return False
    if cx == 0:
        return bool(grid[cy][0] & WEST)
    if cx == w:
        return bool(grid[cy][w - 1] & EAST)
    return bool(grid[cy][cx] & WEST)


def _corner(
    grid: list[list[int]],
    cx: int, cy: int,
    w: int, h: int,
) -> str:
    """Return the box-drawing char for corner (cx, cy).

    Looks at the four possible wall segments meeting at
    this corner and picks the matching unicode character.
    """
    up = int(cy > 0 and _v_wall(grid, cx, cy - 1, w, h))
    rt = int(_h_wall(grid, cx, cy, w, h))
    dn = int(_v_wall(grid, cx, cy, w, h))
    lt = int(cx > 0 and _h_wall(grid, cx - 1, cy, w, h))
    return _CORNERS[up * 8 + rt * 4 + dn * 2 + lt]


def _cell(
    x: int, y: int,
    entry: tuple[int, int],
    exit: tuple[int, int],
    path_map: dict[tuple[int, int], str],
    pattern42: frozenset[tuple[int, int]],
    clr: str,
) -> str:
    """Return the 3-char content for cell (x, y)."""
    if (x, y) == entry:
        return _ENTRY_CLR + " E " + clr
    if (x, y) == exit:
        return _EXIT_CLR + " X " + clr
    if (x, y) in path_map:
        arrow = _ARROWS.get(path_map[(x, y)], "·")
        return _PATH_CLR + " " + arrow + " " + clr
    if (x, y) in pattern42:
        return _PAT42_CLR + " ▪ " + clr
    return "   "


def _trace_path(
    entry: tuple[int, int],
    path: str,
) -> dict[tuple[int, int], str]:
    """Convert NESW path string to dict of cell->direction."""
    cells: dict[tuple[int, int], str] = {}
    x, y = entry
    for ch in path:
        cells[(x, y)] = ch
        dx, dy = DIRECTIONS[ch][0], DIRECTIONS[ch][1]
        x, y = x + dx, y + dy
    cells[(x, y)] = "*"
    return cells


def _top_line(
    grid: list[list[int]], y: int,
    w: int, h: int,
) -> str:
    """Build the top-wall line for row y."""
    line = ""
    for x in range(w):
        line += _corner(grid, x, y, w, h)
        line += "───" if grid[y][x] & NORTH else "   "
    line += _corner(grid, w, y, w, h)
    return line


def _cell_line(
    grid: list[list[int]], y: int, w: int,
    entry: tuple[int, int],
    exit: tuple[int, int],
    path_map: dict[tuple[int, int], str],
    pattern42: frozenset[tuple[int, int]],
    clr: str,
) -> str:
    """Build the cell-content line for row y."""
    line = ""
    for x in range(w):
        line += "│" if grid[y][x] & WEST else " "
        line += _cell(
            x, y, entry, exit, path_map, pattern42, clr,
        )
    line += "│" if grid[y][w - 1] & EAST else " "
    return line


# ── Main rendering ────────────────────────────────────

def render(
    grid: list[list[int]],
    entry: tuple[int, int],
    exit: tuple[int, int],
    path: str,
    show_path: bool,
    wall_color: str,
    pattern42: frozenset[tuple[int, int]] = frozenset(),
) -> None:
    """Render the maze to the terminal.

    Draws the maze grid with optional path overlay using
    ANSI colors. Entry is shown as 'E' (green), exit as
    'X' (red), path as arrows (yellow), and the 42 pattern
    cells as magenta squares.

    Args:
        grid: A 2D list of integers encoding wall presence
            per cell using bitflags (N=1, E=2, S=4, W=8).
        entry: Tuple of (x, y) for the maze entry point.
        exit: Tuple of (x, y) for the maze exit point.
        path: A NESW string representing the solution path.
        show_path: Whether to overlay the solution path.
        wall_color: ANSI color name for rendering walls.
        pattern42: Cells belonging to the 42 pattern.
    """
    h = len(grid)
    w = len(grid[0])
    clr = COLORS.get(wall_color, "")

    path_map: dict[tuple[int, int], str] = {}
    if show_path and path:
        path_map = _trace_path(entry, path)

    for y in range(h):
        top = _top_line(grid, y, w, h)
        print(clr + top + RESET)
        mid = _cell_line(
            grid, y, w, entry, exit,
            path_map, pattern42, clr,
        )
        print(clr + mid + RESET)

    # bottom wall line
    bot = ""
    for x in range(w):
        bot += _corner(grid, x, h, w, h)
        bot += "───" if grid[h - 1][x] & SOUTH else "   "
    bot += _corner(grid, w, h, w, h)
    print(clr + bot + RESET)


# ── Interactive menu ──────────────────────────────────

_MENU_ITEMS = [
    "1. Display maze",
    "2. Solve & show path",
    "3. Change wall color",
    "4. Regenerate (new seed)",
    "5. Show maze info",
    "6. Exit",
]


def show_menu() -> int:
    """Display the interactive menu and return the choice.

    Presents options for displaying, solving, customizing
    and regenerating the maze.

    Returns:
        An integer corresponding to the selected option.
    """
    bw = 32
    print()
    print("╔" + "═" * bw + "╗")
    title = " A-MAZE-ING MENU ".center(bw)
    print("║" + title + "║")
    print("╠" + "═" * bw + "╣")
    for item in _MENU_ITEMS:
        pad = " " * (bw - len(item) - 2)
        print("║ " + item + pad + " ║")
    print("╚" + "═" * bw + "╝")

    n = len(_MENU_ITEMS)
    while True:
        try:
            choice = int(input("\nSelect option: "))
            if 1 <= choice <= n:
                return choice
            print(f"Please enter 1-{n}.")
        except ValueError:
            print("Invalid input. Enter a number.")
