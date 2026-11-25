import random

from maze_generator.utils import tuple_op

from .maze_generator import MazeGenerator


class DFSMazeGenerator(MazeGenerator):

    def initial_grid(self) -> None:
        _ready: bool = False
        current_cell: tuple[int, int] = self.config.entry_pos
        stack: list[tuple[int, int]] = [current_cell]
        visited_cells: list[tuple[int, int]] = [current_cell]
        while len(stack) > 0 or not _ready:
            n: tuple[int, int] | None = self.pick_random_unvisited_neighbor(
                current_cell, set(visited_cells)
            )
            if n is None:
                current_cell = stack.pop()
                continue
            self.remove_wall_between(current_cell, n)
            stack.append(n)
            visited_cells.append(n)
            current_cell = n
            _ready = True

    def pick_random_unvisited_neighbor(
        self, cell: tuple[int, int], visited_cells: set[tuple[int, int]]
    ) -> tuple[int, int] | None:
        """
        Picks a random neighboring cell not present in the visited_cells set.
        returns None if there is no such neighbor
        """
        neighbors: list[tuple[int, int] | None] = self.get_neighbor_cells(cell)
        valid_neighbors: list[tuple[int, int]] = [
            n for n in neighbors if n is not None and n not in visited_cells
        ]
        if len(valid_neighbors) == 0:
            return None
        return random.choice(valid_neighbors)

    def get_neighbor_cells(
        self, cell: tuple[int, int]
    ) -> list[tuple[int, int] | None]:
        """
        Returns the neighboring cells of the given cell
        as an array of positions.
        the cells are given as follows: [N, E, S, W].
        If a cell has no cell at one of its cardinal, e.g. N, then
        the value for N will be None
        """

        def _is_valid_cell(cell: tuple[int, int]) -> bool:
            if (
                cell[0] >= self.width
                or cell[0] < 0
                or cell[1] >= self.height
                or cell[1] < 0
            ):
                return False

            if self.blocked[cell[1]][cell[0]]:
                return False
            return True

        neighbours: list[tuple[int, int] | None] = []
        cardinals: list[tuple[int, int]] = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        for c in cardinals:
            n: tuple[int, int] = tuple_op(c, cell, lambda a, b: a + b)
            if not _is_valid_cell(n):
                neighbours.append(None)
            else:
                neighbours.append(n)
        return neighbours
