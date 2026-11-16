from abc import ABC, abstractmethod
from enum import Enum

from mlx import Mlx

from logger import Logger
from rendering.image import MlxImage
from rendering.window import MlxWindow

class Rect:
    def __init__(self, size: tuple[int, int], start: tuple[int, int]) -> None:
        self.size = size
        self.start = start
        self.end = (self.start[0] + self.size[0], self.start[1] + self.size[1])
        pass

    @classmethod
    def empty(cls) -> "Rect":
        """
        Returns a new empty rect
        """
        return Rect((0, 0), (0, 0))

    def has_point(self, point: tuple[int, int]) -> bool:
        """
        Returns wether or not the specified point is within the bounds
        of the rect
        """
        return (point[0] >= self.start[0] and point[0] <= self.end[0]
            and point[1] >= self.start[1] and point[1] <= self.start[1])

class CanvasElement(ABC):

    def __init__(self) -> None:
        self._initialized: bool = False
        self.parent: CanvasElement | None = None
        # Position on screen
        self.global_position: tuple[int, int] = (0, 0)
        # Positions based on parent's position
        self.position: tuple[int, int] = self.global_position
        self.rect: Rect = Rect.empty()
        self.children: list[CanvasElement] = []
        super().__init__()

    def initialize(self, window: MlxWindow) -> None:
        if (self._initialized):
            return Logger.get().w(
                    "Attempted to initialize an already initialized canvas element."
                    )
        self.window = window
        self._initialized = True

    def add_child(self, child: "CanvasElement"):
        """
        Adds a child to this canvas element
        """
        if (not self._initialized):
            return Logger.get().e("Cannot add child to uninitialized element.")
        self.children.append(child)
        child.parent = self
        child.initialize(self.window)

    def remove_child(self, child: "CanvasElement"):
        """
        Removes a child to this canvas element
        """
        self.children.remove(child)
        child.parent = None

    def draw(self) -> None:
        """
        Draws this canvas element on image.
        expects an image of size, screen size
        """
        for c in self.children:
            c.draw()
        if (not self._initialized):
            return Logger.get().e("Cannot draw an uninitialized element.")
        self._draw()

    @abstractmethod
    def _draw(self) -> None:
        pass

    def is_hovering(self, mouse_pos: tuple[int, int]) -> bool:
        return (self.rect.has_point(mouse_pos))

class Canvas:
    class Anchors(tuple, Enum):
        TOP_LEFT = (0, 0)
        TOP_RIGHT = (1, 0)
        CENTER = (0.5, 0.5)
        BOT_LEFT = (0, 1)
        BOT_RIGHT = (1, 1)

    def __init__(self, window: MlxWindow) -> None:
        self.window = window
        self.children: list[CanvasElement] = []

    def add_child(self, element: CanvasElement) -> None:
        element.initialize(self.window)
        self.children.append(element)

    def render_canvas(self):
        for c in self.children:
            c.draw()
