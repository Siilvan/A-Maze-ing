from ..canvas import CanvasElement, Rect
from ..colors import Colors
from ..maze import CanvasMaze
from ..vector import Vector2
from typing import override
from pathlib import Path
from ..window import MlxImage

IMG_DIR = Path(__file__).resolve().parent / "../static/images/game"


class Player(CanvasElement):
    def __init__(
            self,
            path: str,
            scale: float,
            grid: list[list[int]],
            start_pos: tuple[int, int],
            cell_size: tuple[int, int]
            ) -> None:
        self.path = str(IMG_DIR / path)
        self.player: MlxImage | None = None
        self.grid = grid
        self.pos: Vector2 = Vector2.from_tuple(start_pos)
        self.scale = scale
        self.cell_size = cell_size
        self.erase_img: MlxImage | None = None
        self.prev_pos: Vector2 | None = None
        super().__init__()

    @override
    def get_rect(self):
        if self.player is not None:
            size = Vector2(self.player.width, self.player.height)
        else:
            size = Vector2(0,0)
        self.rect = Rect(size, self.global_position)
        return self.rect

    @override
    def _draw(self) -> None:
        self.get_img()
        if self.prev_pos is not None:
            self.erase_at(self.prev_pos)
            self.prev_pos = None
        self.window.put_image(self.player, self.global_position.x, self.global_position.y)
        self.dirty = False

    def get_img(self) -> None:
        if self.player is None:
            self.player = MlxImage.from_image(
                self.window.mlx,
                self.window.mptr,
                self.path,
                self.scale
            )

    def erase_at(self, pos: Vector2) -> None:
        if self.erase_img is None:
            self.get_img()
            assert self.player is not None
            self.erase_img = MlxImage.new_image(
                self.window.mlx, self.window.mptr,
                self.player.width, self.player.height
            )
            self.erase_img.clear_image(self.window.bg)
        self.window.put_image(self.erase_img, pos.x, pos.y)

    def erase_me(self) -> None:
        if self.prev_pos is not None:
            self.erase_at(self.prev_pos)
            self.prev_pos = None
        self.erase_at(self.global_position)
    
    def _initialize(self) -> None:
        self.get_img()

    def get_open_paths(self) -> set[int]:
        cell_val = self.grid[self.pos.y][self.pos.x]
        paths: set[int] = set()
        i = 0
        while i < 4:
            if not cell_val & 1:
                paths.add(i)
            i += 1
            cell_val >>= 1
        return paths

    def take_step(self, dir: int) -> Vector2:
        open_paths = self.get_open_paths()
        if dir not in open_paths:
            return self.pos
        move_amount = self.cell_size[0]
        self.prev_pos = Vector2(self.global_position.x, self.global_position.y)
        if dir == 0:
            self.global_position.y -= move_amount
            self.pos.y -= 1
        elif dir == 1:
            self.global_position.x += move_amount
            self.pos.x += 1
        elif dir == 2:
            self.global_position.y += move_amount
            self.pos.y += 1
        elif dir == 3:
            self.global_position.x -= move_amount
            self.pos.x -= 1
        self.dirty = True
        return self.pos