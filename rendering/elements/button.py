from pathlib import Path
from typing import override
from typing import Callable

from maze_generator import Logger
from rendering.canvas import CanvasElement, Rect
from rendering.colors import Color, Colors
from .text import CanvasText
from .container import CanvasContainer
from rendering.vector import Vector2

logger = Logger.get()


class CanvasButton(CanvasElement):
    FONT_DIR: Path = Path(__file__).resolve().parent / "../static/fonts/"

    def __init__(
        self,
        text: str,
        callback: Callable[[], None],
        font_size: int = 12,
        color: Color = Colors.BLACK,
    ) -> None:
        self.text = text
        self.callback = callback
        self.font_size = font_size
        self.color = color
        self.container = CanvasContainer(30, 0, False)
        super().__init__()

    def get_rect(self) -> Rect:
        self.rect = self.container.get_rect()
        return self.rect

    @override
    def _draw(self) -> None:
        self.rect = self.get_rect()
        super()._draw()

    def _initialize(self) -> None:
        self.add_child(self.container)
        self.hover_arrow = CanvasText("<", self.font_size, self.window.bg)
        self.container.add_child(
            CanvasText(self.text, self.font_size, self.color)
            )
        self.container.add_child(self.hover_arrow)

    @override
    def _on_mouse_press(self, button: int, pos: Vector2) -> None:
        if button == 1 and self.is_hovering(pos):
            self.callback()

    @override
    def _on_hover_enter(self):
        self.hover_arrow.color = self.color
        self.hover_arrow.dirty = True

    @override
    def _on_hover_exit(self):
        self.hover_arrow.color = self.window.bg
        self.hover_arrow.dirty = True
