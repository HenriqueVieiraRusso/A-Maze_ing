"""Terminal rendering for the A-Maze-ing project."""

import time
from typing import Generator

from .constants import NORTH, EAST, SOUTH, WEST
from .directions import DIRECTIONS
from .dfs import DFSStep

_ANIM_DELAY = 0.02  # seconds between animation frames

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
BG_COLORS: dict[str, str] = {
    "red": "\033[41m",
    "green": "\033[42m",
    "yellow": "\033[43m",
    "blue": "\033[44m",
    "magenta": "\033[45m",
    "cyan": "\033[46m",
    "white": "\033[47m",
    "bright_red": "\033[101m",
    "bright_green": "\033[102m",
    "bright_yellow": "\033[103m",
    "bright_blue": "\033[104m",
    "bright_magenta": "\033[105m",
    "bright_cyan": "\033[106m",
    "bright_white": "\033[107m",
}
RESET = "\033[0m"
_ENTRY_CLR = "\033[92m"      # bright green
_EXIT_CLR = "\033[91m"       # bright red
_PATH_CLR = "\033[93m"       # bright yellow
_VISIT_CLR = "\033[44m"      # blue background — active cell
_BACKTRACK_CLR = "\033[100m" # dark grey background — backtracked cell

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
    pat42_clr: str,
    dfs_visited: frozenset[tuple[int, int]] | None = None,
    dfs_backtracked: frozenset[tuple[int, int]] | None = None,
    dfs_current: tuple[int, int] | None = None,
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
        return pat42_clr + "   " + RESET + clr
    if dfs_current is not None and (x, y) == dfs_current:
        return _VISIT_CLR + " · " + RESET + clr
    if dfs_backtracked and (x, y) in dfs_backtracked:
        return _BACKTRACK_CLR + "   " + RESET + clr
    if dfs_visited and (x, y) in dfs_visited:
        return _VISIT_CLR + "   " + RESET + clr
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
    pat42_clr: str,
    dfs_visited: frozenset[tuple[int, int]] | None = None,
    dfs_backtracked: frozenset[tuple[int, int]] | None = None,
    dfs_current: tuple[int, int] | None = None,
) -> str:
    """Build the cell-content line for row y."""
    line = ""
    for x in range(w):
        line += "│" if grid[y][x] & WEST else " "
        line += _cell(
            x, y, entry, exit, path_map, pattern42, clr, pat42_clr,
            dfs_visited, dfs_backtracked, dfs_current,
        )
    line += "│" if grid[y][w - 1] & EAST else " "
    return line


# ── Main rendering ────────────────────────────────────

def _print_maze(
    grid: list[list[int]],
    h: int, w: int,
    entry: tuple[int, int],
    exit: tuple[int, int],
    path_map: dict[tuple[int, int], str],
    pattern42: frozenset[tuple[int, int]],
    clr: str,
    pat42_clr: str,
    dfs_visited: frozenset[tuple[int, int]] | None = None,
    dfs_backtracked: frozenset[tuple[int, int]] | None = None,
    dfs_current: tuple[int, int] | None = None,
) -> None:
    """Print every line of the maze (shared by all renderers)."""
    for y in range(h):
        print(clr + _top_line(grid, y, w, h) + RESET)
        print(clr + _cell_line(
            grid, y, w, entry, exit,
            path_map, pattern42, clr, pat42_clr,
            dfs_visited, dfs_backtracked, dfs_current,
        ) + RESET)
    bot = ""
    for x in range(w):
        bot += _corner(grid, x, h, w, h)
        bot += "───" if grid[h - 1][x] & SOUTH else "   "
    bot += _corner(grid, w, h, w, h)
    print(clr + bot + RESET)


def render(
    grid: list[list[int]],
    entry: tuple[int, int],
    exit: tuple[int, int],
    path: str,
    show_path: bool,
    wall_color: str,
    pattern42: frozenset[tuple[int, int]] = frozenset(),
    pat42_color: str = "magenta",
) -> None:
    """Render the maze instantly (no animation)."""
    h, w = len(grid), len(grid[0])
    clr = COLORS.get(wall_color, "")
    pat42_clr = BG_COLORS.get(pat42_color, "")
    path_map: dict[tuple[int, int], str] = {}
    if show_path and path:
        path_map = _trace_path(entry, path)
    _print_maze(grid, h, w, entry, exit, path_map, pattern42, clr, pat42_clr)


def animate_generation(
    grid: list[list[int]],
    entry: tuple[int, int],
    exit: tuple[int, int],
    wall_color: str,
    pattern42: frozenset[tuple[int, int]] = frozenset(),
    pat42_color: str = "magenta",
) -> None:
    """Reveal the maze row by row with a short delay.

    Prints the top wall and cell line for each row in
    sequence, pausing between rows to create the effect
    of the maze appearing from top to bottom.
    """
    h, w = len(grid), len(grid[0])
    clr = COLORS.get(wall_color, "")
    pat42_clr = BG_COLORS.get(pat42_color, "")
    for y in range(h):
        print(clr + _top_line(grid, y, w, h) + RESET)
        print(clr + _cell_line(
            grid, y, w, entry, exit,
            {}, pattern42, clr, pat42_clr,
        ) + RESET)
        time.sleep(_ANIM_DELAY)
    bot = ""
    for x in range(w):
        bot += _corner(grid, x, h, w, h)
        bot += "───" if grid[h - 1][x] & SOUTH else "   "
    bot += _corner(grid, w, h, w, h)
    print(clr + bot + RESET)


def animate_path(
    grid: list[list[int]],
    entry: tuple[int, int],
    exit: tuple[int, int],
    path: str,
    wall_color: str,
    pattern42: frozenset[tuple[int, int]] = frozenset(),
    pat42_color: str = "magenta",
) -> None:
    """Draw the solution path one step at a time.

    Builds the path map incrementally. After each step,
    moves the cursor back up with ANSI to overwrite the
    previous frame — no screen flash.
    """
    h, w = len(grid), len(grid[0])
    clr = COLORS.get(wall_color, "")
    pat42_clr = BG_COLORS.get(pat42_color, "")
    lines = h * 2 + 1   # lines printed per full maze render

    # Pre-build the ordered list of (x, y, marker) steps
    steps: list[tuple[int, int, str]] = []
    x, y = entry
    for ch in path:
        steps.append((x, y, ch))
        x, y = x + DIRECTIONS[ch][0], y + DIRECTIONS[ch][1]
    steps.append((x, y, "*"))   # final cell at exit

    path_map: dict[tuple[int, int], str] = {}
    for i, (sx, sy, d) in enumerate(steps):
        path_map[(sx, sy)] = d
        if i > 0:
            # Move cursor back up to overwrite the previous frame
            print(f"\033[{lines}A", end="", flush=True)
        _print_maze(
            grid, h, w, entry, exit,
            path_map, pattern42, clr, pat42_clr,
        )
        time.sleep(_ANIM_DELAY)


def animate_dfs(
    grid: list[list[int]],
    entry: tuple[int, int],
    exit: tuple[int, int],
    steps: Generator[DFSStep, None, None],
    wall_color: str,
    pattern42: frozenset[tuple[int, int]] = frozenset(),
    pat42_color: str = "magenta",
) -> None:
    """Animate DFS generation step by step.

    Colours visited cells with a blue background and
    backtracked cells with a dark grey background.
    The current cell is marked with a dot.
    Redraws the full maze on every step using cursor
    repositioning so the display stays in place.
    """
    h, w = len(grid), len(grid[0])
    clr = COLORS.get(wall_color, "")
    pat42_clr = BG_COLORS.get(pat42_color, "")
    lines = h * 2 + 1

    visited: set[tuple[int, int]] = set()
    backtracked: set[tuple[int, int]] = set()
    first = True

    for i, (x, y, action) in enumerate(steps):
        if action == 'visit':
            visited.add((x, y))
        elif action == 'backtrack':
            backtracked.add((x, y))

        current = (x, y) if action == 'visit' else None

        if not first:
            print(f"\033[{lines}A", end="", flush=True)
        first = False

        _print_maze(
            grid, h, w, entry, exit,
            {}, pattern42, clr, pat42_clr,
            frozenset(visited),
            frozenset(backtracked),
            current,
        )
        time.sleep(_ANIM_DELAY)


# ── Interactive menu ──────────────────────────────────

_MENU_ITEMS = [
    "1. Animate DFS generation",
    "2. Animate maze reveal",
    "3. Animate solution path",
    "4. Change wall color",
    "5. Regenerate (new seed)",
    "6. Show maze info",
    "7. Exit",
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
