from typing import Set, Tuple, Any
from .directions import DIRECTIONS


class LoopGenerator:
    def __init__(
        self,
        grid: list[list[int]],
        rng: Any,
        in_bounds: Any,
        open_wall: Any,
        can_move: Any,
    ) -> None:
        self.grid = grid
        self.rng = rng
        self.in_bounds = in_bounds
        self.open_wall = open_wall
        self.can_move = can_move

    def add_loops(
        self,
        blocked: Set[Tuple[int, int]],
        density: float,
    ) -> None:

        if density <= 0.0:
            return

        attempts = int(len(self.grid) * len(self.grid[0]) * density)
        if attempts < 1:
            return

        directions = list(DIRECTIONS.keys())

        for _ in range(attempts):
            x = self.rng.randrange(len(self.grid[0]))
            y = self.rng.randrange(len(self.grid))
            # Pick a cell at random
            if (x, y) in blocked:
                # Don't touch pattern-blocked cells
                continue

            # Pick a random direction to attempt to open
            d = self.rng.choice(directions)
            dx, dy, _, _ = DIRECTIONS[d]
            nx, ny = x + dx, y + dy

            if not self.in_bounds(nx, ny):
                continue

            if (nx, ny) in blocked:
                continue

            # Only add a loop if a wall currently exists between the cells
            if self.can_move(x, y, d):
                continue

            # Open the wall to create a loop
            self.open_wall(x, y, d)

            # Safety check: if the new opening creates an invalid open area
            # we undo it. The placeholder returns False so by default loops
            # are left open.
            if self._creates_invalid_open_area():
                self._close_wall(x, y, d)

    def _close_wall(self, x: int, y: int, d: str) -> None:
        dx, dy, bit_current, bit_opposite = DIRECTIONS[d]
        nx, ny = x + dx, y + dy

        if not self.in_bounds(nx, ny):
            return

        self.grid[y][x] |= bit_current
        self.grid[ny][nx] |= bit_opposite

    def _creates_invalid_open_area(self) -> bool:
        # Detect simple "room" patterns introduced by opening a wall.
        # We forbid 2x2 fully-open blocks (all four internal adjacencies open)
        # which commonly create large open areas that break maze feel.
        h = len(self.grid)
        if h == 0:
            return False
        w = len(self.grid[0])
        if w < 2 or h < 2:
            return False

        # Helper to test whether wall between (x,y) and (nx,ny) is open
        def is_open_between(x: int, y: int, nx: int, ny: int) -> bool:
            # Determine direction from (x,y) to (nx,ny)
            dx = nx - x
            dy = ny - y
            if dx == 1 and dy == 0:
                # right neighbour: check EAST of (x,y)
                left_open = (self.grid[y][x] & 2) == 0
                right_open = (self.grid[ny][nx] & 8) == 0
                return left_open and right_open
            if dx == -1 and dy == 0:
                # left neighbour: check WEST of (x,y)
                left_open = (self.grid[y][x] & 8) == 0
                right_open = (self.grid[ny][nx] & 2) == 0
                return left_open and right_open
            if dx == 0 and dy == 1:
                # down neighbour: check SOUTH of (x,y)
                top_open = (self.grid[y][x] & 4) == 0
                bottom_open = (self.grid[ny][nx] & 1) == 0
                return top_open and bottom_open
            if dx == 0 and dy == -1:
                # up neighbour: check NORTH of (x,y)
                top_open = (self.grid[y][x] & 1) == 0
                bottom_open = (self.grid[ny][nx] & 4) == 0
                return top_open and bottom_open
            return False

        # Scan all 2x2 blocks for fully-open internal connections
        for yy in range(h - 1):
            for xx in range(w - 1):
                a = (xx, yy)
                b = (xx + 1, yy)
                c = (xx, yy + 1)
                d = (xx + 1, yy + 1)

                # Check internal adjacencies: a-b, a-c, b-d, c-d
                if (
                    is_open_between(a[0], a[1], b[0], b[1])
                    and is_open_between(a[0], a[1], c[0], c[1])
                    and is_open_between(b[0], b[1], d[0], d[1])
                    and is_open_between(c[0], c[1], d[0], d[1])
                ):
                    return True

        return False
