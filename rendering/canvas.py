from abc import ABC, abstractmethod
from cmath import rect
from enum import Enum
from turtle import position

from mlx import Mlx

from logger import Logger
from rendering.colors import Colors
from rendering.image import MlxImage
from rendering.vector import Vector2
from rendering.window import MlxWindow

class Rect:
    def __init__(self, size: Vector2, start: Vector2) -> None:
        self.size = size
        self.start = start
        self.end: Vector2 = Vector2(self.start.x + self.size.x, self.start.y + self.size.y)
        pass

    @classmethod
    def empty(cls) -> "Rect":
        """
        Returns a new empty rect
        """
        return Rect(Vector2(0, 0), Vector2(0, 0))

    def has_point(self, point: Vector2) -> bool:
        """
        Returns wether or not the specified point is within the bounds
        of the rect
        """
        return (point.x >= self.start.x and point.x <= self.end.x
            and point.y >= self.start.y and point.y <= self.start.y)

class CanvasElement(ABC):

    def __init__(self) -> None:
        self._initialized: bool = False
        self.parent: CanvasElement | None = None
        # Position on screen
        self.global_position: Vector2 = Vector2(0, 0)
        self.rect: Rect = Rect.empty()
        self.children: list[CanvasElement] = []
        super().__init__()

    @property
    def position(self) -> Vector2:
        if (self.parent is None):
            return self.global_position
        return self.global_position - self.parent.global_position

    @position.setter
    def position(self, p: Vector2):
        if (self.parent is not None):
            self.global_position = self.parent.global_position + p
        else:
            self.global_position = p

    def initialize(self, window: MlxWindow) -> None:
        if (self._initialized):
            return Logger.get().w(
                    "Attempted to initialize an already initialized canvas element."
                    )
        self.window = window
        self._initialized = True
        self._initialize()

    def draw(self, debug: bool = False) -> None:
        """
        Draws this canvas element on image.
        expects an image of size, screen size
        """
        if (not self._initialized):
            return Logger.get().e("Cannot draw an uninitialized element.")
        self._draw()
        if (debug):
            self.draw_rect()

    def draw_rect(self) -> None:
        if (not self._initialized):
            return Logger.get().e("Cannot draw rect of an uninitialized element.")
        image: MlxImage = MlxImage.new_image(self.window.mlx, self.window.mptr,
                                             self.rect.size.x,
                                             self.rect.size.y)
        image.clear_image(Colors.TRANSPARENT)
        for x in range(self.rect.size.x):
            for y in range(self.rect.size.y):
                if (x == 0 or x == self.rect.size.x - 1 or y == 0 or y == self.rect.size.y - 1):
                    image.set_pixel(x, y, Colors.BLACK)
        self.window.put_image(image, self.global_position.x, self.global_position.y)
        image.destroy(self.window.mlx, self.window.mptr)

    def _initialize(self) -> None:
        """
        _initialize method gets called when the child element is added as a child
        """
        pass

    def _draw(self) -> None:
        for c in self.children:
            c.draw()

    def add_child(self, child: "CanvasElement"):
        """
        Adds a child to this canvas element
        """
        if (not self._initialized):
            return Logger.get().e(f"({self})Cannot add child to uninitialized element.")
        child.global_position = self.global_position
        self.children.append(child)
        child.parent = self
        child.initialize(self.window)

    def remove_child(self, child: "CanvasElement"):
        """
        Removes a child to this canvas element
        """
        self.children.remove(child)
        child.parent = None


    def is_hovering(self, mouse_pos: Vector2) -> bool:
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

    def render_canvas(self, debug: bool = False):
        for c in self.children:
            c.draw(debug)
