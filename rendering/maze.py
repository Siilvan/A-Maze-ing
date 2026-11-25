from pathlib import Path
import random
import time

from maze_generator.maze_generator import N, E, S, W

from rendering import Colors
from rendering.canvas import CanvasElement, Rect
from maze_generator import Logger, MazeConfig
from rendering.colors import Color
from rendering.image import MlxImage
from rendering.vector import Vector2

CELL_SIZE = 50
CELL_SCALE = 1.5
IMG_DIR = Path(__file__).resolve().parent / "./static/images/forest"


class CanvasMaze(CanvasElement):
    def __init__(
        self,
        grid: list[list[int]],
        maze_config: MazeConfig,
        cell_size: int = CELL_SIZE,
        cell_scale: float = CELL_SCALE,
        maze_solution: list[tuple[int, int]] | None = None,
    ) -> None:
        self.maze_solution: list[Vector2] | None
        if maze_solution is not None:
            self.maze_solution = [Vector2.from_tuple(s) for s in maze_solution]
        else:
            self.maze_solution = None
        self.conf = maze_config
        self.grid = grid
        self.cell_size: tuple[int, int] = (
            round(cell_size * cell_scale),
            round(cell_size * cell_scale),
        )
        self.image_cache: dict[int, MlxImage] = {}
        super().__init__()

    def get_rect(self) -> Rect:
        self.rect = Rect(
            Vector2(
                self.cell_size[1] * len(self.grid[0]),
                self.cell_size[0] * len(self.grid),
            ),
            self.global_position,
        )
        return self.rect

    def _draw(self) -> None:
        """
        Draws the maze on screen, cell by cell
        """
        s = time.perf_counter()
        Logger.get().i("Drawing maze...")
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                cell_image: MlxImage | None = self._get_cell_image(
                    self.grid[y][x], Vector2(x, y)
                )
                if cell_image is None:
                    return Logger.get().e(
                        f"Cell image for cell at pos {x, y} is None!"
                    )
                cell_pos: Vector2 = (
                    Vector2(x * self.cell_size[0], y * self.cell_size[1])
                    + self.global_position
                )
                self.window.put_image(cell_image, cell_pos.x, cell_pos.y)
        self.get_rect()
        end = time.perf_counter()
        self.get_rect()
        Logger.get().i(f"Done! time taken: {end - s:.3}s")

    def _get_cell_image(self, cell: int, cell_pos: Vector2) -> MlxImage | None:
        """
        Creates a new image of a cell, returns the image pointer on success,
        None on failure
        """
        path: str = self._get_cell_image_path(cell, cell_pos)
        fill_color: Color = Colors.TRANSPARENT
        fill_padding: int = 10
        if cell_pos == Vector2.from_tuple(self.conf.entry_pos):
            fill_color = Colors.CYAN
            fill_padding = round(self.cell_size[0] / 2)
        elif cell_pos == Vector2.from_tuple(self.conf.exit_pos):
            fill_color = Colors.LIME
            fill_padding = round(self.cell_size[0] / 2)
        elif self.maze_solution is not None:
            if cell_pos in self.maze_solution:
                fill_color = Colors.RED
                fill_padding = fill_padding = round(self.cell_size[0] / 1.7)
        img: MlxImage | None = MlxImage.from_image(
            self.window.mlx,
            self.window.mptr,
            path,
            scale=CELL_SCALE,
            bg=fill_color,
            bg_padding=fill_padding,
        )
        if img is None:
            Logger.get().e("Failed to generate cell image.")
            return None
        return img

    def _get_cell_image_path(self, cell: int, cell_pos: Vector2) -> str:
        """
        Returns the image path appropriate for the cell `cell`
        """
        if cell == 0:
            return str(IMG_DIR / "empty.png")
        if cell == N + E + S + W:
            return str(IMG_DIR / "north_east_south_west_1.png")
            return str(IMG_DIR / f"full_{random.randint(1, 6)}.png")
        path: list[str] = []
        if cell & N:
            path.append("north")
        if cell & E:
            path.append("east")
        if cell & S:
            path.append("south")
        if cell & W:
            path.append("west")
        if len(path) == 0:
            return str(IMG_DIR / "empty.png")

        return str(IMG_DIR / f"{'_'.join(path)}_{random.randint(1, 7)}.png")


if __name__ == "__main__":
    Logger.get().w("You're running the wrong file dawg")
