
from pathlib import Path
from typing import override
import uuid

from PIL import Image, ImageDraw, ImageFont

from maze_generator import Logger
from rendering.canvas import CanvasElement, Rect
from rendering.colors import Color, Colors
from ..image import MlxImage
from . import CanvasText
from rendering.vector import Vector2

SHIFT_MAP = {
    44: '<', 46: '>', 47: '?', 48: ')', 49: '!', 57: '(',
    59: ':', 61: '+', 91: '{', 93: '}', 96: '~',
}

logger = Logger.get()

class CanvasTextBox(CanvasElement):
    FONT_DIR: Path = Path(__file__).resolve().parent / "../static/fonts/"

    def __init__(self, text: str, font_size: int = 12, color: Color = Colors.BLACK) -> None:
        self.text = text
        self.font_size = font_size
        self.color = color
        self.focused = False
        self.shift_held = False
        super().__init__()

    @override
    def _draw(self) -> None:
        image: MlxImage | None = self._get_string_image(f"'{self.text}'")
        if (image is None):
            logger.e(f"Failed to generate image for string '{self.text}'")
            return
        self.rect = Rect(Vector2(image.width, image.height), self.global_position)
        self.window.put_image(image, self.global_position.x, self.global_position.y)
        return super()._draw()

    def get_rect(self) -> Rect:
        image: MlxImage | None = self._get_string_image(f"'{self.text}'")
        if (image is None):
            logger.e(f"Failed to generate image for string '{self.text}'")
            raise RuntimeError
        self.rect = Rect(Vector2(image.width, image.height), self.global_position)
        return self.rect
        
    def _get_string_image(self, string: str) -> MlxImage | None:
        font: ImageFont.FreeTypeFont = ImageFont.truetype(CanvasText.FONT_DIR /
                                                          "Roboto-Regular.ttf", self.font_size)
        ascent, descent = font.getmetrics()
        height: int = ascent + descent
        advance: float = font.getlength(string)
        width: int = max(1, round(advance))
        im = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(im)
        draw.text((0, ascent - font.getbbox(string)[3]), string,
                      font=font, fill=self.color.to_tuple())
        im_path: str = f"/tmp/PILtemp.png" 
        im.save(im_path)
        return MlxImage.from_image(self.window.mlx, self.window.mptr, im_path)

    def key_press(self, button: int, fil = None):
        if button in (65505, 65506):
            self.shift_held = True
            return
        if not self.focused:
            return   
        if button == 65293:
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

    def key_release(self, button: int, fil=None):
        if button in (65505, 65506):
            self.shift_held = False

    def _on_mouse_press(self, button, pos):
        self.focused = self.rect.has_point(pos)
        if self.focused:
            self.window.mlx.mlx_hook(self.window.wptr, 2, 1, self.key_press, None)
            self.window.mlx.mlx_hook(self.window.wptr, 3, 2, self.key_release, None)
