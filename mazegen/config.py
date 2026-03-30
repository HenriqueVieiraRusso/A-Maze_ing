"""Configuration parsing for the A-Maze-ing project."""

import shutil
from dataclasses import dataclass
from pydantic import (  # ignore
    BaseModel,
    Field,
    ValidationError,
    field_validator,
    model_validator,
)


def get_terminal_size() -> tuple[int, int]:
    """Return maze-appropriate (width, height) derived from terminal size.

    Width is terminal columns // 4, height is terminal lines // 2.
    """
    cols, lines = shutil.get_terminal_size()
    return cols // 4, lines // 2


@dataclass
class MazeConfig:
    """Configuration settings for the maze generator.

    Attributes:
        width: Number of columns in the maze.
        height: Number of rows in the maze.
        entry: Tuple of (row, col) for the maze entry point.
        exit: Tuple of (row, col) for the maze exit point.
        output_file: Path to the file where the maze will be written.
        perfect: Whether to generate a perfect maze (no loops).
        seed: Random seed for reproducible generation. (opt)
        algorithm: Name of the maze generation algorithm to use. (opt)
    """

    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int = 42
    algorithm: str = 'recursive_backtracker'


class _ConfigModel(BaseModel):
    """Pydantic model for validating config values.

    Uses Field constraints for individual values and
    a model_validator for cross-field rules (bounds check).
    """

    width: int = Field(gt=0)
    height: int = Field(gt=0)
    entry: tuple[int, int]
    exit_point: tuple[int, int]
    output_file: str = Field(min_length=1)
    perfect: bool

    @field_validator('output_file')
    @classmethod
    def output_file_must_be_txt(cls, v: str) -> str:
        if ' ' in v or not v.endswith('.txt'):
            raise ValueError(
                f"OUTPUT_FILE incorrect formatting: '{v}'"
            )
        return v
    seed: int = 42
    algorithm: str = 'recursive_backtracker'

    @model_validator(mode='after')
    def check_bounds(self) -> '_ConfigModel':
        """Ensure entry/exit are inside the grid."""
        ex, ey = self.entry
        w, h = self.width, self.height
        if ex < 0 or ex >= w or ey < 0 or ey >= h:
            raise ValueError(
                f"Entry {self.entry} out of bounds"
            )
        xx, xy = self.exit_point
        if xx < 0 or xx >= w or xy < 0 or xy >= h:
            raise ValueError(
                f"Exit {self.exit_point} out of bounds"
            )
        if self.entry == self.exit_point:
            raise ValueError(
                "Entry and exit cannot be the same"
            )
        return self


def _parse_seed(value: str) -> int:
    """Parse a seed value, raising on invalid input.

    Returns 42 if the value is 'none' (case-insensitive).
    Raises ValueError for empty strings, non-integers,
    or integers that are not positive (> 0).

    Raises:
        ValueError: If the value is not a positive int
            or the string 'none'.
    """
    if value.lower() == 'none':
        return 42
    error_msg = (
        "SEED must be a positive integer or 'none',"
        f" got '{value}'"
    )
    try:
        seed = int(value)
        if seed <= 0:
            raise ValueError
    except ValueError as exc:
        raise ValueError(error_msg) from exc
    return seed


def _parse_point(value: str) -> tuple[int, int]:
    """Parse 'x,y' string into an (int, int) tuple."""
    parts = value.split(',')
    if len(parts) != 2:
        raise ValueError(
            f"Expected 'x,y' format, got '{value}'"
        )
    return (int(parts[0].strip()), int(parts[1].strip()))


def parse_config(filepath: str) -> MazeConfig:
    """Parse a maze configuration file.

    Reads KEY=VALUE pairs from the file, validates them
    through a Pydantic model, and returns a MazeConfig.

    Args:
        filepath: Path to the configuration file to parse.

    Returns:
        A MazeConfig instance populated with validated values.
    """
    raw: dict[str, str] = {}
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            key, sep, value = line.partition('=')
            if not sep:
                print(
                    f"  Skipping malformed line: '{line}'"
                    "\n  Expected format: KEY=VALUE"
                )
                continue
            raw[key.strip().upper()] = value.strip()

    required = ['WIDTH', 'HEIGHT', 'ENTRY', 'EXIT',
                'OUTPUT_FILE', 'PERFECT']
    for key in required:
        if key not in raw:
            raise ValueError(f"Missing config key: {key}")

    width = int(raw['WIDTH'])
    height = int(raw['HEIGHT'])
    term_w, term_h = get_terminal_size()
    if width > term_w:
        raise ValueError(
            f"WIDTH {width} exceeds terminal limit {term_w}"
            f" (terminal columns // 4)"
        )
    if height > term_h:
        raise ValueError(
            f"HEIGHT {height} exceeds terminal limit {term_h}"
            f" (terminal lines // 2)"
        )

    seed = (
        _parse_seed(raw['SEED'].strip())
        if 'SEED' in raw else 42
    )
    algo = raw.get(
        'ALGORITHM',
        'recursive_backtracker'
    ).strip().lower()

    try:
        validated = _ConfigModel(
            width=width,
            height=height,
            entry=_parse_point(raw['ENTRY']),
            exit_point=_parse_point(raw['EXIT']),
            output_file=raw['OUTPUT_FILE'],
            perfect=raw['PERFECT'].lower()
            in ('true', '1', 'yes'),
            seed=seed,
            algorithm=algo,
        )
    except ValidationError as e:
        msgs = [
            str(err['ctx']['error'])
            if 'ctx' in err and 'error' in err['ctx']
            else err['msg']
            for err in e.errors()
        ]
        raise ValueError('; '.join(msgs)) from e

    if algo in (
        'recursive_backtracker',
        'recursive backtracker',
    ):
        algo = 'recursive_backtracker'
    else:
        print(
            "\n⚠️ Algorithm not available, defaulting to"
            " recursive backtracker"
        )
        algo = 'recursive_backtracker'
    return MazeConfig(
        width=validated.width,
        height=validated.height,
        entry=validated.entry,
        exit=validated.exit_point,
        output_file=validated.output_file,
        perfect=validated.perfect,
        seed=validated.seed,
        algorithm=validated.algorithm,
    )
