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
            if (x, y) in blocked:
                continue

            d = self.rng.choice(directions)
            dx, dy, _, _ = DIRECTIONS[d]
            nx, ny = x + dx, y + dy

            if not self.in_bounds(nx, ny):
                continue
            if (nx, ny) in blocked:
                continue
            if self.can_move(x, y, d):
                continue

            self.open_wall(x, y, d)

            if self._creates_invalid_open_area():
                self._close_wall(x, y, d)

    def _close_wall(self, x: int, y: int, d: str) -> None:
        dx, dy, bit_current, bit_opposite = DIRECTIONS[d]
        nx, ny = x + dx, y + dy
        if not self.in_bounds(nx, ny):
            return
        self.grid[y][x] |= bit_current
        self.grid[ny][nx] |= bit_opposite

    def _is_open_between(self, x: int, y: int, nx: int, ny: int) -> bool:
        dx = nx - x
        dy = ny - y
        if dx == 1 and dy == 0:
            return (self.grid[y][x] & 2) == 0 and (self.grid[ny][nx] & 8) == 0
        if dx == -1 and dy == 0:
            return (self.grid[y][x] & 8) == 0 and (self.grid[ny][nx] & 2) == 0
        if dx == 0 and dy == 1:
            return (self.grid[y][x] & 4) == 0 and (self.grid[ny][nx] & 1) == 0
        if dx == 0 and dy == -1:
            return (self.grid[y][x] & 1) == 0 and (self.grid[ny][nx] & 4) == 0
        return False

    def _creates_invalid_open_area(self) -> bool:
        h = len(self.grid)
        if h == 0:
            return False
        w = len(self.grid[0])
        if w < 3 or h < 3:
            return False

        for yy in range(h - 2):
            for xx in range(w - 2):
                all_open = True

                for row in range(3):
                    for col in range(2):
                        if not self._is_open_between(xx + col, yy + row, xx + col + 1, yy + row):
                            all_open = False
                            break
                    if not all_open:
                        break

                if all_open:
                    for row in range(2):
                        for col in range(3):
                            if not self._is_open_between(xx + col, yy + row, xx + col, yy + row + 1):
                                all_open = False
                                break
                        if not all_open:
                            break

                if all_open:
                    return True

        return False
