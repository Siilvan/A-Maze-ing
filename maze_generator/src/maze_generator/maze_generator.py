import random
from typing import override
from .config import MazeConfig
from .logo import Logos
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
        self.blocked: list[list[bool]] = Logos("G", conf).MakeLogo()

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
        if self.is_blocked(r, c):
            return
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
            if r_idx == 0: allow &= ~1
            if c_idx == self.width - 1: allow &= ~2
            if r_idx == self.height - 1: allow &= ~4
            if c_idx == 0: allow &= ~8
            if self.is_blocked(r_idx - 1, c_idx): allow &= ~1
            if self.is_blocked(r_idx, c_idx + 1): allow &= ~2
            if self.is_blocked(r_idx + 1, c_idx): allow &= ~4
            if self.is_blocked(r_idx, c_idx - 1): allow &= ~8
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

    def is_blocked(self, y: int, x: int) -> bool:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.blocked[y][x]
        return False


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
        self.compute_can_continue()
        for y in range(self.height):
            self.sets = self.new_sets
            self.new_sets = []
            merge_chance: float = (0.55 if y != self.height - 1 else 1)
            if y != 0:
                self.initialise_sets(self.grid[y - 1])
                self.h_corridors(self.grid[y], y, merge_chance, self.grid[y - 1])
            else:
                self.initialise_sets()
                self.h_corridors(self.grid[y], y, merge_chance)
            if y != self.height - 1:
                self.force_valid_sets(self.grid[y], y)
                self.v_corridors(self.grid[y], y)

    def compute_can_continue(self) -> None:
        h, w = self.height, self.width
        ok = [[False] * w for _ in range(h)]
        for x in range(w):
            ok[h - 1][x] = not self.is_blocked(h - 1, x)
        for y in range(h - 2, -1, -1):
            x = 0
            while x < w:
                if self.is_blocked(y, x):
                    x += 1
                    continue
                start = x
                while x < w and not self.is_blocked(y, x):
                    x += 1
                segment = range(start, x)
                if any(not self.is_blocked(y + 1, c) and ok[y + 1][c]
                    for c in segment):
                    for c in segment:
                        ok[y][c] = True
        self.ok = ok

    def can_go_down(self, y: int, x: int) -> bool:
        return (not self.is_blocked(y, x)
                and not self.is_blocked(y + 1, x)
                and self.ok[y + 1][x])
    
    def force_valid_sets(self, row: list[int], y: int) -> None:
        if y == self.height - 1:
            return
        while True:
            set_dict: dict[int, list[int]] = {}
            for x in range(self.width):
                s_id = self.new_sets[x]
                if self.is_blocked(y, x):
                    continue
                if s_id not in set_dict.keys():
                    set_dict[s_id] = []
                set_dict[s_id].append(x)
            stuck_sets = []
            for s_id, cell_list in set_dict.items():
                valid_cells = [
                    c for c in cell_list
                    if self.can_go_down(y, c)
                ]
                if not valid_cells:
                    stuck_sets.append(s_id)
            if not stuck_sets:
                break
            fixed = False
            for s_id in stuck_sets:
                for x in set_dict[s_id]:
                    if (x > 0 and self.new_sets[x - 1] != s_id and
                        not self.is_blocked(y, x - 1)):
                        neighbour_set = self.new_sets[x - 1]
                        row[x - 1] &= ~2
                        row[x] &= ~8
                        self.merge_sets(s_id, neighbour_set)
                        fixed = True
                        break
                    elif (x < self.width - 1 and self.new_sets[x + 1] != s_id and
                          not self.is_blocked(y, x + 1)):
                        neighbour_set= self.new_sets[x + 1]
                        row[x + 1] &= ~8
                        row[x] &= ~2
                        self.merge_sets(s_id, neighbour_set)
                        fixed = True
                        break
                if fixed:
                    break
            if not fixed:
                raise ValueError(f"set {stuck_sets[0]} is fully enclosed")

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

    def v_corridors(self, row: list[int], y: int):
        set_dict: dict[int, list[int]] = {}
        for x in range(self.width):
            if self.new_sets[x] in set_dict.keys():
                set_dict[self.new_sets[x]].append(x)
            else:
                set_dict[self.new_sets[x]] = [x]
        for cell_list in set_dict.values():
            valid_cells = [cell for cell in cell_list 
                            if self.can_go_down(y, cell)]
            if not valid_cells:
                continue

            forced = random.choice(valid_cells)
            for cell in cell_list:
                if self.is_blocked(y, cell) or self.is_blocked(y + 1, cell):
                    continue
                dead_pocket_below = not self.ok[y + 1][cell]
                if cell == forced or dead_pocket_below or random.random() < 0.4:
                    row[cell] &= ~4


    def h_corridors(
            self, row: list[int], y: int,
            merge_chance: float, row_above: list[int] = []
            ) -> None:
        for x in range(self.width - 1):
            if (self.new_sets[x] != self.new_sets[x + 1] and
               random.random() < merge_chance and
               not self.is_blocked(y, x) and not self.is_blocked(y, x + 1)):
                row[x] &= ~2
                row[x + 1] &= ~8
                self.merge_sets(self.new_sets[x], self.new_sets[x + 1])

        for x in range(self.width):
            if row_above and (row_above[x] & 4) == 0:
                row[x] &= ~1
