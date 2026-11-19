from pathlib import Path
import time

from maze_generator import (
    MazeConfig, RowByRowMazeGenerator,
    MazeSizeException, MazeGenerationException, ManualExit,
    Logger, SolverBot)
from rendering.canvas import Canvas
from rendering import Colors, MazeWindow
from rendering.elements.hbox_container import CanvasHBoxContainer
from rendering.elements.text import CanvasText
from rendering.vector import Vector2
from rendering.window import MlxWindow

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
    except MazeSizeException as e:
        Logger.get().e(f"{e}")
    except MazeGenerationException as e:
        Logger.get().e(f"{e}")
    except ManualExit as e:
        Logger.get().e(f"{e}")
    return None


def main_loop(delta: float, c: Canvas) -> None:
    c.clear_canvas()
    c.tick()
    c.render_canvas()

def main() -> None:
    conf: MazeConfig | None = load_conf("maze.conf")
    if (conf is None):
        Logger.get().e("Failed to load configuration.")
        return
    generator = RowByRowMazeGenerator(conf)
    generator.generate_maze()
    grid : list[list[int]] = generator.get_maze()
    window: MazeWindow = MazeWindow(grid)
    window.draw_maze()
    # window: MlxWindow = MlxWindow()
    # window.init_window((1920, 1080), Colors.DARK_GRAY, "Hello")
    # canvas: Canvas = Canvas(window)
    # container: CanvasHBoxContainer = CanvasHBoxContainer(60, 24)
    # container.global_position += Vector2(100, 100)
    # canvas.add_child(container)
    # for i in range(10):
    #     label: CanvasText = CanvasText(f"H{i}lo", 24, Colors.FOREST_GREEN)
    #     container.add_child(label)
    # i = 0
    window.loop()


if __name__ == "__main__":
    main()
