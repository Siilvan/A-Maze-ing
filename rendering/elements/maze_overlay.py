from ..canvas import CanvasElement, Rect
from ..colors import Colors
from ..maze import CanvasMaze
from ..vector import Vector2
from typing import override
from pathlib import Path
from ..window import MlxImage

IMG_DIR = Path(__file__).resolve().parent / "../static/images/forest"


class MazeOverlay(CanvasElement):
    def __init__(
            self, maze: CanvasMaze,
            solution: list[tuple[int, int]]
            ) -> None:
        super().__init__()
        self.show_solution = False
        self._trail: MlxImage | None = None
        self.update_vars(maze)
        self.set_solution(maze, solution)
        self._trail: MlxImage | None = None

    def update_vars(self, maze: CanvasMaze) -> None:
        new_scale = maze.cell_scale
        new_side = maze.cell_size[0]
        if (self._trail is not None and
            (new_scale != getattr(self, "scale", None) or
             new_side != getattr(self, "side", None))):
            self._trail.destroy(self.window.mlx, self.window.mptr)
            self._trail = None
        self.cell_size = maze.cell_size
        self.side = new_side
        self.scale = new_scale
        self.width = len(maze.grid[0])
        self.height = len(maze.grid)

    def _get_trail(self) -> MlxImage | None:
        if self._trail is None:
            self._trail = MlxImage.from_image(
                self.window.mlx, self.window.mptr,
                str(IMG_DIR / "empty.png"),
                self.scale, Colors.RED,
                round(self.side / 1.8)
            )
        return self._trail

    @override
    def get_rect(self) -> Rect:
        size = Vector2(
            self.width * self.cell_size[0],
            self.height * self.cell_size[1],
        )
        self.rect = Rect(size, self.global_position)
        return self.rect

    def set_solution(self,
                     maze: CanvasMaze,
                     solution: list[tuple[int, int]]
                     ) -> None:
        self.update_vars(maze)
        self.solution = [Vector2.from_tuple(c) for c in solution]

    def draw_solution(self) -> None:
        marker = self._get_trail()
        for step in self.solution[1:-1]:
            pos = Vector2(
                (step.x * self.cell_size[0]) + self.global_position.x,
                (step.y * self.cell_size[1]) + self.global_position.y)
            self.window.put_image(marker, pos.x, pos.y)

    def _draw(self):
        self.get_rect()
        if self.show_solution:
            self.draw_solution()
        else:
            self.clear()

    @override
    def clear(self) -> None:
        if not self.dirty:
            return
        clear = MlxImage.from_image(
            self.window.mlx, self.window.mptr,
            str(IMG_DIR / "empty.png"), self.scale,
            self.window.bg, round(self.side / 1.8))
        for step in self.solution[1:-1]:
            pos = Vector2(
                (step.x * self.cell_size[0]) + self.global_position.x,
                (step.y * self.cell_size[1]) + self.global_position.y)
            self.window.put_image(clear, pos.x, pos.y)
        clear.destroy(self.window.mlx, self.window.mptr)
