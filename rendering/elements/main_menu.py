from ..canvas import CanvasElement, Rect, Canvas
from ..colors import Colors
from ..maze import CanvasMaze
from .container import CanvasBoxContainer
from .button import CanvasButton
from .maze_overlay import MazeOverlay
from maze_generator import RowByRowMazeGenerator, MazeConfig, Logger
from .settings_window import CanvasSettings
from typing import override

class CanvasMainMenu(CanvasElement):
    def __init__(self, conf: MazeConfig,
                 conf_path: str,
                 curr_maze: CanvasMaze,
                 gen: RowByRowMazeGenerator,
                 overlay: MazeOverlay) -> None:
        self.options: list[str] = [
            "Regenerate",
            "Settings",
            "Show path",
            "Get seed",
            "Bonus",
        ]
        self.vbox = CanvasBoxContainer(10, 0, True)
        self.conf = conf
        self.conf_path = conf_path
        self.curr_maze = curr_maze
        self.gen = gen
        self.overlay = overlay
        super().__init__()

    def get_rect(self) -> Rect:
        self.rect = self.vbox.get_rect()
        return self.rect

    def _draw(self) -> None:
        self.rect = self.get_rect()
        super()._draw()

    def settings(self) -> None:
        # if len(self.parent.children) > 2:
        #     self.parent.remove_child(self.parent.children[2])
        # self.settings_window = CanvasSettings(self.conf, self.conf_path)
        # self.parent.add_child(self.settings_window)
        while len(self.vbox.children) > len(self.options):
            self.vbox.remove_child(self.vbox.children[len(self.options)])
            return
        self.settings_window = CanvasSettings(self.conf, self.conf_path)
        self.vbox.add_child(self.settings_window)

    def regenerate(self) -> None:
        try:
            self.conf = MazeConfig().from_file(self.conf_path)
        except Exception as e:
            Logger.get().e(f"{e}")
            return
        self.gen = new_gen = RowByRowMazeGenerator(self.conf)
        new_gen.generate_maze()
        new_gen.write_grid_to_file()
        new_grid = new_gen.get_maze()
        solution: list[tuple[int, int]] | None = new_gen.get_solution()
        if (solution is None):
            Logger.get().e("Failed to solve maze.")
        self.curr_maze.set_new_grid(new_grid, self.window)
        self.curr_maze.conf = self.conf
        self.curr_maze.set_new_solution(solution)
        self.parent.dirty_tree()

    def get_seed(self):
        pass

    def bonus(self):
        pass

    def show_path(self):
        solution = self.gen.get_solution()
        self.overlay.set_solution(self.curr_maze, solution)
        if self.overlay.show_solution:
            self.overlay.show_solution = False
        else:
            self.overlay.show_solution = True
        self.overlay.dirty = True

    def _initialize(self) -> None:
        self.add_child(self.vbox)
        for option in self.options:
            self.vbox.add_child(CanvasButton(
                option,
                getattr(self, option.lower().replace(" ", "_")),
                30, Colors.LIGHT_GRAY))
