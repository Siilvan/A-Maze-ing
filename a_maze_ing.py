from pathlib import Path

from maze_generator import MazeConfig, RowByRowMazeGenerator, errors
from solver import SolverBot
from logger import Logger
from rendering.canvas import Canvas
from rendering.canvas_elements import CanvasText
from rendering.colors import Colors
from rendering.maze_window import MazeWindow
from rendering.window import MlxWindow
from rendering import SettingsWindow
from typing import Any

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
    try:
        generator.generate_maze()
    except errors.ManualExit as e:
        print(f"{e} hw")
    grid : list[list[int]] = generator.get_maze()
    # window: MazeWindow = MazeWindow(grid)
    # window.draw_maze()
    window: MlxWindow = MlxWindow()
    window.init_window((2560, 1440), Colors.DARK_GRAY, "The A-Maze-ing Maze")
    canvas: Canvas = Canvas(window)
    # label: CanvasText = CanvasText("This is so a-Maze-ing", 60, Colors.FOREST_GREEN)
    # label.global_position = (100, 0)
    # canvas.add_child(label)
    # canvas.render_canvas()
    settings = SettingsWindow(conf, canvas)
    settings.draw_settings()
    window.loop()


if __name__ == "__main__":
    main()
