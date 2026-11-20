from ..canvas import CanvasElement, Rect
from ..colors import Colors
from ..maze import CanvasMaze
from .container import CanvasBoxContainer
from .button import CanvasButton
from maze_generator import RowByRowMazeGenerator, MazeConfig, ManualExit
from typing import override

class CanvasMainMenu(CanvasElement):
    def __init__(self, conf: MazeConfig, curr_maze: CanvasMaze) -> None:
        self.options: list[str] = [
            "Regenerate",
            "Settings",
            "Get seed",
            "Bonus",
        ]
        self.vbox = CanvasBoxContainer(10, 0, True)
        self.conf = conf
        self.curr_maze = curr_maze
        super().__init__()

    def get_rect(self) -> Rect:
        return self.vbox.get_rect()

    def _draw(self) -> None:
        self.rect = self.get_rect()
        super()._draw()

    def settings(self):
        print("settings")

    def regenerate(self):
        new_gen = RowByRowMazeGenerator(self.conf)
        try:
            print("AAAAAAAAAAAAAAAAAAAAA")
            new_gen.generate_maze()
        except ManualExit as e:
            print(f"{e}")
        new_grid = new_gen.get_maze()
        self.curr_maze.dirty = True
        self.curr_maze.grid = new_grid

    def get_seed(self):
        print("ew, i dont wanna give you my seed")

    def bonus(self):
        print("Super cool bonus that will definetly exist")

    @override
    def _initialize(self) -> None:
        self.add_child(self.vbox)
        for option in self.options:
            self.vbox.add_child(CanvasButton(
                option,
                getattr(self, option.lower().replace(" ", "_")),
                30, Colors.LIGHT_GRAY))


            
