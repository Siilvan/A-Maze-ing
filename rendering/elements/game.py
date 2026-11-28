from ..canvas import CanvasElement, Rect, Canvas
from ..colors import Colors
from ..maze import CanvasMaze
from ..vector import Vector2
from typing import override
from pathlib import Path
from ..window import MlxImage
from .player import Player

IMG_DIR = Path(__file__).resolve().parent / "../static/images/game"
PLAYER_IMG_SIZE = Vector2(3850, 3850)
EXIT_IMG_SIZE = Vector2(200, 200)

class GameOverlay(CanvasElement):
    def __init__(
            self,
            maze: CanvasMaze,
            canvas: Canvas
            ) -> None:
        super().__init__()
        self.show_solution = False
        self._goal: MlxImage | None = None
        self.is_active = False
        self.maze = maze
        self.conf = maze.conf
        self.scale = maze.cell_scale
        self.cell_size = maze.cell_size
        self.canvas = canvas
        self.player_scale = (maze.cell_size[0] / PLAYER_IMG_SIZE.x) / 2
        self.goal_scale = (maze.cell_size[0] / EXIT_IMG_SIZE.x) / 2
        self.width = len(maze.grid[0])
        self.height = len(maze.grid)
        self.image_side = maze.image_side

    @override
    def _on_key_press(self, button: int):
        if not self.is_active:
            return
        if button == 65362:
            self.move_player(0)
        elif button == 65363:
            self.move_player(1)
        elif button == 65364:
            self.move_player(2)
        elif button == 65361:
            self.move_player(3)

    @override
    def get_rect(self) -> Rect:
        size = Vector2(
            self.width * self.cell_size[0],
            self.height * self.cell_size[1],
        )
        self.rect = Rect(size, self.global_position)
        return self.rect

    def _cell_origin(self, cell: tuple[int, int]) -> Vector2:
        return Vector2(
            cell[0] * self.cell_size[0] + self.global_position.x,
            cell[1] * self.cell_size[1] + self.global_position.y,
        )

    def _centered_pos(self, cell: tuple[int, int], img_size: Vector2, scale: float) -> Vector2:
        origin = self._cell_origin(cell)
        w = round(img_size.x * scale)
        h = round(img_size.y * scale)
        return Vector2(
            origin.x + (self.image_side - w) // 2,
            origin.y + (self.image_side - h) // 2
        )

    def _get_goal(self) -> MlxImage | None:
        if self._goal is None:
            self._goal = MlxImage.from_image(
                self.window.mlx,
                self.window.mptr,
                str(IMG_DIR / "dogg.jpeg"),
                self.goal_scale
            )
        return self._goal
    
    def start_game(self) -> None:
        self.player = Player(
            "john_deliverer.jpg",
            self.player_scale,
            self.maze.grid,
            self.conf.entry_pos,
            self.cell_size
            )
        self.add_child(self.player)
        self.player.global_position = self._centered_pos(
            self.conf.entry_pos, PLAYER_IMG_SIZE,
            self.player_scale,
            )
        
        goal = self._get_goal()
        self.g_pos = self._centered_pos(self.conf.exit_pos, EXIT_IMG_SIZE, self.goal_scale)
        self.window.put_image(goal, self.g_pos.x , self.g_pos.y)
        # do stuff before game start
        self.player.dirty = True
        self.dirty = True
        self.is_active = True

    def end_game(self) -> None:
        self.player.erase_me()
        self.remove_child(self.player)
        self._goal.clear_image(self.window.bg)
        self.window.put_image(self._goal, self.g_pos.x, self.g_pos.y)
        self._goal.destroy(self.window.mlx, self.window.mptr)
        self._goal = None
        self.is_active = False
        self.maze.draw_entry_exit()

    def game_start_end(self) -> None:
        if not self.is_active:
            self.start_game()
        else:
            self.end_game()

    def move_player(self, dir: int) -> None:
        new_pos = self.player.take_step(dir)
        if new_pos == Vector2.from_tuple(self.conf.exit_pos):
            self.end_game()