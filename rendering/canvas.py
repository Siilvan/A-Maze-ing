from abc import ABC, abstractmethod
from enum import Enum
from typing import Callable

from maze_generator import Logger, ManualExit
from rendering.colors import Colors
from rendering.image import MlxImage
from rendering.vector import Vector2
from rendering.window import MlxWindow


class Rect:
    def __init__(self, size: Vector2, start: Vector2) -> None:
        self.size = size
        self.start = start
        self.end: Vector2 = Vector2(
            self.start.x + self.size.x, self.start.y + self.size.y
        )
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
        return point >= self.start and point <= self.end

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f"Rect(size={self.size}, start={self.start}, end={self.end})"


class CanvasElement(ABC):

    def __init__(self) -> None:
        self._initialized: bool = False
        self.parent: CanvasElement | None = None
        self._dirty: bool = True
        # Position on screen
        self._global_position: Vector2 = Vector2(0, 0)
        self.rect: Rect = Rect.empty()
        self.children: list[CanvasElement] = []
        super().__init__()

    @property
    def dirty(self) -> bool:
        return self._dirty

    @dirty.setter
    def dirty(self, value: bool) -> None:
        self._dirty = value

    @property
    def global_position(self) -> Vector2:
        return self._global_position

    @global_position.setter
    def global_position(self, a: Vector2) -> None:
        if a != self._global_position:
            delta = a - self._global_position
            self._global_position = a
            self.dirty = True
            for c in self.children:
                c.global_position = c.global_position + delta

    @property
    def position(self) -> Vector2:
        if self.parent is None:
            return self.global_position
        return self.global_position - self.parent.global_position

    @position.setter
    def position(self, p: Vector2):
        if self.parent is not None:
            self.global_position = self.parent.global_position + p
        else:
            self.global_position = p

    def initialize(self, window: MlxWindow) -> None:
        if self._initialized:
            return Logger.get().w(
                "Attempted to initialize an" +
                "already initialized canvas element."
            )
        self.window = window
        self._initialized = True
        self._initialize()

    def dirty_tree(self) -> None:
        self.dirty = True
        for c in self.children:
            c.dirty_tree()

    def draw(self, debug: bool = False) -> None:
        """
        Draws this canvas element on image.
        expects an image of size, screen size
        """
        if not self._initialized:
            return Logger.get().e("Cannot draw an uninitialized element.")
        if self.dirty:
            self._pre_draw()
            self._draw()
            self.dirty = False
        for c in self.children:
            c.draw()
        if debug:
            self.draw_rect()

    def clear(self) -> None:
        if self.rect.size == Vector2(0, 0):
            return
        for c in self.children:
            c.clear()
        if not self.dirty:
            return
        image: MlxImage = MlxImage.new_image(
            self.window.mlx,
            self.window.mptr,
            self.rect.size.x,
            self.rect.size.y,
        )
        image.clear_image(self.window.bg)
        self.window.put_image(
            image, self.global_position.x, self.global_position.y
        )
        image.destroy(self.window.mlx, self.window.mptr)

    def tick(self) -> None:
        """
        Gets called every frame, do not override.
        """
        self._tick()
        for c in self.children:
            c.tick()

    @abstractmethod
    def get_rect(self) -> Rect:
        """
        Returns the rect of that item. If possible, try to avoid
        using this method, and draw the item instead;
        as this (in most cases) does all the steps of drawing
        the item, but just doesn't.
        """
        ...

    def on_mouse_press(self, button: int, pos: Vector2) -> None:
        self._on_mouse_press(button, pos)
        for c in self.children:
            c.on_mouse_press(button, pos)

    def on_key_press(self, button: int) -> None:
        self._on_key_press(button)
        for c in self.children:
            c.on_key_press(button)

    def draw_rect(self) -> None:
        """
        Draws the borders of this object. Used for debug purposes
        """
        if not self._initialized:
            return Logger.get().e(
                "Cannot draw rect of an uninitialized element."
            )
        image: MlxImage = MlxImage.new_image(
            self.window.mlx,
            self.window.mptr,
            self.rect.size.x,
            self.rect.size.y,
        )
        image.clear_image(Colors.TRANSPARENT)
        for x in range(self.rect.size.x):
            for y in range(self.rect.size.y):
                if (
                    x == 0
                    or x == self.rect.size.x - 1
                    or y == 0
                    or y == self.rect.size.y - 1
                ):
                    image.set_pixel(x, y, Colors.BLACK)
        self.window.put_image(
            image, self.global_position.x, self.global_position.y
        )
        image.destroy(self.window.mlx, self.window.mptr)

    def _on_key_press(self, button: int) -> None:
        """
        On key press
        """
        return

    def _on_mouse_press(self, button: int, pos: Vector2) -> None:
        """
        Handles mouse presses with `button` being the button, and `pos`
        the position of the cursor
        """
        return

    def _initialize(self) -> None:
        """
        _initialize method gets called when the child element is added
        as a child
        """
        return

    def _pre_draw(self) -> None:
        pass

    def _draw(self) -> None:
        """
        Renders this object on screen
        """
        for c in self.children:
            c.draw()

    def _tick(self) -> None:
        """
        Gets called every frame
        """
        return

    def add_child(self, child: "CanvasElement"):
        """
        Adds a child to this canvas element
        """
        if not self._initialized:
            return Logger.get().e(
                f"({self})Cannot add child to uninitialized element."
            )
        child.global_position = self.global_position
        self.children.append(child)
        child.parent = self
        child.initialize(self.window)
        self._pre_draw()

    def remove_child(self, child: "CanvasElement"):
        """
        Removes a child to this canvas element
        """
        self.children.remove(child)
        child.dirty = True
        child.clear()
        child.parent = None

    def is_hovering(self, mouse_pos: Vector2) -> bool:
        return self.rect.has_point(mouse_pos)


class Canvas:
    class Anchors(tuple, Enum):
        TOP_LEFT = (0, 0)
        TOP_RIGHT = (1, 0)
        CENTER = (0.5, 0.5)
        BOT_LEFT = (0, 1)
        BOT_RIGHT = (1, 1)

    def __init__(
        self, window: MlxWindow, main: Callable | None = None
    ) -> None:
        self.window = window
        self.main = main
        self.children: list[CanvasElement] = []
        self.delta: float = 0
        self.window.hook_mouse_press(self._catch_mouse_press)
        self.window.hook_loop(self.process_loop, None)
        self.window.hook_key_press(self._catch_key_press)
        self.window.mlx.mlx_hook(
            self.window.wptr,
            33,
            131072,
            lambda param: self.close_window(param),
            self.window.mptr,
        )

    def process_loop(self, _p: None):
        self.clear_canvas()
        self.render_canvas()
        # now = time.perf_counter()
        # if (self.main is not None):
        #     self.main(now - self.delta, self)
        # self.tick()
        # self.delta = now

    def tick(self) -> None:
        for c in self.children:
            c.tick()

    def _catch_mouse_press(self, button: int, x: int, y: int, _p: None):
        try:
            for c in self.children:
                c.on_mouse_press(button, Vector2(x, y))
        except ManualExit as e:
            Logger.get().e(f"{e}")
            self.close_window(self.window.mptr)

    def _catch_key_press(self, key: int, _p: None):
        for c in self.children:
            c.on_key_press(key)

    def close_window(self, mptr: int) -> None:
        self.window.mlx.mlx_loop_exit(mptr)
        Logger.get().i("Window got closed successfully!")
        return

    def get_mouse_pos(self) -> Vector2:
        pos: tuple[int, int, int] = self.window.mlx.mlx_mouse_get_pos(
            self.window.mptr
        )
        return Vector2(pos[1], pos[2])

    def add_child(self, element: CanvasElement) -> None:
        element.initialize(self.window)
        self.children.append(element)

    def clear_canvas(self) -> None:
        for c in self.children:
            c.clear()

    def render_canvas(self, debug: bool = False):
        for c in self.children:
            c.draw(debug)
