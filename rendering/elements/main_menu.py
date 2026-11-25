from ..canvas import CanvasElement, Rect
from ..colors import Colors
from ..maze import CanvasMaze
from .container import CanvasBoxContainer
from .button import CanvasButton
from maze_generator import RowByRowMazeGenerator, MazeConfig, Logger
from .settings_window import CanvasSettings
from ..vector import Vector2
from typing import override

class CanvasMainMenu(CanvasElement):
    def __init__(self, conf: MazeConfig, conf_path: str, curr_maze: CanvasMaze) -> None:
        self.options: list[str] = [
            "Regenerate",
            "Settings",
            "Get seed",
            "Bonus",
        ]
        self.vbox = CanvasBoxContainer(10, 0, True)
        self.conf = conf
        self.conf_path = conf_path
        self.curr_maze = curr_maze
        super().__init__()

    def get_rect(self) -> Rect:
        # self.rect = self.vbox.get_rect()
        # return self.rect
        return self.vbox.get_rect()

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
        self.settings_window = CanvasSettings(self.conf, self.conf_path)
        self.vbox.add_child(self.settings_window)

    def regenerate(self) -> None:
        try:
            self.conf = MazeConfig().from_file(self.conf_path   )
        except Exception as e:
            Logger.get().e(f"{e}")
            return
        new_gen = RowByRowMazeGenerator(self.conf)
        new_gen.generate_maze()
        new_grid = new_gen.get_maze()
        self.curr_maze.grid = new_grid
        self.parent.dirty_tree()
        # self.curr_maze.dirty = True
        print(f"{self.curr_maze.rect.size}\n{self.rect.size}")

    def get_seed(self):
        pass

    def bonus(self):
        pass

    def _initialize(self) -> None:
        self.add_child(self.vbox)
        for option in self.options:
            self.vbox.add_child(CanvasButton(
                option,
                getattr(self, option.lower().replace(" ", "_")),
                30, Colors.LIGHT_GRAY))
