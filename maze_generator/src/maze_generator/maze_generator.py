import random
from typing import override
from .config import MazeConfig
from abc import ABC, abstractmethod



class MazeGenerator(ABC):
    """
    Base class for other maze generators.

    It defines the abstract "generate_maze" class every generator should have.

    Contains some functions that should work for an type of maze generator:
        - make_non_perfect
        - draw_logo
    """
    def __init__(self, conf: MazeConfig):
        self.width = conf.width
        self.height = conf.height
        self.grid: list[list[int]] = [
            [15 for i in range(self.width)]
            for j in range(self.height)]
        self.sets: list[int] = []
        self.new_sets: list[int] = []
        self.next_id = 1

    @abstractmethod
    def generate_maze(self) -> list[list[int]]:
        pass


class RowByRowMazeGenerator(MazeGenerator):
    """
    A type of "MazeGenerator".

    This MazeGenerator is inspired by Ellers algorithm.
    It works with sets and creates the maze row by row.
    This generator is mainly useful for huge mazes
    """

    @override
    def generate_maze(self) -> list[list[int]]:
        for y in range(self.height):
            self.sets = self.new_sets
            self.new_sets = []
            merge_chance: float = (random.uniform(0.49, 0.55)
                                   if y != self.height - 1 else 1)
            if y != 0:
                self.initialise_sets(self.grid[y - 1])
                self.h_corridors(self.grid[y], merge_chance, self.grid[y - 1])
            else:
                self.initialise_sets()
                self.h_corridors(self.grid[y], merge_chance)
            if y != self.height - 1:
                self.v_corridors(self.grid[y])
        return self.grid

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
            cell = random.choice(cell_list)
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
