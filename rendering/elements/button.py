
from pathlib import Path
from typing import override
from typing import Callable
from PIL import Image, ImageDraw, ImageFont

from maze_generator import Logger
from rendering.canvas import CanvasElement, Rect
from rendering.colors import Color, Colors
from ..image import MlxImage
from . import CanvasText
from rendering.vector import Vector2

logger = Logger.get()

class CanvasButton(CanvasElement):
    FONT_DIR: Path = Path(__file__).resolve().parent / "../static/fonts/"

    def __init__(self, text: str,
                 callback: Callable[[], None],
                 font_size: int = 12,
                 color: Color = Colors.BLACK,
                 ) -> None:
        self.text = text
        self.callback = callback
        self.font_size = font_size
        self.color = color
        super().__init__()

    @override
    def _draw(self) -> None:
        image: MlxImage | None = self.get_string_image(self.text)
        if (image is None):
            logger.e(f"Failed to generate image for string '{self.text}'")
            return
        self.rect = Rect(Vector2(image.width, image.height), self.global_position)
        self.window.put_image(image, self.global_position.x, self.global_position.y)
        return super()._draw()

    def get_string_image(self, string: str) -> MlxImage | None:
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

    @override
    def _on_mouse_press(self, button: int, pos: Vector2) -> None:
        if button == 1 and self.is_hovering(pos):
            self.callback()
