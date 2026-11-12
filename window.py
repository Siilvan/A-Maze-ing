from enum import Enum, auto
import time

from maze_generator import MazeConfig, MazeGenerator, RowByRowMazeGenerator
from mlx import Mlx

from logger import Logger

logger = Logger.get()
N, E, S, W = 1, 2, 4, 8


class ImageData:
    """
    Class to store the data of an image from the mlx_get_data_addr call
    """
    def __init__(self, pixels: memoryview, bppixels: int, sizeline: int, iformat: int) -> None:
        self.pixels = pixels
        self.bppixels = bppixels
        self.sizeline = sizeline
        self.iformat = iformat

    @classmethod
    def from_ptr(cls, mlx: Mlx, iptr: int) -> "ImageData":
        """
        Returns a new ImageData object from image at the specified
        pointer
        """
        (p, bpp, sl, f) = mlx.mlx_get_data_addr(iptr) 
        return ImageData(
                pixels=p,
                bppixels=bpp,
                sizeline=sl,
                iformat=f)

class Color:
    def __init__(self, r: int, g: int, b: int, a: int = 255) -> None:
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def to_int(self) -> int:
        return (self.a << 24) | (self.r << 16) | (self.g << 8) | self.b

    def to_bytes(self, cformat: int = 0) -> bytes:
        if (cformat == 0):
            return bytes([self.b, self.g, self.r, self.a])
        else:
            return bytes([self.a, self.r, self.g, self.b])

class MlxWindow:
    def __init__(self) -> None:
        self.mlx = Mlx()
        self.cell_size: tuple[int, int] = (50, 50)
        if (self.mlx is None):
            return logger.e("Failed to get the connection to the x server")
        self.mptr: int = self.mlx.mlx_init()
        self.wptr: int = self.mlx.mlx_new_window(self.mptr, 1920, 1080, "A-Maze-Ing!")
        self.setup()
        logger.i("Successfully initialized window")

    def setup(self) -> None:
        self.mlx.mlx_clear_window(self.mptr, self.wptr)

    def loop(self) -> None:
        self.mlx.mlx_loop(self.mptr)

    def draw_maze(self, grid: list[list[int]]) -> None:
        s = time.time()
        logger.i("Drawing maze...")
        for x in range(len(grid) - 1):
            for y in range(len(grid[x]) - 1):
                cell_image: int | None = self._get_cell_image(grid[x][y])
                if (cell_image is None):
                    return logger.e(f"Cell image for cell at pos {x, y} is None!")
                self._put_image(cell_image, x * self.cell_size[0], y * self.cell_size[1])
        end = time.time()
        logger.i(f"Done! time taken: {end - s:.3}s")

    def _put_image(self, iptr: int, x: int, y: int) -> None:
        self.mlx.mlx_put_image_to_window(self.mptr, self.wptr, iptr, x, y)

    def _get_cell_image(self, cell: int) -> int | None:
        """
        Creates a new image of a cell, returns the image pointer on success,
        None on failure
        """
        iptr: int | None = self.mlx.mlx_new_image(self.mptr, self.cell_size[0], self.cell_size[1])
        if (iptr is None):
            return logger.e(f"Failed to get image for cell")
        data: ImageData = ImageData.from_ptr(self.mlx, iptr)
        for x in range(self.cell_size[0]):
            for y in range(self.cell_size[1]):
                if cell & N and y == 0:
                    set_image_pixel(data, x, y, Color(255, 0, 0))
                if cell & S and y == self.cell_size[1]:
                    set_image_pixel(data, x, y, Color(255, 0, 0))
                if cell & W and x == 0:
                    set_image_pixel(data, x, y, Color(255, 0, 0))
                if cell & E and x == self.cell_size[0]:
                    set_image_pixel(data, x, y, Color(255, 0, 0))
        return (iptr)


def set_image_pixel(image: ImageData, x: int, y: int, color: Color):
    offset = y * image.sizeline + x * (image.bppixels // 8)
    image.pixels[offset: offset + 4] = color.to_bytes(cformat=image.iformat)

if __name__ == "__main__":
    logger.w("You're running the wrong file dawg")

