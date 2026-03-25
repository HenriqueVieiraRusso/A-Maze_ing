from collections import deque
from typing import Tuple, List, Set, Iterator
from mazegen import Maze, DIRS  # import Maze and directions from your generator


def solve_bfs(maze: Maze, entry: Tuple[int,int], exit_: Tuple[int,int]) -> List[str]:
    """
    Return the shortest path from entry to exit as a list of moves ['N','E',...].
    Uses BFS (guaranteed shortest path).
    """
    
