from typing import Final

# Wall bit flags used to represent the presence of walls in each cell.
# Each direction corresponds to a single bit in a 4-bit integer.

# When a bit is set it means the wall is PRESENT. Bits are arranged as
# single-bit flags so multiple walls can be combined into one int per cell.
# Example: `15` == 0b1111 -> all four walls present for that cell.
NORTH: Final[int] = 1  # 0001 (north wall present)
EAST:  Final[int] = 2  # 0010 (east wall present)
SOUTH: Final[int] = 4  # 0100 (south wall present)
WEST:  Final[int] = 8  # 1000 (west wall present)
