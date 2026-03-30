from typing import Generator, List, Set, Tuple, Any
from .directions import DIRECTIONS


Coord = Tuple[int, int]
Neighbor = Tuple[int, int, str]
DFSStep = Tuple[int, int, str]   # (x, y, action)


class DFSGenerator:
    def __init__(
        self,
        grid: List[List[int]],
        rng: Any,
        in_bounds: Any,
        open_wall: Any,
    ) -> None:

        self.grid = grid
        self.rng = rng
        self.in_bounds = in_bounds
        self.open_wall = open_wall

    def generate(
        self,
        start: Coord,
        blocked: Set[Coord],
    ) -> Generator[DFSStep, None, None]:
        """Run DFS maze carving, yielding each step.

        Yields:
            (x, y, action) where action is:
              'visit'     — moved into a new cell and carved a wall
              'backtrack' — dead end, popped from the stack
        """
        visited: Set[Coord] = set()
        stack: List[Coord] = []

        visited.add(start)
        stack.append(start)
        yield (start[0], start[1], 'visit')

        while stack:
            x, y = stack[-1]

            # Collect all valid unvisited neighbours
            neighbors: List[Neighbor] = []

            for d, (dx, dy, _, _) in DIRECTIONS.items():
                nx, ny = x + dx, y + dy

                if not self.in_bounds(nx, ny):
                    continue

                if (nx, ny) in visited:
                    continue

                if (nx, ny) in blocked:
                    continue

                # Valid candidate: add to neighbour list
                neighbors.append((nx, ny, d))

            # If there are no available neighbours, backtrack by popping
            if not neighbors:
                stack.pop()
                yield (x, y, 'backtrack')
                continue

            # Choose a random neighbour and carve a passage to it
            nx, ny, d = self.rng.choice(neighbors)

            # Remove the wall between current cell and chosen neighbour
            self.open_wall(x, y, d)

            # Mark neighbour visited and push it onto the stack
            visited.add((nx, ny))
            stack.append((nx, ny))
            yield (nx, ny, 'visit')
