from pathlib import Path
import random
import time

from logger import Logger
from rendering.image import MlxImage
from rendering.window import MlxWindow


logger = Logger.get()
CELL_SIZE = 16
CELL_SCALE = 3
IMG_DIR = Path(__file__).resolve().parent / "./static/images/"
N, E, S, W = 1, 2, 4, 8

class MazeWindow:
    def __init__(self, grid: list[list[int]], cell_size: int = CELL_SIZE, cell_scale: int = CELL_SCALE) -> None:
        self.grid = grid
        self.window: MlxWindow = MlxWindow()
        self.cell_size: tuple[int, int] = (round(cell_size * cell_scale),
                                           round(cell_size * cell_scale))
        self.window.init_window((self.cell_size[0] * len(grid), self.cell_size[1] * len(grid[0])))
        self.image_cache: dict[int, MlxImage] = {}
        pass

    def draw_maze(self) -> None:
        """
        Draws the maze on screen, cell by cell
        """
        s = time.perf_counter()
        logger.i("Drawing maze...")
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                cell_image: MlxImage | None = self._get_cell_image(self.grid[y][x])
                if (cell_image is None):
                    return logger.e(f"Cell image for cell at pos {x, y} is None!")
                self.window.put_image(cell_image, x * self.cell_size[0], y * self.cell_size[1])
        end = time.perf_counter()
        logger.i(f"Done! time taken: {end - s:.3}s")
        self.window.loop()

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
        logger.i(f"{cell} not cached, creating new image")
        path: str = self._get_cell_image_path(cell)
        img: MlxImage | None = MlxImage.from_image(self.window.mlx, self.window.mptr, path, scale=CELL_SCALE)
        if (img is None):
            return logger.e("Failed to generate cell image.")
        self.image_cache[cell] = img
        return (img)

    def _get_cell_image_path(self, cell: int) -> str:
        """
        Returns the image path appropriate for the cell `cell`
        """
        if (cell == 0):
            return str(IMG_DIR / "empty.png")
        if (cell == N + E + S + W):
            return str(IMG_DIR / f"full_{random.randint(1, 6)}.png")
        path: list[str] = []
        if (cell & N):
            path.append("north")
        if (cell & E):
            path.append("east")
        if (cell & S):
            path.append("south")
        if (cell & W):
            path.append("west")
        return str(IMG_DIR / f"{'_'.join(path)}.png")

if __name__ == "__main__":
    logger.w("You're running the wrong file dawg")
