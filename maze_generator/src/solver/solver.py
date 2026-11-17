from maze_generator import MazeConfig
import concurrent.futures
from collections import deque

DIRS: dict[int, tuple[str, int, int]] = {
    0: ("N", -1, 0),
    1: ("E", 0, 1),
    2: ("S", 1, 0),
    3: ("W", 0, -1)
    }

class SolverBot():
    def __init__(self, grid: list[list[int]], conf: MazeConfig) -> None:
        self.grid = grid
        self.entry = tuple(conf.entry_pos)
        self.exit = tuple(conf.exit_pos)
        self.paths: list[list[tuple[int, int]]] = []

    def solve(self, fast: bool) -> list[tuple[int, int]]:
        if fast:
            result = self.fast_solve()
        else:
            self.slow_solve()
            result = min(self.paths, key=len) if self.paths else None
        return result
    
    def fast_solve(self) -> list[tuple[int, int]] | None:
        queue = deque([self.entry])
        visited = {self.entry}
        parent_cell: dict[tuple[int, int], tuple[int, int]] = {}
        while queue:
            curr_cell = queue.popleft()
            if curr_cell == self.exit:
                path = []
                while curr_cell in parent_cell:
                    path.append(curr_cell)
                    curr_cell = parent_cell[curr_cell]
                path.append(self.entry)
                path.reverse()
                return path
            for path in self.get_paths(curr_cell):
                y_dir, x_dir = DIRS[path][1:]
                neighbour = (curr_cell[0] + y_dir, curr_cell[1] + x_dir)
                if neighbour in visited:
                    continue
                queue.append(neighbour)
                visited.add(neighbour)
                parent_cell[neighbour] = curr_cell

    def slow_solve(self):
        self.paths = []
        best_path: dict[tuple[int, int], int] = {}
        with concurrent.futures.ProcessPoolExecutor() as executor:
            futures = {executor.submit(self.walk_path, self.entry, coords=[self.entry])}
            
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
                            executor.submit(self.walk_path, junction, coords, path))
        
    def walk_path(self, pos: list[int, int], coords: list[tuple[int, int]] = [], s_move: int = None) -> tuple[bool, list[int], list[tuple[int, int]]]:
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
                return(False, [], coord_list)
            seen.add(curr_pos)
            if curr_pos == self.exit:
                return (True, [], coord_list)
        return (False, paths, coord_list)
        
    def update_vars(self, curr_pos, coord_list, move) -> tuple[tuple[int, int], list[int]]:
        move_dir, y_dir, x_dir = DIRS[move]
        new_pos = (curr_pos[0] + y_dir, curr_pos[1] + x_dir)
        coord_list.append(new_pos)
        return new_pos, self.get_paths(new_pos, move_dir)

    def get_paths(self, pos: list[int, int], dir: str = "") -> list[int]:
        cell_val = self.grid[pos[0]][pos[1]]
        ignore = 42
        for key, val, in DIRS.items():
            if val[0] == dir:
                ignore = ((key + 2) % 4)
        positions = []
        position = 0
        while position < 4:
            if not cell_val & 1 and not position == ignore:
                positions.append(position)
            cell_val >>= 1
            position += 1
        return positions