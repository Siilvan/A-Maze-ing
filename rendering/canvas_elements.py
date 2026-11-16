from typing import Callable

from .canvas import CanvasElement


class CanvasButton(CanvasElement):
    def __init__(self, text: str = "") -> None:
        self.text = text
        self.hooks: list[Callable] = []
        super().__init__()

    def _draw(self) -> None:
        return super()._draw()
