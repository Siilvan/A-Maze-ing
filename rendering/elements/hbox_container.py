from typing import override

from rendering.canvas import CanvasElement, Rect
from rendering.vector import Vector2


class CanvasHBoxContainer(CanvasElement):
    def __init__(self, spacing: int = 10) -> None:
        self.spacing = spacing
        super().__init__()

    @override
    def _draw(self) -> None:
        width: int = 0
        height: int = 0
        for i, c in enumerate(self.children):
            if (i != 0 and i < len(self.children)):
                c.position = Vector2(width + self.spacing, c.position.y)
                width += self.spacing
            c.draw()
            width += c.rect.size.x
            height = max(height, c.rect.size.y)
        self.rect = Rect(Vector2(width, height), self.global_position)
        return super()._draw()

