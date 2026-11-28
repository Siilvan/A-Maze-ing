from ..canvas import CanvasElement, Rect
from ..colors import Colors
from ..maze import CanvasMaze
from .container import CanvasContainer
from .button import CanvasButton
from .path_overlay import PathOverlay
from .settings_menu import CanvasSettings
from .game import GameOverlay
from maze_generator import RowByRowMazeGenerator, MazeConfig


class CanvasMainMenu(CanvasElement):
    def __init__(
            self,
            conf: MazeConfig,
            conf_path: str | None,
            curr_maze: CanvasMaze,
            gen: RowByRowMazeGenerator,
            path_overlay: PathOverlay,
            game_overlay: GameOverlay
            ) -> None:
        self.options: list[str] = [
            "Regenerate",
            "Settings",
            "Show path",
            "Game",
        ]
        self.vbox = CanvasContainer(10, 0, True)
        self.conf = conf
        self.conf_path = conf_path
        self.curr_maze = curr_maze
        self.gen = gen
        self.path_overlay = path_overlay
        self.game_overlay = game_overlay
        super().__init__()

    def get_rect(self) -> Rect:
        self.rect = self.vbox.get_rect()
        return self.rect

    def _draw(self) -> None:
        self.rect = self.get_rect()
        super()._draw()

    def _set_conf_path(self, path: str) -> None:
        self.conf_path = path

    def settings(self) -> None:
        while len(self.vbox.children) > len(self.options):
            self.vbox.remove_child(self.vbox.children[len(self.options)])
            return
        self.settings_window = CanvasSettings(
            self.conf,
            self.conf_path,
            self._set_conf_path)
        self.vbox.add_child(self.settings_window)

    def regenerate(self) -> None:
        self.gen = new_gen = RowByRowMazeGenerator(self.conf)
        new_gen.generate_maze()
        new_gen.write_grid_to_file()
        new_grid = new_gen.get_maze()
        self.curr_maze.set_new_grid(
            new_grid,
            self.window,
            new_gen.logo.pocket_cells())
        self.curr_maze.conf = self.conf
        self.path_overlay.update_vars(self.curr_maze)
        if (self.parent is not None):
            self.parent.dirty_tree()

    def game(self) -> None:
        self.game_overlay.game_start_end()

    def show_path(self) -> None:
        solution = self.gen.get_solution()
        if (solution is None):
            return None
        self.path_overlay.set_solution(self.curr_maze, solution)
        if self.path_overlay.show_solution:
            self.path_overlay.show_solution = False
        else:
            self.path_overlay.show_solution = True
        self.path_overlay.dirty = True

    def _initialize(self) -> None:
        self.add_child(self.vbox)
        for option in self.options:
            self.vbox.add_child(CanvasButton(
                option,
                getattr(self, option.lower().replace(" ", "_")),
                32, Colors.WHITE))
