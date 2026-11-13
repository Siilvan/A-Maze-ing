from pathlib import Path

from maze_generator import MazeConfig, RowByRowMazeGenerator
from logger import Logger
from rendering.window import CELL_SCALE, CELL_SIZE, MlxWindow

def load_conf(conf_path: str) -> MazeConfig | None:
    """
    Attempts to load the conf specified by `conf_path`
    returns None on failure. 
    If the specified path does not point to a file, returns a default config.
    """
    p = Path(conf_path)
    if not p.exists():
        Logger.get().w("Specified config path does not exist, using default instead.")
        return MazeConfig()
    try:
        return MazeConfig.from_file(conf_path)
    except MazeConfig.ParseError as e:
        Logger.get().e(f"Parse error on line ({e.line_n}): {e.msg}\n{e.line[:-1]} << HERE")
    return None


def main() -> None:
    conf: MazeConfig | None = load_conf("maze.conf")
    if (conf is None):
        Logger.get().e("Failed to load configuration.")
        return
    generator = RowByRowMazeGenerator(conf)
    generator.generate_maze()
    grid : list[list[int]] = generator.get_maze()
    # grid = [[1, 2, 4, 8]]
    window: MlxWindow = MlxWindow()
    window.init_window((CELL_SIZE * CELL_SCALE * conf.width, CELL_SIZE * CELL_SCALE * conf.height),
                       )
    window.draw_maze(grid)
    window.loop()
    # logger1 = Logger().get()
    # logger2 = Logger().get()
    # print(f"1: {logger1}, 2: {logger2}")

if __name__ == "__main__":
    main()
