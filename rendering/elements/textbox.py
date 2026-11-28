from typing import override

from PIL import Image, ImageDraw

from maze_generator import Logger
from rendering.canvas import CanvasElement, Rect
from rendering.colors import Color, Colors
from ..image import MlxImage
from rendering.vector import Vector2
from .text import get_font, measure_text

SHIFT_MAP = {
    44: "<",
    46: ">",
    47: "?",
    48: ")",
    49: "!",
    57: "(",
    59: ":",
    61: "+",
    91: "{",
    93: "}",
    96: "~",
}

logger = Logger.get()


class CanvasTextBox(CanvasElement):
    def __init__(
        self, text: str, font_size: int = 12, color: Color = Colors.BLACK,
        bg_color: Color = Colors.WHITE
    ) -> None:
        self.text = text
        self.font_size = font_size
        self.color = color
        self.bg_color = bg_color
        self.focused = False
        self.shift_held = False
        super().__init__()

    @property
    def display_text(self) -> str:
        return f"'{self.text}'"

    @override
    def _draw(self) -> None:
        image: MlxImage | None = self._get_string_image(self.display_text)
        if image is None:
            logger.e(f"Failed to generate image for string '{self.text}'")
            return
        self.get_rect()
        self.window.put_image(
            image, self.global_position.x, self.global_position.y
        )
        return super()._draw()

    def get_rect(self) -> Rect:
        width, height = measure_text(self.display_text, self.font_size)
        self.rect = Rect(Vector2(width, height), self.global_position)
        return self.rect

    def _get_string_image(self, string: str) -> MlxImage | None:
        font = get_font(self.font_size)
        width, height = measure_text(string, self.font_size)
        ascent, _ = font.getmetrics()
        im = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(im)
        if self.text and self.focused:
            idx = len(self.text)
            x0 = round(font.getlength(string[:idx]))
            x1 = round(font.getlength(string[:idx + 1]))
            draw.rectangle(
                (x0, 0, x1 - 1, height - 1),
                fill=self.bg_color.to_tuple(),
            )
        draw.text(
            (0, ascent - font.getbbox(string)[3]),
            string,
            font=font,
            fill=self.color.to_tuple(),
        )
        im_path: str = "/tmp/PILtemp.png"
        im.save(im_path)
        return MlxImage.from_image(self.window.mlx, self.window.mptr, im_path)

    def key_press(self, button: int, fil: None = None) -> None:
        if button in (65505, 65506):
            self.shift_held = True
            return
        if not self.focused:
            return
        if button == 65293:
            self.dirty = True
            self.focused = False
        elif button == 65288:
            self.text = self.text[:-1]
            self.dirty = True
        elif 32 <= button <= 126:
            if button in SHIFT_MAP and self.shift_held:
                char = SHIFT_MAP[button]
            else:
                char = chr(button)
            self.text += char
            self.dirty = True

    def key_release(self, button: int, fil: None = None) -> None:
        if button in (65505, 65506):
            self.shift_held = False

    def _on_mouse_press(self, button: int, pos: Vector2) -> None:
        hit = self.get_rect().has_point(pos)
        if self.focused != hit:
            self.dirty = True
        self.focused = hit
        if self.focused:
            self.window.mlx.mlx_hook(
                self.window.wptr, 2, 1, self.key_press, None
            )
            self.window.mlx.mlx_hook(
                self.window.wptr, 3, 2, self.key_release, None
            )
