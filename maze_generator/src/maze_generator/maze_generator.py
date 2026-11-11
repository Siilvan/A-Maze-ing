import random
from .config import MazeConfig
from abc import ABC, abstractmethod


class MazeGenerator(ABC):
    """
    Base class for other maze generators.

    It defines the abstract "initial_grid" class every generator should have.

    Contains some functions that every maze generator needs:
        - remove_dead_ends
        - draw_logo
        - generate_maze
    """
    def __init__(self, conf: MazeConfig):
        self.width = conf.width
        self.height = conf.height
        self.grid: list[list[int]] = [
            [15 for _ in range(self.width)]
            for _ in range(self.height)]
        self.perfect = conf.perfect

    def get_maze(self) -> list[list[int]]:
        return self.grid

    def generate_maze(self) -> None:
        """
        Wrapper function for creating the full maze
        """
        self.initial_grid()
        if not self.perfect:
            self.remove_dead_ends()

    @abstractmethod
    def initial_grid(self) -> None:
        """
        Abstract method.
        
        This should create the initial grid of the maze.
        The grid should be an unchanged perfect grid.
        """
        pass

    def edit_wall(self, r: int, c: int, pwr: int, remove: bool) -> None:
        nbr = pow(2, pwr)
        row_dir = r + (pwr % 2 == 0) * (pwr - 1)
        cell_dir = c + (pwr % 2) * (2 - pwr)
        opposite = (1 << ((pwr + 2) % 4))
        if remove:
            self.grid[r][c] &= ~nbr
            self.grid[row_dir][cell_dir] &= ~opposite
        else:
            self.grid[r][c] |= nbr
            self.grid[row_dir][cell_dir] |= opposite

    def get_allowed_walls(self, r_idx: int, c_idx: int, cell: int) -> int:
        cnt = 0
        n = cell
        while n > 0:
            n &= (n - 1)
            cnt += 1
        if cnt == 3:
            allow = 15
            if r_idx == 0:
                allow &= ~1
            if c_idx == self.width - 1:
                allow &= ~2
            if r_idx == self.height - 1:
                allow &= ~4
            if c_idx == 0:
                allow &= ~8
        else:
            allow = 0
        return (allow)

    def get_set_bits(self, nbr: int) -> list[int]:
        positions = []
        position = 0
        while nbr > 0:
            if nbr & 1:
                positions.append(position)
            nbr >>= 1
            position += 1
        return positions

    def is_open_3x3(self, r: int, c: int) -> bool:
        if r > self.height - 3 or c > self.width - 3:
            return False
        if r < 0 or c < 0:
            return False
        for rr in range(r, r + 3):
            for cc in range(c, c + 2):
                if self.grid[rr][cc] & 2:
                    return False
        for rr in range(r, r + 2):
            for cc in range(c, c + 3):
                if self.grid[rr][cc] & 4:
                    return False
        return True

    def creates_open_3x3(self, r: int, c: int) -> tuple[bool, int, int]:
        for wr in range(r - 2, r + 1):
            for wc in range(c - 2, c + 1):
                if self.is_open_3x3(wr, wc):
                    return (True, wr, wc)
        return (False, r, c)

    def check_3x3(self, r: int, c: int) -> None:
        check_open, wr, wc = self.creates_open_3x3(r, c)
        while check_open:
            middle_walls = [3, 5, 6, 9, 10, 12]
            choice = random.choice(middle_walls)
            set_bits = self.get_set_bits(choice)
            for bit in set_bits:
                self.edit_wall(wr + 1, wc + 1, bit, False)
            check_open, wr, wc = self.creates_open_3x3(r, c)

    def remove_dead_ends(self) -> None:
        for r_idx, row in enumerate(self.grid):
            for c_idx, cell in enumerate(row):
                allowed: int = self.get_allowed_walls(r_idx, c_idx, cell)
                overlap = allowed & cell
                if picks := self.get_set_bits(overlap):
                    pwr = random.choice(picks)
                    self.edit_wall(r_idx, c_idx, pwr, True)
                    self.check_3x3(r_idx, c_idx)


class RowByRowMazeGenerator(MazeGenerator):
    """
    A type of "MazeGenerator".

    This MazeGenerator is inspired by Ellers algorithm.
    It works with sets and creates the maze row by row.
    This generator is mainly useful for huge mazes
    """
    def __init__(self, conf: MazeConfig) -> None:
        super().__init__(conf)
        self.sets: list[int] = []
        self.new_sets: list[int] = []
        self.next_id = 1
    def initial_grid(self) -> None:
        for y in range(self.height):
            self.sets = self.new_sets
            self.new_sets = []
            merge_chance: float = (0.55 if y != self.height - 1 else 1)
            if y != 0:
                self.initialise_sets(self.grid[y - 1])
                self.h_corridors(self.grid[y], merge_chance, self.grid[y - 1])
            else:
                self.initialise_sets()
                self.h_corridors(self.grid[y], merge_chance)
            if y != self.height - 1:
                self.v_corridors(self.grid[y])

    def initialise_sets(self, row_above: list[int] = []):
        for x in range(self.width):
            if row_above and (row_above[x] & 4) == 0:
                self.new_sets.append(self.sets[x])
            else:
                self.new_sets.append(self.next_id)
                self.next_id += 1

    def merge_sets(self, set_a: int, set_b: int) -> None:
        for x in range(self.width):
            if self.new_sets[x] == set_b:
                self.new_sets[x] = set_a

    def v_corridors(self, row: list[int]):
        set_dict: dict[int, list[int]] = {}
        for x in range(self.width):
            if self.new_sets[x] in set_dict.keys():
                set_dict[self.new_sets[x]].append(x)
            else:
                set_dict[self.new_sets[x]] = [x]
        for cell_list in set_dict.values():
            forced = random.choice(cell_list)
            for cell in cell_list:
                if cell == forced or random.random() < 0.4:
                    row[cell] &= ~4

    def h_corridors(
            self, row: list[int],
            merge_chance: float, row_above: list[int] = []
            ) -> None:
        for x in range(self.width - 1):
            if (self.new_sets[x] != self.new_sets[x + 1] and
               random.random() < merge_chance):
                row[x] &= ~2
                row[x + 1] &= ~8
                self.merge_sets(self.new_sets[x], self.new_sets[x + 1])

        for x in range(self.width):
            if row_above and (row_above[x] & 4) == 0:
                row[x] &= ~1
