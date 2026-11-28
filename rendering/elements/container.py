from ..canvas import CanvasElement, Vector2, Rect


class CanvasContainer(CanvasElement):
    def __init__(
        self, spacing: int = 10, padding: int = 100, vertical: bool = False
    ) -> None:
        self.vertical = vertical
        self.padding = padding
        self.spacing = spacing
        super().__init__()

    def _layout(self) -> Vector2:
        main = self.padding
        cross = 0

        for i, c in enumerate(self.children):
            if i != 0:
                main += self.spacing

            size = c.get_rect().size
            if self.vertical:
                c.position = Vector2(self.padding, main)
                main += size.y
                cross = max(cross, size.x)
            else:
                c.position = Vector2(main, self.padding)
                main += size.x
                cross = max(cross, size.y)

        main += self.padding
        cross += self.padding * 2

        total = Vector2(cross, main) if self.vertical else Vector2(main, cross)
        self.rect = Rect(total, self.global_position)
        return total

    def get_rect(self) -> Rect:
        self._layout()
        return self.rect

    def _pre_draw(self) -> None:
        self._layout()
