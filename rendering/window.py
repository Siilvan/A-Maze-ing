from enum import Enum, auto
from pathlib import Path
import random
import time
from mlx import Mlx

from .colors import Color, Colors
from .image import MlxImage
from logger import Logger

logger = Logger.get()
IMG_DIR = Path(__file__).resolve().parent / "./images/"
CELL_SIZE = 16
CELL_SCALE = 2
N, E, S, W = 1, 2, 4, 8

class MlxWindow:
    """
    A window wrapper for the Mlx Library
    """
    def __init__(self, background_color: Color = Colors.WHITE, name: str = "A-Maze-Ing!") -> None:
        self.mlx = Mlx()
        self.cell_size: tuple[int, int] = (round(CELL_SIZE * CELL_SCALE),
                                           round(CELL_SIZE * CELL_SCALE))
        if (self.mlx is None):
            return logger.e("Failed to get the connection to the x server")
        self.width: int = 1920
        self.height: int = 1080
        self.mptr: int = self.mlx.mlx_init()
        self.image_cache: dict[int, MlxImage] = {}
        self.wptr: int = self.mlx.mlx_new_window(self.mptr, self.width, self.height, name)
        self.setup(background_color)
        logger.i("Successfully initialized window")

    def setup(self, bg: Color) -> None:
        """
        Sets up the Mlx Window, puts the screen to white
        """
        self.mlx.mlx_clear_window(self.mptr, self.wptr)
        background: MlxImage = MlxImage.new_image(self.mlx, self.mptr, self.width, self.height)
        background.clear_image(bg)
        self._put_image(background, 0, 0)
        background.destroy(self.mlx, self.mptr)

    def loop(self) -> None:
        """
        Starts the mlx_loop, without this, the window never draws anything
        """
        self.mlx.mlx_loop(self.mptr)

    def draw_maze(self, grid: list[list[int]]) -> None:
        """
        Draws the maze on screen, cell by cell
        """
        s = time.perf_counter()
        logger.i("Drawing maze...")
        for y in range(len(grid)):
            for x in range(len(grid[y])):
                cell_image: MlxImage | None = self._get_cell_image(grid[y][x])
                if (cell_image is None):
                    return logger.e(f"Cell image for cell at pos {x, y} is None!")
                self._put_image(cell_image, x * self.cell_size[0], y * self.cell_size[1])
        end = time.perf_counter()
        logger.i(f"Done! time taken: {end - s:.3}s")

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
        # logger.i(f"{cell} not cached, creating new image")
        path: str = self._get_cell_image_path(cell)
        img: MlxImage = MlxImage.from_image(self.mlx, self.mptr, path, scale=CELL_SCALE)
        self.image_cache[cell] = img
        return (img)

    def _get_cell_image_path(self, cell: int) -> str:
        """
        Returns the image path appropriate for the cell `cell`
        """
        if (cell == 0):
            return str(IMG_DIR / "empty.png")
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

    def _put_image(self, img: MlxImage, x: int, y: int) -> None:
        self.mlx.mlx_put_image_to_window(self.mptr, self.wptr, img.pointer, x, y)

if __name__ == "__main__":
    logger.w("You're running the wrong file dawg")

