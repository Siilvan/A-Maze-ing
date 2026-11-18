# IF YOUR NOT SILVAN PLEASE DONT TOUCH THIS FILE
from pathlib import Path

from maze_generator import MazeConfig
from logger import Logger
from rendering.canvas import Canvas, Colors, Vector2, MlxWindow
from rendering import SettingsWindow

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


def main_loop() -> None:
    print("F")

def main() -> None:
    conf_path = "maze.conf"
    conf: MazeConfig | None = load_conf(conf_path)
    if (conf is None):
        Logger.get().e("Failed to load configuration.")
        return
    window: MlxWindow = MlxWindow()
    window.init_window((2560, 1440), Colors.DARK_GRAY, "The a-Maze-ing Maze")
    canvas: Canvas = Canvas(window)
    settings = SettingsWindow(conf, canvas, conf_path)
    settings.draw_settings()
    # container: CanvasTextBox = CanvasTextBox(f"Hello", 24, Colors.FOREST_GREEN)
    # container.global_position += Vector2(100, 100)
    # canvas.add_child(container)
    window.loop()


if __name__ == "__main__":
    main()
