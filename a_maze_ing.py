from pathlib import Path

from maze_generator import MazeConfig, RowByRowMazeGenerator, errors
from solver import SolverBot
from logger import Logger
from rendering.window import CELL_SCALE, CELL_SIZE, MlxWindow
import stupid_claude_draw_test_func as d
import time

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
    window: MlxWindow = MlxWindow()
    window.init_window((CELL_SIZE * CELL_SCALE * conf.width, CELL_SIZE * CELL_SCALE * conf.height),
                       )
    window.draw_maze(grid)
    window.loop()

    # logger1 = Logger().get()
    # logger2 = Logger().get()
    # print(f"1: {logger1}, 2: {logger2}")
    # d.draw_maze(generator.get_maze())
    # solver = SolverBot(grid, conf)
    # start = time.time()
    # res = solver.solve(True)
    # end_time = time.time()
    # print(f"time: {end_time - start}\n result: {res} \n len: {len(res)}")
    # start = time.time()
    # res = solver.solve(False)
    # end_time = time.time()
    # print(f"time: {end_time - start}\n result: {res} \n len: {len(res)}")
    

if __name__ == "__main__":
    main()
