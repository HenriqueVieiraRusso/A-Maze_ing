from collections import deque
from typing import Tuple, List, Set, Iterator
from mazegen import Maze, DIRS  # import Maze and directions from your generator


def solve_bfs(maze: Maze, entry: Tuple[int,int], exit_: Tuple[int,int]) -> List[str]:
    """
    Return the shortest path from entry to exit as a list of moves ['N','E',...].
    Uses BFS (guaranteed shortest path).
    """
    visited: Set[Tuple[int,int]] = set()
    prev: dict[Tuple[int,int], Tuple[Tuple[int,int], str]] = {}

    q = deque()
    q.append(entry)
    visited.add(entry)

    while q:
        x, y = q.popleft()
        if (x,y) == exit_:
            break

        for d, (dx, dy, _, _) in DIRS.items():
            nx, ny = x + dx, y + dy
            if not (0 <= nx < maze.width and 0 <= ny < maze.height):
                continue
            if (nx, ny) in visited:
                continue
            # Can only move if wall is open
            if (maze.get(x,y) & DIRS[d][2]) != 0:
                continue
            visited.add((nx, ny))
            prev[(nx, ny)] = ((x, y), d)
            q.append((nx, ny))

    if exit_ not in visited:
        return []

    # Reconstruct path
    path: List[str] = []
    cur = exit_
    while cur != entry:
        cur, move = prev[cur]
        path.append(move)
    path.reverse()
    return path


def solve_bfs_steps(
    maze: Maze,
    entry: Tuple[int,int],
    exit_: Tuple[int,int],
    yield_every: int = 1
) -> Iterator[Tuple[Tuple[int,int], Set[Tuple[int,int]], Set[Tuple[int,int]], List[str]]]:
    """
    BFS solver that yields intermediate states for animation.

    Yields a tuple:
      (current_cell, visited_set, queue_set, path_so_far)
    """
    visited: Set[Tuple[int,int]] = set()
    prev: dict[Tuple[int,int], Tuple[Tuple[int,int], str]] = {}
    q = deque()
    q.append(entry)
    visited.add(entry)

    steps = 0
    yield (entry, set(visited), set(q), [])

    while q:
        x, y = q.popleft()
        if (x, y) == exit_:
            break

        for d, (dx, dy, _, _) in DIRS.items():
            nx, ny = x+dx, y+dy
            if not (0 <= nx < maze.width and 0 <= ny < maze.height):
                continue
            if (nx, ny) in visited:
                continue
            if (maze.get(x,y) & DIRS[d][2]) != 0:
                continue
            visited.add((nx, ny))
            prev[(nx, ny)] = ((x, y), d)
            q.append((nx, ny))

        steps += 1
        if yield_every > 0 and (steps % yield_every) == 0:
            yield ( (x,y), set(visited), set(q), [] )

    # Final path reconstruction
    path: List[str] = []
    cur = exit_
    if cur in prev:
        while cur != entry:
            (px, py), move = prev[cur]
            path.append(move)
            cur = (px, py)
        path.reverse()

    yield (exit_, set(visited), set(q), path)
