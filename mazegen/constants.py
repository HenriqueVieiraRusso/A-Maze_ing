from typing import Final


NORTH: Final[int] = 1  # 0001 (north wall present)
EAST:  Final[int] = 2  # 0010 (east wall present)
SOUTH: Final[int] = 4  # 0100 (south wall present)
WEST:  Final[int] = 8  # 1000 (west wall present)

MAX_LOOP_DENSITY: Final[float] = 0.25
