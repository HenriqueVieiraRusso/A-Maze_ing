from __future__ import annotations
from collections import deque
from typing import TYPE_CHECKING
from .directions import DIRECTIONS

if TYPE_CHECKING:
    from .generator import MazeGenerator


class MazeSolver:
    def __init__(self, gen: MazeGenerator) -> None:
        self.gen = gen

    def _can_move(self, x: int, y: int, d: str) -> bool:
        dx, dy, bit_current, _ = DIRECTIONS[d]
        nx = x + dx
        ny = y + dy
        if not self.gen.in_bounds(nx, ny):
            return False
        return (self.gen.grid[y][x] & bit_current) == 0

    def solve(self) -> list[str]:
        start: tuple[int, int] = self.gen.entry
        goal: tuple[int, int] = self.gen.exit_

        q: deque[tuple[int, int]] = deque()
        visited: set[tuple[int, int]] = set()
        prev: dict[tuple[int, int], tuple[tuple[int, int], str]] = {}

        q.append(start)
        visited.add(start)

        while q:
            x, y = q.popleft()
            if (x, y) == goal:
                break
            for d, (dx, dy, _, _) in DIRECTIONS.items():
                if not self._can_move(x, y, d):
                    continue
                nxt: tuple[int, int] = (x + dx, y + dy)
                if nxt in visited:
                    continue
                visited.add(nxt)
                prev[nxt] = ((x, y), d)
                q.append(nxt)

        if goal not in visited:
            return []

        path: list[str] = []
        cur: tuple[int, int] = goal
        while cur != start:
            (px, py), d = prev[cur]
            path.append(d)
            cur = (px, py)

        path.reverse()
        return path
