from pathlib import Path
import random
import time

from maze_generator.maze_generator import N, E, S, W

from rendering import Colors
from rendering.canvas import CanvasElement, Rect
from maze_generator import Logger, MazeConfig
from rendering.colors import Color
from rendering.image import MlxImage
from rendering.window import MlxWindow
from rendering.vector import Vector2

CELL_SIZE = 50
REAL_CELL_SIZE = 70
CELL_SCALE = 1.5
IMG_DIR = Path(__file__).resolve().parent / "./static/images/forest"


class CanvasMaze(CanvasElement):
    def __init__(self, grid: list[list[int]],
                 maze_config: MazeConfig,
                 window: MlxWindow,
                 enclosed: set[tuple[int, int]]
                 ) -> None:
        self.conf = maze_config
        self.image_cache: dict[tuple, MlxImage] = {}
        self.set_new_grid(grid, window, enclosed)
        super().__init__()

    def get_rect(self) -> Rect:
        rows, cols = len(self.grid), len(self.grid[0])
        self.rect = Rect(
            Vector2(
                self.cell_size[0] * (cols - 1) + self.image_side,
                self.cell_size[0] * (rows - 1) + self.image_side,
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
                self.draw_cell(x, y)
        end = time.perf_counter()
        self.get_rect()
        Logger.get().i(f"Done! time taken: {end - s:.3}s")

    def draw_cell(self, x: int, y: int) -> None:
        img = self._get_cell_image(self.grid[y][x], Vector2(x, y))
        if img is None:
            return Logger.get().e(
                f"Cell image for cell at pos {x, y} is None!"
                )
        pos = (
            Vector2(x * self.cell_size[0], y * self.cell_size[1])
            + self.global_position
            )
        self.window.put_image(img, pos.x, pos.y)

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
        key = (path, fill_color, fill_padding)
        img = self.image_cache.get(key)
        if img is None:
            img = MlxImage.from_image(
                self.window.mlx, self.window.mptr,
                path, scale=self.cell_scale, bg=fill_color,
                bg_padding=fill_padding)
            if (img is None):
                Logger.get().e("Failed to generate cell image.")
                return None
            self.image_cache[key] = img
        return img

    def _get_cell_image_path(self, cell: int, cell_pos: Vector2) -> str:
        """
        Returns the image path appropriate for the cell `cell`
        """
        if cell == 0:
            return str(IMG_DIR / "empty.png")
        if (cell == N + E + S + W):
            if (cell_pos.y, cell_pos.x) in self.enclosed:
                return str(IMG_DIR / "north_east_south_west_1.png")
            return str(IMG_DIR / "north_east_south_west_2.png")
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

    def draw_entry_exit(self) -> None:
        self.draw_cell(*self.conf.entry_pos)
        self.draw_cell(*self.conf.exit_pos)

    def clear_image_cache(self) -> None:
        for img in self.image_cache.values():
            img.destroy(self.window.mlx, self.window.mptr)
        self.image_cache.clear()

    def set_new_grid(
            self,
            grid: list[list[int]],
            window: MlxWindow,
            enclosed: set[tuple[int, int]]) -> None:
        self.clear_image_cache()
        self.grid = grid
        self.enclosed = enclosed
        maze_space = Vector2(window.width - 700, window.height - 200)
        rows, cols = len(grid), len(grid[0])
        scale = min(
            maze_space.x / (CELL_SIZE * (cols - 1) + REAL_CELL_SIZE),
            maze_space.y / (CELL_SIZE * (rows - 1) + REAL_CELL_SIZE)
            )
        side = round(CELL_SIZE * scale)
        self.cell_scale = scale
        self.cell_size = (side, side)
        self.image_side = round(REAL_CELL_SIZE * scale)


if __name__ == "__main__":
    Logger.get().w("You're running the wrong file dawg")
