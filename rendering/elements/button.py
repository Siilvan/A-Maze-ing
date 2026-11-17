from typing import Callable, override

from rendering.canvas import CanvasElement, Rect
from rendering.elements.hbox_container import CanvasHBoxContainer
from .text import CanvasText


class CanvasButton(CanvasHBoxContainer):
    def __init__(self, text: CanvasText) -> None:
        self.text = text
        self.hooks: list[Callable] = []
        super().__init__()

    def _initialize(self) -> None:
        self.add_child(self.text)
        return super()._initialize()
