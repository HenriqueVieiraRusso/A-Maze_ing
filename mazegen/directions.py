from typing import Dict, Tuple
from .constants import NORTH, EAST, SOUTH, WEST


DIRECTIONS: Dict[str, Tuple[int, int, int, int]] = {
    "N": (0, -1, NORTH, SOUTH),
    "E": (1,  0, EAST,  WEST),
    "S": (0,  1, SOUTH, NORTH),
    "W": (-1, 0, WEST,  EAST),
}
