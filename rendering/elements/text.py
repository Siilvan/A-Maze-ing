from pathlib import Path
from typing import override
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFont

from maze_generator import Logger
from rendering.canvas import CanvasElement, Rect
from rendering.colors import Color, Colors
from rendering.image import MlxImage
from rendering.vector import Vector2

logger = Logger.get()
FONT_PATH = Path(__file__).resolve().parent / "../static/fonts/rainyhearts.ttf"


@lru_cache(maxsize=None)
def get_font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_PATH, size)


@lru_cache(maxsize=4096)
def measure_text(string: str, size: int) -> tuple[int, int]:
    font = get_font(size)
    ascent, descent = font.getmetrics()
    return max(1, round(font.getlength(string))), ascent + descent


class CanvasText(CanvasElement):
    def __init__(
        self, text: str, font_size: int = 12, color: Color = Colors.BLACK
    ) -> None:
        self.text = text
        self.font_size = font_size
        self.color = color
        super().__init__()

    def get_rect(self) -> Rect:
        width, height = measure_text(self.text, self.font_size)
        self.rect = Rect(Vector2(width, height), self.global_position)
        return self.rect

    @override
    def _draw(self) -> None:
        image: MlxImage | None = self._get_string_image(self.text)
        if image is None:
            logger.e(f"Failed to generate image for string '{self.text}'")
            return
        self.get_rect()
        self.window.put_image(
            image, self.global_position.x, self.global_position.y
        )

    def _get_string_image(self, string: str) -> MlxImage | None:
        font = get_font(self.font_size)
        width, height = measure_text(string, self.font_size)
        ascent, _ = font.getmetrics()
        im = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(im)
        draw.text(
            (0, ascent - font.getbbox(string)[3]),
            string,
            font=font,
            fill=self.color.to_tuple(),
        )
        im_path: str = "/tmp/PILtemp.png"
        im.save(im_path)
        return MlxImage.from_image(self.window.mlx, self.window.mptr, im_path)
