import time
from typing import override

from rendering.canvas import CanvasElement, Rect
from rendering.vector import Vector2


class CanvasHBoxContainer(CanvasElement):
    def __init__(self, spacing: int = 10, padding: int = 100) -> None:
        self.padding = padding
        self.spacing = spacing
        self.timer: float = time.perf_counter()
        super().__init__()

    def _tick(self) -> None:
        now = time.perf_counter()
        print(time.perf_counter() - now)
        self.timer = now

    @override
    def _on_mouse_press(self, button: int, pos: Vector2) -> None:
        if (self.rect.has_point(pos)):
            print(f"Pressed in me!")

    def get_rect(self) -> Rect:
        width: int = self.padding
        height: int = self.padding
        for i, c in enumerate(self.children):
            c.position = Vector2(width, self.padding)
            if (i != 0 and i < len(self.children)):
                c.position = Vector2(c.position.x + self.spacing, c.position.y)
                width += self.spacing
            rect: Rect = c.get_rect()
            width += rect.size.x
            height = max(height, rect.size.y + self.padding)
        width += self.padding
        height += self.padding
        self.rect = Rect(Vector2(width, height), self.global_position)
        return self.rect

    @override
    def _draw(self) -> None:
        width: int = self.padding
        height: int = self.padding
        for i, c in enumerate(self.children):
            c.position = Vector2(width, self.padding)
            if (i != 0 and i < len(self.children)):
                c.position = Vector2(c.position.x + self.spacing, c.position.y)
                width += self.spacing
            c.draw()
            width += c.rect.size.x
            height = max(height, c.rect.size.y + self.padding)
        width += self.padding
        height += self.padding
        self.rect = Rect(Vector2(width, height), self.global_position)
