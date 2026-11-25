from pathlib import Path
import sys

from maze_generator import (
    MazeConfig,
    RowByRowMazeGenerator,
    MazeSizeException,
    MazeGenerationException,
    ManualExit,
    Logger,
)
from rendering.canvas import Canvas
from rendering import Colors
from rendering.elements import (
    CanvasMaze,
)
from rendering.window import MlxWindow


def load_conf(conf_path: str) -> MazeConfig | None:
    """
    Attempts to load the conf specified by `conf_path`
    returns None on failure.
    If the specified path does not point to a file,
    returns a default config.
    """
    p = Path(conf_path)
    if not p.exists():
        Logger.get().w(
            "Specified config path does not exist,"
            + "using default values instead."
        )
        return MazeConfig()
    try:
        return MazeConfig.from_file(conf_path)
    except MazeConfig.ParseError as e:
        Logger.get().e(
            f"Parse error: {e.msg}\n\n\t{e.line_n}: {e.line[:-1]} << HERE\n"
        )
    except MazeSizeException as e:
        Logger.get().e(f"{e}")
    except MazeGenerationException as e:
        Logger.get().e(f"{e}")
    except ManualExit as e:
        Logger.get().e(f"{e}")
    return None


class ConfigPath:
    path: str

    @classmethod
    def set_path(cls, path: str) -> None:
        cls.path = path


def main() -> None:
    conf: MazeConfig | None = None
    if len(sys.argv) < 2:
        Logger.get().w("No config specified, using default values instead.")
        conf = MazeConfig()
    else:
        conf = load_conf(sys.argv[1])
    if conf is None:
        Logger.get().e("Failed to load configuration.")
        return
    generator = RowByRowMazeGenerator(conf)
    try:
        generator.generate_maze()
    except ManualExit as e:
        Logger.get().e(f"{e}")
    grid: list[list[int]] = generator.get_maze()
    generator.write_grid_to_file()
    window: MlxWindow = MlxWindow()
    window.init_window((1920, 1080), Colors.DARK_GRAY, "A-Maze-Ing!")
    canvas: Canvas = Canvas(window)
    solution: list[tuple[int, int]] | None = generator.get_solution()
    if solution is None:
        Logger.get().e("Failed to solve maze.")
    maze: CanvasMaze = CanvasMaze(grid, conf, maze_solution=solution)
    canvas.add_child(maze)
    canvas.render_canvas(True)
    window.loop()


if __name__ == "__main__":
    main()
