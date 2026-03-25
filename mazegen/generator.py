import random
from typing import Optional

from .wall import WallUtils
from .dfs import DFSGenerator
from .patterns import PatternManager
from .loops import LoopGenerator
from .validation import MazeValidator


class MazeGenerator:
    def __init__(
        self,
        width: int,
        height: int,
        seed: Optional[int],
        perfect: bool,
        entry: tuple[int, int],
        exit_: tuple[int, int],
        density: float = 0.06,
    ) -> None:

        self.width = width
        self.height = height
        self.seed = seed
        self.perfect = perfect
        self.entry = entry
        self.exit_ = exit_

        self.density = density

        # Initialize grid (all walls present)
        self.grid = [
            [15 for _ in range(width)] for _ in range(height)
        ]

        # RNG
        self.rng = random.Random(seed)

        # Utility modules
        self.walls = WallUtils(self.grid, self.in_bounds)
        self.patterns = PatternManager(
            self.grid,
            width,
            height,
            self.in_bounds,
        )
        self.validator = MazeValidator(
            self.grid,
            width,
            height,
            self.in_bounds,
        )
        self.loop_gen = LoopGenerator(
            self.grid,
            self.rng,
            self.in_bounds,
            self.walls.open_wall,
            self.walls.can_move,
        )

        self.dfs = DFSGenerator(
            self.grid,
            self.rng,
            self.in_bounds,
            self.walls.open_wall,
        )

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def generate(self) -> list[list[int]]:
        # Validate entry/exit
        self.validator.validate(self.entry, self.exit_, self.perfect)

        # Reset grid
        self.grid = [
            [15 for _ in range(self.width)] for _ in range(self.height)
        ]

        # Rebind utilities to fresh grid
        self.walls.grid = self.grid
        self.patterns.grid = self.grid

        # Compute and stamp 42 pattern
        coords = self.patterns.get_42_coords()
        self.patterns.stamp_42(coords)

        blocked = coords

        self.dfs.generate(self.entry, blocked)

        # Add loops if not perfect
        if not self.perfect:
            self.loop_gen.add_loops(blocked, self.density)

        return self.grid
