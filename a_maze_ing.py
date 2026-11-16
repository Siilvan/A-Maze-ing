from pathlib import Path

from maze_generator import MazeConfig, RowByRowMazeGenerator
from logger import Logger
from rendering import MlxWindow, CELL_SCALE, CELL_SIZE

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
    window: MlxWindow = MlxWindow()
    window.init_window((CELL_SIZE * CELL_SCALE * conf.width,
                        CELL_SIZE * CELL_SCALE * conf.height))
    window.draw_maze(grid)
    window.loop()

if __name__ == "__main__":
    main()
