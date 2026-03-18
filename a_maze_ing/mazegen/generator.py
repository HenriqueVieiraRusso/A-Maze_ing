import random
from typing import Final, List, Tuple


NORTH: Final[int] = 1
EAST: Final[int] = 2
SOUTH: Final[int] = 4
WEST: Final[int] = 8

DIRECTIONS = {
    "N": (0, -1, NORTH, SOUTH),
    "E": (1, 0, EAST, WEST),
    "S": (0, 1, SOUTH, NORTH),
    "W": (-1, 0, WEST, EAST),
}


class MazeGenerator:
    """Generates a maze using the configured algorithm.

    Attributes:
        width: Number of columns in the maze.
        height: Number of rows in the maze.
        seed: Random seed for reproducible generation.
        perfect: Whether to generate a perfect maze (no loops).
        entry: Tuple of (row, col) for the maze entry point.
        exit: Tuple of (row, col) for the maze exit point.
    """

    def __init__(
        self,
        width: int,
        height: int,
        seed: int,
        perfect: bool,
        entry: tuple[int, int],
        exit_: tuple[int, int],
    ) -> None:
        """Initialize the MazeGenerator."""

        self.width = width
        self.height = height
        self.seed = seed
        self.perfect = perfect
        self.entry = entry
        self.exit_ = exit_
        self.stamp42: set[tuple[int,int]] = set()

    # Maze grid (all walls closed)
        self.grid: list[list[int]] = [
            [15 for _ in range(width)] for _ in range(height)]

    # Create a random generator with the seed
        self.rng = random.Random(seed)

    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if (x, y) is inside the maze grid."""
        return 0 <= x < self.width and 0 <= y < self.height

    def generate(self) -> list[list[int]]:
        """Generate the maze using recursive backtracker."""
        visited = [[False] * self.width for _ in range(self.height)]

        stack = [self.entry]
        ex, ey = self.entry
        visited[ey][ex] = True

        while stack:
            x, y = stack[-1]

            neighbors = self.get_unvisited_neighbors(x, y, visited)

            if neighbors:
                nx, ny, wall, opposite = self.rng.choice(neighbors)

                self.remove_wall(x, y, nx, ny, wall, opposite)

                visited[ny][nx] = True
                stack.append((nx, ny))

            else:
                stack.pop()

        self.embed_42()

        if not self.perfect:
            self.add_loops()

        self.fix_open_areas()

        return self.grid                                                                                                                                                                                                               

    def validate(self) -> bool:
        """Validate the generated maze."""
        # 1. Entry / Exit checks
        ex, ey = self.entry
        ox, oy = self.exit_

        if not (self.in_bounds(ex, ey) and self.in_bounds(ox, oy)):
            return False

        if self.entry == self.exit_:
            return False

        # 2. Connectivity check (DFS)
        reachable_cells: List[List[bool]] = [[False] * self.width for _ in range(self.height)]
        stack: List[Tuple[int, int]] = [self.entry]
        reachable_cells[ey][ex] = True
        reachable: int = 1

        while stack:
            # removes the current cell from the stack
            x, y = stack.pop()

            for dx, dy, wall, opposite in DIRECTIONS.values():
                # nx e ny vao ter o valor da cell vizinha atual
                nx, ny = x + dx, y + dy

                if not self.in_bounds(nx, ny):
                    # se cell vizinha nao for valida (fora da grid)
                    continue

                # return true if no wall 
                if not (self.grid[y][x] & wall):
                    # checks in the negative if the current cell has a wall in the direction that wall holds
                    if not reachable_cells[ny][nx]:
                        # adicion cell que ainda nao foram reached para a stack
                        reachable_cells[ny][nx] = True
                        stack.append((nx, ny))
                        reachable += 1

        total_cells = self.width * self.height

        if reachable != total_cells:
            return False  # Not fully connected

        # 3. Perfect maze check (tree property)
        if self.perfect:
            # only runs se o self.perfect = True
            open_walls = 0

            for y in range(self.height):
                for x in range(self.width):
                    cell = self.grid[y][x]

                    for wall in [NORTH, EAST, SOUTH, WEST]:
                        # Loops through each of the 4 wall constants one by one and checks if that wall is open on the current cell
                        if not (cell & wall):
                            # se a parede estiver aberta openwall++
                            open_walls += 1

            edges = open_walls / 2

            if edges != total_cells - 1:
                return False

        return True

    def fix_open_areas(self) -> None:
        """Fix open areas larger than 2x2 in a perfect maze, without affecting the 42 pattern."""

        for y in range(self.height - 2):
            for x in range(self.width - 2):
                open_cells = 0
                for dy in range(3):
                    for dx in range(3):
                        cell_coords = (x+dx, y+dy)
                        if cell_coords in self.stamp42:
                            continue  # never touch 42 cells
                        cell = self.grid[y+dy][x+dx]
                        if cell == 0:
                            open_cells += 1

                if open_cells >= 3:
                    # Close one wall safely in a cell not part of 42
                    for dy in range(3):
                        for dx in range(3):
                            cell_x, cell_y = x+dx, y+dy
                            if (cell_x, cell_y) in self.stamp42:
                                continue
                            cell = self.grid[cell_y][cell_x]
                            if cell != 15:  # Try closing any open wall safely
                                for wall, (dx2, dy2) in zip(
                                    [NORTH, EAST, SOUTH, WEST],
                                    [(0, -1), (1, 0), (0, 1), (-1, 0)]
                                ):
                                    nx, ny = cell_x + dx2, cell_y + dy2
                                    if self.in_bounds(nx, ny) and not (cell & wall):
                                        self.grid[cell_y][cell_x] |= wall
                                        self.grid[ny][nx] |= {NORTH:SOUTH, EAST:WEST, SOUTH:NORTH, WEST:EAST}[wall]
                                        break
                            break
                        else:
                            continue
                        break

    def embed_42(self) -> None:
        """Embed the number 42 visually into the middle of the maze using fully closed cells."""
        
        try:
            coords = self._get_42_coords()
        except ValueError:
            print("Maze too small to embed '42'.")
            return

        self._stamp_42(coords)


    def _get_42_coords(self) -> set[tuple[int, int]]:
        """Return coordinates of a centered '42' pattern (size-aware)."""
        
        # Patterns: 1 = fill/closed, . = leave as-is
        pat_small = [
            "#.#.###",
            "#.#...#",
            "###.###",
            "..#.#..",
            "..#.###",
        ]  # 7x5

        pat_med = [
            "#..#.####",
            "#..#....#",
            "####.####",
            "...#.#...",
            "...#.####",
            ".......#.",
        ]  # 8x6

        pat_big = [
            "#...#.#####",
            "#...#.....#",
            "#...#.....#",
            "#####.#####",
            "....#.#....",
            "....#.#....",
            "....#.#####",
        ]  # 11x7

        # Pick pattern based on maze size
        if self.width < 28 or self.height < 20:
            pattern = pat_small
        elif self.width < 45 or self.height < 30:
            pattern = pat_med
        else:
            pattern = pat_big

        base_h = len(pattern)
        base_w = len(pattern[0])

        margin = 2
        avail_w = self.width - (2 * margin)
        avail_h = self.height - (2 * margin)

        if avail_w < base_w or avail_h < base_h:
            raise ValueError("Maze too small for 42 pattern")

        # Center the stamp
        ox = (self.width - base_w) // 2
        oy = (self.height - base_h) // 2

        coords: set[tuple[int, int]] = set()
        for py in range(base_h):
            row = pattern[py]
            for px in range(base_w):
                if row[px] == ".":
                    continue
                coords.add((ox + px, oy + py))

        return coords


    def _stamp_42(self, coords: set[tuple[int, int]]) -> None:
        """Stamp the "42" pattern into the maze by setting those cells fully closed."""
        self.stamp42.clear()           # store coords in the object
        self.stamp42.update(coords)        
        
        for x, y in coords:
            if not self.in_bounds(x, y):
                continue

            # Fully close this cell
            self.grid[y][x] = 15

            # Also close adjacent walls to keep consistency
            for dx, dy, wall, opposite in DIRECTIONS.values():
                nx, ny = x + dx, y + dy
                if self.in_bounds(nx, ny):
                    self.grid[ny][nx] |= opposite

    def remove_wall(
        self,
        x: int,
        y: int,
        nx: int,
        ny: int,
        wall: int,
        opposite: int,
    ) -> None:
        """Remove wall between two cells."""
        self.grid[y][x] &= ~wall
        self.grid[ny][nx] &= ~opposite

    def get_unvisited_neighbors(
        self,
        x: int,
        y: int,
        visited: list[list[bool]]
    ):
        neighbors = []

        for dx, dy, wall, opposite in DIRECTIONS.values():
            nx = x + dx
            ny = y + dy

            if self.in_bounds(nx, ny) and not visited[ny][nx]:
                neighbors.append((nx, ny, wall, opposite))

        return neighbors

    def add_loops(self) -> None:
    """Remove extra walls to create loops and multiple solution paths."""
    # how many extra walls to remove — adjust to taste
    num_loops = (self.width * self.height) // 10  # 10% of total cells

    attempts = 0
    loops_added = 0

    while loops_added < num_loops and attempts < 1000:
        # pick a random cell
        x = self.rng.randint(0, self.width - 1)
        y = self.rng.randint(0, self.height - 1)

        # skip 42 pattern cells
        if (x, y) in self.stamp42:
            attempts += 1
            continue

        # pick a random wall to remove
        wall, opposite, dx, dy = self.rng.choice([
            (NORTH, SOUTH, 0, -1),
            (EAST,  WEST,  1,  0),
            (SOUTH, NORTH, 0,  1),
            (WEST,  EAST, -1,  0),
        ])

        nx, ny = x + dx, y + dy

        # skip if neighbor is out of bounds or part of 42
        if not self.in_bounds(nx, ny):
            attempts += 1
            continue

        if (nx, ny) in self.stamp42:
            attempts += 1
            continue

        # only remove walls that are still closed — otherwise pointless
        if self.grid[y][x] & wall:
            self.remove_wall(x, y, nx, ny, wall, opposite)
            loops_added += 1

        attempts += 1
