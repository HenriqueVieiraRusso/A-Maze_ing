from typing import Any
from .directions import DIRECTIONS


class WallUtils:
    def __init__(self, grid: list[list[int]], in_bounds: Any) -> None:

        self.grid = grid
        self.in_bounds = in_bounds

    def open_wall(self, x: int, y: int, d: str) -> None:
        dx, dy, bit_current, bit_opposite = DIRECTIONS[d]
        nx, ny = x + dx, y + dy

        if not self.in_bounds(nx, ny):
            return

        self.grid[y][x] &= ~bit_current
        self.grid[ny][nx] &= ~bit_opposite

    def close_wall(self, x: int, y: int, d: str) -> None:
        dx, dy, bit_current, bit_opposite = DIRECTIONS[d]
        nx, ny = x + dx, y + dy

        if not self.in_bounds(nx, ny):
            return

        # Add wall to current cell
        self.grid[y][x] |= bit_current

        # Add opposite wall to neighbor cell
        self.grid[ny][nx] |= bit_opposite

    def can_move(self, x: int, y: int, d: str) -> bool:
        dx, dy, bit_current, _ = DIRECTIONS[d]
        nx, ny = x + dx, y + dy

        if not self.in_bounds(nx, ny):
            return False

        # If the wall bit is NOT set → movement is allowed
        return (self.grid[y][x] & bit_current) == 0

    def remove_wall_between(
        self,
        x: int,
        y: int,
        nx: int,
        ny: int,
        wall: int,
        opposite: int,
    ) -> None:
        # Direct helper that clears two wall bits between two specified cells.
        self.grid[y][x] &= ~wall
        self.grid[ny][nx] &= ~opposite
