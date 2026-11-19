import random
from typing import Generator, override

from maze_generator.utils import solution_to_directions

from .helpers import Logger
from .config import MazeConfig
from .logo import Logos
from abc import ABC, abstractmethod

class MazeGenerator(ABC):
    """
    Base class for the maze generators.

    Holds the grid, the logo mask and the stuff every generator needs:
    editing walls, killing dead ends and the main generate_maze wrapper.
    Child classes only have to fill in initial_grid.

    Wall bits: 1 = north, 2 = east, 4 = south, 8 = west.
    A cell of 15 means walls on all sides.
    """

    def __init__(self, conf: MazeConfig):
        """Sets up the size, a grid full of walls (15), and the logo mask."""
        self.config = conf
        self.width = conf.width
        self.height = conf.height
        self.perfect = conf.perfect
        self.generated: bool = False
        self.blocked = Logos(conf.logo.strip("\n"), conf).MakeLogo()

    def get_maze(self) -> list[list[int]]:
        """Gives back the grid."""
        return self.grid

    def generate_maze(self) -> None:
        """Resets the grid, builds the maze
        and removes dead ends if perfect isnt true."""
        self.grid = [[15 for _ in range(self.width)] for _ in range(self.height)]
        self.initial_grid()
        if not self.perfect:
            self.remove_dead_ends()
        self.generated = True

    @abstractmethod
    def initial_grid(self) -> None:
        """
        Every generator has to have this.
        Should create a perfect maze (no loops).
        """
        pass

    def edit_wall(self, row: int, col: int, pwr: int, remove: bool) -> None:
        """
        Adds or removes one wall on a cell,
        and the opposing wall on the neighbour cell.
        Does nothing if the cell is part of the logo.
        """
        nbr = pow(2, pwr)
        row_dir = row + (pwr % 2 == 0) * (pwr - 1)
        cell_dir = col + (pwr % 2) * (2 - pwr)
        opposite = (1 << ((pwr + 2) % 4))
        if self.is_blocked(row, col):
            return
        if remove:
            self.grid[row][col] &= ~nbr
            self.grid[row_dir][cell_dir] &= ~opposite
        else:
            self.grid[row][col] |= nbr
            self.grid[row_dir][cell_dir] |= opposite

    def get_allowed_walls(self, r_idx: int, c_idx: int, cell: int) -> int:
        """For dead ends (3 walls) returns which walls we're allowed to remove.
        Border and logo walls aren't allowed. Anything else gives 0."""
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
            if self.is_blocked(r_idx - 1, c_idx):
                allow &= ~1
            if self.is_blocked(r_idx, c_idx + 1):
                allow &= ~2
            if self.is_blocked(r_idx + 1, c_idx):
                allow &= ~4
            if self.is_blocked(r_idx, c_idx - 1):
                allow &= ~8
        else:
            allow = 0
        return (allow)

    def get_set_bits(self, nbr: int) -> list[int]:
        """Returns the positions of the 1 bits, e.g. 10 (0b1010) -> [1, 3]."""
        positions = []
        position = 0
        while nbr > 0:
            if nbr & 1:
                positions.append(position)
            nbr >>= 1
            position += 1
        return positions

    def is_open_3x3(self, r: int, c: int) -> bool:
        """True if the 3x3 area starting at (r, c) has no walls."""
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
        """Checks the 9 blocks that include (r, c).
        Returns the first open one it finds, if there are any."""
        for wr in range(r - 2, r + 1):
            for wc in range(c - 2, c + 1):
                if self.is_open_3x3(wr, wc):
                    return (True, wr, wc)
        return (False, r, c)

    def check_3x3(self, r: int, c: int) -> None:
        """Puts random walls around the middle of any open 3x3 near (r, c)
        until there are no open areas left."""
        check_open, wr, wc = self.creates_open_3x3(r, c)
        while check_open:
            middle_walls = [3, 5, 6, 9, 10, 12]
            choice = random.choice(middle_walls)
            set_bits = self.get_set_bits(choice)
            for bit in set_bits:
                self.edit_wall(wr + 1, wc + 1, bit, False)
            check_open, wr, wc = self.creates_open_3x3(r, c)

    def remove_dead_ends(self) -> None:
        """Goes over the whole grid,
        knocks a random wall out of every dead end,
        then fixes any 3x3 room that it created."""
        for r_idx, row in enumerate(self.grid):
            for c_idx, cell in enumerate(row):
                allowed: int = self.get_allowed_walls(r_idx, c_idx, cell)
                overlap = allowed & cell
                if picks := self.get_set_bits(overlap):
                    pwr = random.choice(picks)
                    self.edit_wall(r_idx, c_idx, pwr, True)
                    self.check_3x3(r_idx, c_idx)

    def is_blocked(self, y: int, x: int) -> bool:
        """True if (y, x) is a logo cell.
        Out of bounds counts as not blocked."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.blocked[y][x]
        return False

    def grid_iterate(self) -> Generator[tuple[int, int, int]]:
        """
        Returns a generator that iterates over the grid, each item being:
        tuple[int, int, int]
        with (x, y, cell)
        """
        if (not self.generated):
            Logger.get().w("Caution, iterating over the grid of an ungenerated maze")
        for y in range(self.height):
            for x in range(self.width):
                yield (x, y, self.grid[y][x])

    def write_grid_to_file(self) -> None:
        logger = Logger.get()
        if (not self.generated):
            return logger.e("Cannot write to file, " +
                            "the grid has not been generated yet!")
        solution: list[tuple[int, int]] | None = self.get_solution()
        if (solution is None):
            return logger.e("Cannot write to file, " +
                            "Failed to solve the maze!")
        string_solution: str | None = solution_to_directions(solution)
        if (string_solution is None):
            return logger.e("Cannot write to file, " +
                            "Failed to parse solution!")
        with open(self.config.output_path, "w") as f:
            for x, y, cell in self.grid_iterate():
                f.write(hex(cell)[2:])
                if (x == self.width - 1):
                    f.write("\n")
            f.write(f"""
{self.config.entry_pos[0]}, {self.config.entry_pos[1]}
{self.config.exit_pos[0]}, {self.config.exit_pos[1]}
{string_solution}
""")
        Logger.get().i(f"Successfully wrote maze to file: {self.config.output_path}")

    def get_solution(self) -> list[tuple[int, int]] | None:
        """
        Returns the solution of this maze. returns the path as a list of 
        tuples each representing the coordinates of the cells.
        None on failure.
        """
        from .solver import SolverBot
        if (not self.generated):
            Logger.get().w("Caution, trying to solve an ungenerated maze.")
        return SolverBot(self.grid, self.config).solve(True)

class RowByRowMazeGenerator(MazeGenerator):
    """
    Maze generator based on Eller's algorithm.

    Builds the maze one row at a time, using sets to track which cells
    are already connected so no loops appear. Works around the logo cells
    so nothing gets trapped. Good for big mazes since it only looks at one
    row at a time.
    """
    def __init__(self, conf: MazeConfig) -> None:
        """Same as the base setup, with the extra needed set traching stuff."""
        super().__init__(conf)
        self.sets: list[int] = []
        self.new_sets: list[int] = []
        self.next_id = 1

    @override
    def initial_grid(self) -> None:
        """Builds the maze one row at a time
        make sets, join some horizontally,
        fix any stuck sets, then open some paths down."""
        self.compute_can_continue()
        for y in range(self.height):
            self.sets = self.new_sets
            self.new_sets = []
            merge_chance: float = (0.55 if y != self.height - 1 else 1)
            if y != 0:
                self.initialise_sets(self.grid[y - 1])
                self.h_corridors(self.grid[y], y,
                                 merge_chance, self.grid[y - 1])
            else:
                self.initialise_sets()
                self.h_corridors(self.grid[y], y, merge_chance)
            if y != self.height - 1:
                self.force_valid_sets(self.grid[y], y)
                self.v_corridors(self.grid[y], y)

    def compute_can_continue(self) -> None:
        """Works out, for each cell,
        if you can still keep going down from it to the
        bottom row without getting trapped by the logo. Saved in self.ok."""
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
        """True if the cell and the one below it are
        free and the one below isn't a dead pocket."""
        return (not self.is_blocked(y, x)
                and not self.is_blocked(y + 1, x)
                and self.ok[y + 1][x])

    def force_valid_sets(self, row: list[int], y: int) -> None:
        """Makes sure every set in the row has
        at least one cell that can go down.
        If one is stuck, it gets merged with a neighbouring set.
        Errors if it's completely boxed in."""
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
                    elif (x < self.width - 1
                          and self.new_sets[x + 1] != s_id
                          and not self.is_blocked(y, x + 1)):
                        neighbour_set = self.new_sets[x + 1]
                        row[x + 1] &= ~8
                        row[x] &= ~2
                        self.merge_sets(s_id, neighbour_set)
                        fixed = True
                        break
                if fixed:
                    break
            if not fixed:
                raise ValueError(f"set {stuck_sets[0]} is fully enclosed")

    def initialise_sets(self, row_above: list[int] = []) -> None:
        """Gives every cell in the new row a set id.
        Cells with an open path from above
        inheret their set, the rest get a new one.
        Also builds the members lookup."""
        self.members: dict[int, list[int]] = {}
        for x in range(self.width):
            if row_above and (row_above[x] & 4) == 0:
                s_id = self.sets[x]
            else:
                s_id = self.next_id
                self.next_id += 1
            self.new_sets.append(s_id)
            self.members.setdefault(s_id, []).append(x)

    def merge_sets(self, set_a: int, set_b: int) -> None:
        """Merges two sets, relabelling the smaller one so it stays fast."""
        if set_a == set_b:
            return
        a, b = self.members[set_a], self.members[set_b]
        if len(a) < len(b):
            set_a, set_b = set_b, set_a
            a, b = b, a
        for x in b:
            self.new_sets[x] = set_a
        a.extend(b)
        del self.members[set_b]

    def v_corridors(self, row: list[int], y: int) -> None:
        """Opens the south walls.
        Every set gets at least one way down, plus some
        extras at random (40%). Cells above a dead pocket always open."""
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
                if (cell == forced
                   or dead_pocket_below
                   or random.random() < 0.4):
                    row[cell] &= ~4

    def h_corridors(
            self, row: list[int], y: int,
            merge_chance: float, row_above: list[int] = []
            ) -> None:
        """Randomly joins neighbouring cells of different
        sets sideways (not through the logo),
        then opens the north wall of cells that connect up to the row above."""
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
