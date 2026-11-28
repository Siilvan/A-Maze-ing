from pathlib import Path
import sys

from maze_generator import (
    MazeConfig, RowByRowMazeGenerator,
    MazeSizeException, MazeGenerationException, ManualExit,
    Logger)
from rendering import (
    CanvasMaze, CanvasMainMenu, MlxWindow, Canvas, Colors,
    CanvasContainer, PathOverlay
)


def load_conf(conf_path: str) -> MazeConfig | None:
    """
    Attempts to load the conf specified by `conf_path`
    returns None on failure.
    If the specified path does not point to a file, returns a default config.
    """
    p = Path(conf_path)
    if not p.exists():
        Logger.get().w(
            "Specified config path does not exist."
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
    try:
        if (len(sys.argv) < 2):
            raise Exception()
        else:
            conf = load_conf(sys.argv[1])
            conf_path = sys.argv[1]
    except Exception:
        Logger.get().e("No config specified.")
    if (conf is None):
        Logger.get().e("Failed to load configuration.")
        return
    try:
        generator = RowByRowMazeGenerator(conf)
        generator.generate_maze()
    except ManualExit as e:
        Logger.get().e(f"{e}")
    grid: list[list[int]] = generator.get_maze()
    generator.write_grid_to_file()
    window: MlxWindow = MlxWindow()
    window.init_window((2560, 1440), Colors.DARK_GRAY, "A-Maze-Ing!")
    canvas: Canvas = Canvas(window)
    container = CanvasContainer(100, 100)
    canvas.add_child(container)
    solution: list[tuple[int, int]] | None = generator.get_solution()
    if (solution is None):
        Logger.get().e("Failed to solve maze.")

    maze: CanvasMaze = CanvasMaze(grid, conf, window)
    overlay = PathOverlay(maze, solution)
    menu = CanvasMainMenu(conf, conf_path, maze, generator, overlay)
    container.add_child(maze)
    container.add_child(menu)
    canvas.add_child(overlay)
    overlay.global_position = maze.rect.start
    print(maze.rect)
    canvas.render_canvas()
    window.loop()


if __name__ == "__main__":
    main()
