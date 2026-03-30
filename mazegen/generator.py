import random
from typing import Optional

from .constants import MAX_LOOP_DENSITY
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
        density: float = 0.1,
    ) -> None:

        self.width = width
        self.height = height
        self.seed = seed
        self.perfect = perfect
        self.entry = entry
        self.exit_ = exit_

        if not (0.0 <= density <= MAX_LOOP_DENSITY):
            raise ValueError(
                f"density must be between 0.0 and {MAX_LOOP_DENSITY}"
            )

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
        self.validator.validate(self.entry, self.exit_, self.perfect)

        self.grid = [
            [15 for _ in range(self.width)] for _ in range(self.height)
        ]

        self.walls.grid = self.grid
        self.patterns.grid = self.grid
        self.loop_gen.grid = self.grid
        self.dfs.grid = self.grid

        self.patterns.embed_42()

        if self.patterns.omitted_42:
            print(
                "\n🌟 Maze too small to include the 42 pattern. ✨"
            )
        elif (
            self.entry in self.patterns.stamp42
            or self.exit_ in self.patterns.stamp42
        ):
            raise ValueError(
                "Entry/exit cannot be inside the 42 pattern"
            )

        blocked = self.patterns.stamp42

        self.dfs.generate(self.entry, blocked)

        # Add loops if not perfect
        if not self.perfect:
            self.loop_gen.add_loops(blocked, self.density)

        return self.grid
