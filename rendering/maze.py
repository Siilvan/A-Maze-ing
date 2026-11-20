from pathlib import Path
import random
import time

from rendering.canvas import CanvasElement, Rect
from maze_generator import Logger
from rendering.image import MlxImage
from rendering.vector import Vector2
from rendering.window import MlxWindow

CELL_SIZE = 70
CELL_SCALE = 1
IMG_DIR = Path(__file__).resolve().parent / "./static/images/forest"
N, E, S, W = 1, 2, 4, 8

class CanvasMaze(CanvasElement):
    def __init__(self, grid: list[list[int]], cell_size: int = CELL_SIZE, cell_scale: int = CELL_SCALE) -> None:
        self.grid = grid
        self.cell_size: tuple[int, int] = (round(cell_size * cell_scale),
                                           round(cell_size * cell_scale))
        self.image_cache: dict[int, MlxImage] = {}
        super().__init__()

    def get_rect(self) -> Rect:
        self.rect = Rect(
                Vector2(self.cell_size[1] * len(self.grid[0]),
                        self.cell_size[0] * len(self.grid)),
                self.global_position)
        return (self.rect)

    def _draw(self) -> None:
        """
        Draws the maze on screen, cell by cell
        """
        s = time.perf_counter()
        Logger.get().i("Drawing maze...")
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                cell_image: MlxImage | None = self._get_cell_image(self.grid[y][x])
                if (cell_image is None):
                    return Logger.get().e(f"Cell image for cell at pos {x, y} is None!")
                cell_pos: Vector2 = Vector2(x * self.cell_size[0],
                                            y * self.cell_size[1]) + self.global_position
                self.window.put_image(cell_image, cell_pos.x, cell_pos.y)
        end = time.perf_counter()
        self.get_rect()
        Logger.get().i(f"Done! time taken: {end - s:.3}s")

    def _get_cell_image(self, cell: int) -> MlxImage | None:
        """
        Creates a new image of a cell, returns the image pointer on success,
        None on failure
        """
        # Caching doesn't work and I have no idea why
        # Uncomment these lines to enable it
        #
        # if (cell in self.image_cache):
        #     return self.image_cache[cell]
        # Logger.get().i(f"{cell} not cached, creating new image")
        path: str = self._get_cell_image_path(cell)
        img: MlxImage | None = MlxImage.from_image(self.window.mlx, self.window.mptr, path, scale=CELL_SCALE)
        if (img is None):
            return Logger.get().e("Failed to generate cell image.")
        self.image_cache[cell] = img
        return (img)

    def _get_cell_image_path(self, cell: int) -> str:
        """
        Returns the image path appropriate for the cell `cell`
        """
        if (cell == 0):
            return str(IMG_DIR / "empty.png")
        if (cell == N + E + S + W):
            return str(IMG_DIR / f"north_east_south_west_1.png")
            # return str(IMG_DIR / f"full_{random.randint(1, 6)}.png")
        path: list[str] = []
        if (cell & N):
            path.append("north")
        if (cell & E):
            path.append("east")
        if (cell & S):
            path.append("south")
        if (cell & W):
            path.append("west")
        return str(IMG_DIR / f"{'_'.join(path)}_{random.randint(1, 7)}.png")

if __name__ == "__main__":
    Logger.get().w("You're running the wrong file dawg")