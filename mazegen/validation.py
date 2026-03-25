from typing import List, Tuple, Any
from .directions import DIRECTIONS


class MazeValidator:
    def __init__(
        self,
        grid: list[list[int]],
        width: int,
        height: int,
        in_bounds: Any,
    ) -> None:
        self.grid = grid
        self.width = width
        self.height = height
        self.in_bounds = in_bounds

    def validate(
        self,
        entry: Tuple[int, int],
        exit_: Tuple[int, int],
        perfect: bool,
    ) -> bool:

        # Unpack coordinates
        ex, ey = entry
        ox, oy = exit_

        if not (self.in_bounds(ex, ey) and self.in_bounds(ox, oy)):
            return False

        if entry == exit_:
            return False

        # DFS to check reachability of all cells from the entry
        visited = [[False] * self.width for _ in range(self.height)]
        stack: List[Tuple[int, int]] = [entry]

        visited[ey][ex] = True
        reachable = 1

        while stack:
            x, y = stack.pop()

            # Explore each compass direction from the current cell
            for dx, dy, wall, _ in DIRECTIONS.values():
                nx, ny = x + dx, y + dy

                # Skip out-of-bounds neighbours
                if not self.in_bounds(nx, ny):
                    continue

                # If the wall bit is 0 (no wall) movement is possible
                if not (self.grid[y][x] & wall):
                    if not visited[ny][nx]:
                        visited[ny][nx] = True
                        stack.append((nx, ny))
                        reachable += 1

        total_cells = self.width * self.height

        # Maze must be fully connected
        if reachable != total_cells:
            return False

        # If a perfect maze is requested, verify the edge count equals
        # nodes - 1.
        if perfect:
            edges = 0

            for y in range(self.height):
                for x in range(self.width):
                    cell = self.grid[y][x]
                    # Check each possible wall bit; if it's cleared that's
                    # an open passage and contributes to the edge count.
                    for wall in [1, 2, 4, 8]:
                        if not (cell & wall):
                            edges += 1

            edges //= 2  # each edge is stored twice (once per endpoint)

            # For a perfect maze: edges == nodes - 1
            if edges != total_cells - 1:
                return False

        return True
