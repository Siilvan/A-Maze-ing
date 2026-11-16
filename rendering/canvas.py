from abc import ABC, abstractmethod
from enum import Enum

from mlx import Mlx

class Canvas:
    class Anchors(tuple, Enum):
        TOP_LEFT = (0, 0)
        TOP_RIGHT = (1, 0)
        CENTER = (0.5, 0.5)
        BOT_LEFT = (0, 1)
        BOT_RIGHT = (1, 1)

    def __init__(self, mlx: Mlx, mptr: int, wptr: int, winsize: tuple[int, int]) -> None:
        self.winsize = winsize
        self.mlx = mlx
        self.mptr = mptr
        self.wptr = wptr

class Rect:
    def __init__(self, size: tuple[int, int], start: tuple[int, int], end: tuple[int, int]) -> None:
        self.size = size
        self.start = start
        self.end = end
        pass

    @classmethod
    def empty(cls) -> "Rect":
        """
        Returns a new empty rect
        """
        return Rect((0, 0), (0, 0), (0, 0))

    def has_point(self, point: tuple[int, int]) -> bool:
        """
        Returns wether or not the specified point is within the bounds
        of the rect
        """
        return (point[0] >= self.start[0] and point[0] <= self.end[0]
            and point[1] >= self.start[1] and point[1] <= self.start[1])

class CanvasElement(ABC):

    def __init__(self) -> None:
        self.position: tuple[int, int] = (0, 0)
        self.rect: Rect = Rect.empty()
        self.children: list[CanvasElement] = []
        super().__init__()

    def add_child(self, child: "CanvasElement"):
        """
        Adds a child to this canvas element
        """
        self.children.append(child)

    def remove_child(self, child: "CanvasElement"):
        """
        Removes a child to this canvas element
        """
        self.children.remove(child)

    def draw(self) -> None:
        for c in self.children:
            c.draw()
        c._draw()

    @abstractmethod
    def _draw(self) -> None:
        pass

    def is_hovering(self, mouse_pos: tuple[int, int]) -> bool:
        return (self.rect.has_point(mouse_pos))
