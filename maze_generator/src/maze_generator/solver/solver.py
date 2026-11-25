import concurrent.futures
from collections import deque
from ..config import MazeConfig

DIRS: dict[int, tuple[str, int, int]] = {
    0: ("N", -1, 0),
    1: ("E", 0, 1),
    2: ("S", 1, 0),
    3: ("W", 0, -1),
}


class SolverBot:
    """
    Finds a path through a finished maze from the entry to the exit.

    There are two ways to solve it:
        - fast: BFS, always gives the shortest path, one process.
        - slow: walks every corridor in parallel across processes,
          collects every path that reaches the exit, then picks the shortest.

    Paths are lists of (row, col) cells, starting at the entry and
    ending at the exit.
    """

    def __init__(self, grid: list[list[int]], conf: MazeConfig) -> None:
        """
        Saves the maze grid, the entry and exit cells from the config,
        and an empty list where slow_solve stores the paths it finds.
        """
        self.grid = grid
        self.entry: tuple[int, int] = (conf.entry_pos[1], conf.entry_pos[0])
        self.exit: tuple[int, int] = (conf.exit_pos[1], conf.exit_pos[0])
        self.paths: list[list[tuple[int, int]]] = []

    def solve(self, fast: bool) -> list[tuple[int, int]] | None:
        """
        Main function you call to solve the maze.

        fast=True uses fast_solve (BFS). fast=False uses slow_solve and
        returns the shortest path it found.

        Returns the path as a list of (row, col) cells, or None if
        there's no way from entry to exit.
        """
        if fast:
            result = self._fast_solve()
        else:
            self._slow_solve()
            result = min(self.paths, key=len) if self.paths else None
        if result is not None:
            return [(t[1], t[0]) for t in result]
        return None

    def _fast_solve(self) -> list[tuple[int, int]] | None:
        """
        Solves the maze with a breadth-first search.

        Spreads out from the entry one step at a time, remembering which
        cell each cell was reached from. Once the exit is hit, it walks
        back through those parents to build the path, then flips it so it
        runs entry -> exit. BFS means the first path found is the shortest.

        Returns the path, or None if the exit can't be reached.
        """
        queue = deque([self.entry])
        visited = {self.entry}
        parents: dict[tuple[int, int], tuple[int, int]] = {}
        while queue:
            curr_cell: tuple[int, int] = queue.popleft()
            if curr_cell == self.exit:
                path = []
                while curr_cell in parents:
                    path.append(curr_cell)
                    curr_cell = parents[curr_cell]
                path.append(self.entry)
                path.reverse()
                return path
            options = self.get_paths(curr_cell)
            for option in options:
                _, y_dir, x_dir = DIRS[option]
                neighbour = (curr_cell[0] + y_dir, curr_cell[1] + x_dir)
                if neighbour in visited:
                    continue
                queue.append(neighbour)
                visited.add(neighbour)
                parents[neighbour] = curr_cell
        return None

    def _slow_solve(self) -> None:
        """
        Solves the maze by exploring corridors in parallel with a process pool.

        Each task walks one corridor until it hits a split, a dead end,
        a loop or the exit. At a junction, a new task is started for every
        way out. A junction is only continued if this route got there
        faster than any route before it (best_path), which stops it from
        exploring the same stuff over and over.

        Returns nothing. Every route that reaches the exit gets added to
        self.paths, and solve() picks the shortest one.
        """

        self.paths = []
        best_path: dict[tuple[int, int], int] = {}
        with concurrent.futures.ProcessPoolExecutor() as executor:
            futures = {
                executor.submit(
                    self.walk_path, self.entry, coords=[self.entry]
                )
            }

            while futures:
                done, futures = concurrent.futures.wait(
                    futures, return_when=concurrent.futures.FIRST_COMPLETED
                )
                for future in done:
                    found, branches, coords = future.result()
                    if found:
                        self.paths.append(coords)
                    if not branches:
                        continue
                    junction = coords[-1]
                    if len(coords) >= best_path.get(junction, float("inf")):
                        continue
                    best_path[junction] = len(coords)
                    for path in branches:
                        futures.add(
                            executor.submit(
                                self.walk_path, junction, coords, path
                            )
                        )

    def walk_path(
        self,
        pos: tuple[int, int],
        coords: list[tuple[int, int]] = [],
        s_move: int | None = None,
    ) -> tuple[bool, list[int], list[tuple[int, int]]]:
        """
        Follows a corridor forward until something interesting happens.

        Starts from the last cell in coords.
        If s_move is set, the first step is forced in that direction,
        which is how you leave a junction down a chosen path. Keeps
        walking as long as theres only one way forward, and stops when:
            - it reaches the exit,
            - it hits a dead end,
            - it gets stuck in a loop,
            - it reaches a junction.

        Returns a tuple of:
            - found: True if it reached the exit
            - branches: the directions available at the junction
              (empty if it ended for any other reason)
            - coords: the full path walked so far
        """
        coord_list = [c for c in (coords or [pos])]
        curr_pos = coord_list[-1]
        seen = set(coord_list)
        if s_move is not None:
            paths = [s_move]
        else:
            paths = self.get_paths(curr_pos)
        while len(paths) == 1:
            curr_pos, paths = self.update_vars(curr_pos, coord_list, paths[0])
            if curr_pos in seen:
                return (False, [], coord_list)
            seen.add(curr_pos)
            if curr_pos == self.exit:
                return (True, [], coord_list)
        return (False, paths, coord_list)

    def update_vars(
        self,
        curr_pos: tuple[int, int],
        coord_list: list[tuple[int, int]],
        move: int,
    ) -> tuple[tuple[int, int], list[int]]:
        """
        Takes one step in the given direction.

        Adds the new cell to coord_list and looks up where
        you can go from there, without going back the way you came.

        Returns the new position and the list of directions open from it.
        """
        move_dir, y_dir, x_dir = DIRS[move]
        new_pos = (curr_pos[0] + y_dir, curr_pos[1] + x_dir)
        coord_list.append(new_pos)
        return new_pos, self.get_paths(new_pos, move_dir)

    def get_paths(self, pos: tuple[int, int], dir: str = "") -> list[int]:
        """
        Looks at one cell and says which directions are open.

        dir is the letter of the direction you just moved ("N", "E", "S"
        or "W"). The opposite direction is skipped so you don't walk
        straight back. Leave it empty to get every open direction, like
        at the start.

        Returns a list of direction indexes (0 = N, 1 = E, 2 = S, 3 = W).
        """
        cell_val = self.grid[pos[0]][pos[1]]
        ignore = 42
        for (
            key,
            val,
        ) in DIRS.items():
            if val[0] == dir:
                ignore = (key + 2) % 4
        positions = []
        position = 0
        while position < 4:
            if not cell_val & 1 and not position == ignore:
                positions.append(position)
            cell_val >>= 1
            position += 1
        return positions
