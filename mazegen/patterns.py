from typing import Set, Tuple, Any


class PatternManager:
    def __init__(
        self,
        grid: list[list[int]],
        width: int,
        height: int,
        in_bounds: Any,
    ) -> None:
        self.grid: list[list[int]] = grid
        self.width: int = width
        self.height: int = height
        self.in_bounds: Any = in_bounds

        self.stamp42: Set[Tuple[int, int]] = set()
        self.omitted_42: bool = False

    def get_42_coords(self) -> Set[Tuple[int, int]]:
        pat_small = [
            "#.#.###",
            "#.#...#",
            "###.###",
            "..#.#..",
            "..#.###",
        ]

        pat_med = [
            "#..#.####",
            "#..#....#",
            "####.####",
            "...#.#...",
            "...#.####",
        ]

        pat_big = [
            "#...#.#####",
            "#...#.....#",
            "#...#.....#",
            "#####.#####",
            "....#.#....",
            "....#.#....",
            "....#.#####",
        ]

        # Choose pattern size based on available maze dimensions.
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
            raise ValueError("/n🎨 Maze too small for 42 pattern 🎨")

        # Center the pattern
        ox = (self.width - base_w) // 2
        oy = (self.height - base_h) // 2

        coords: Set[Tuple[int, int]] = set()

        for py in range(base_h):
            row = pattern[py]
            for px in range(base_w):
                if row[px] == ".":
                    # '.' means empty — no stamping at this position
                    continue
                coords.add((ox + px, oy + py))

        return coords

    def stamp_42(self, coords: Set[Tuple[int, int]]) -> None:
        self.stamp42.clear()
        self.stamp42.update(coords)

        for x, y in coords:
            if self.in_bounds(x, y):
                self.grid[y][x] = 15

    def embed_42(self) -> None:
        self.omitted_42 = False
        try:
            coords = self.get_42_coords()
        except ValueError:
            self.omitted_42 = True
            return

        self.stamp_42(coords)
