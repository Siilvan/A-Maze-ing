from typing import Callable, override

from rendering.canvas import CanvasElement
from .text import CanvasText


class CanvasButton(CanvasElement):
    def __init__(self, text: CanvasText) -> None:
        self.text = text
        self.hooks: list[Callable] = []
        super().__init__()

    def _initialize(self) -> None:
        self.add_child(self.text)
        return super()._initialize()

    @override
    def _draw(self) -> None:
        return super()._draw()

