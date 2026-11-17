from typing import Any, Callable

from mlx import Mlx

from logger import Logger
from rendering.colors import Color, Colors
from rendering.image import MlxImage


logger = Logger.get()

class MlxWindow:
    """
    A window wrapper for the Mlx Library
    """
    def __init__(self) -> None:
        self.mlx = Mlx()
        if (self.mlx is None):
            return logger.e("Failed to get the connection to the x server")
        self.mptr: int = self.mlx.mlx_init()
        logger.i("Successfully initialized window")

    def init_window(self,
                    size: tuple[int, int],
                    bg: Color = Colors.WHITE,
                    name: str = "Window",) -> None:
        """
        Initializes the Mlx window
        """
        self.width: int = size[0]
        self.height: int = size[1]
        self.wptr: int = self.mlx.mlx_new_window(self.mptr, self.width, self.height, name)
        self.bg = bg
        self._setup(bg)

    def hook_mouse_press(self, func: Callable[[int, int, int, None], None]) -> None:
        """
        Hooks the provided function to the mouse press event
        the callback should match the following signature:
        callback(button: int, x: int, y: int)
        """
        self.mlx.mlx_mouse_hook(self.wptr, func, None)

    def hook_loop(self, func: Callable, param: Any = None) -> None:
        """
        Hooks the provided function to the main loop.
        signature must match:
        callback(void)
        """
        self.mlx.mlx_loop_hook(self.mptr, func, param)

    def loop(self) -> None:
        """
        Starts the mlx_loop, without this, the window never draws anything
        """
        self.mlx.mlx_loop(self.mptr)

    def put_image(self, img: MlxImage, x: int, y: int) -> None:
        self.mlx.mlx_put_image_to_window(self.mptr, self.wptr, img.pointer, x, y)

    def _setup(self, bg: Color) -> None:
        """
        Sets up the Mlx Window, puts the screen to white
        """
        self.mlx.mlx_clear_window(self.mptr, self.wptr)
        background: MlxImage = MlxImage.new_image(self.mlx, self.mptr, self.width, self.height)
        background.clear_image(bg)
        self.put_image(background, 0, 0)
        background.destroy(self.mlx, self.mptr)

if __name__ == "__main__":
    logger.w("You're running the wrong file dawg")

