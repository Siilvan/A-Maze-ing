from mlx import Mlx

from logger import Logger

logger = Logger.get()

class MlxWindow:
    def __init__(self) -> None:
        self.mlx = Mlx()
        if (self.mlx is None):
            return logger.e("Failed to get the connection to the x server")
        self.mptr: int = self.mlx.mlx_init()
        self.wptr: int = self.mlx.mlx_new_window(self.mptr, 1920, 1080, "A-Maze-Ing!")
        self.setup()
        self.mlx.mlx_loop(self.mptr)

    def tick(self):
        pass

    def setup(self):
        pass

def start_program():
    window: MlxWindow = MlxWindow()

if __name__ == "__main__":
    start_program()

