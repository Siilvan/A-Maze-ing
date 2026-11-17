from pathlib import Path
import uuid

from PIL import Image, ImageFont, ImageDraw
from typing import Callable, override

from logger import Logger
from rendering.colors import Color, Colors
from rendering.image import MlxImage

from .canvas import CanvasElement, Rect

logger = Logger.get()

class CanvasButton(CanvasElement):
    def __init__(self, text: str = "") -> None:
        self.text = text
        self.hooks: list[Callable] = []
        super().__init__()

    @override
    def _draw(self) -> None:
        return super()._draw()

class CanvasText(CanvasElement):
    FONT_DIR: Path = Path(__file__).resolve().parent / "./static/fonts/"

    def __init__(self, text: str, font_size: int = 12, color: Color = Colors.BLACK) -> None:
        self.text = text
        self.font_size = font_size
        self.color = color
        super().__init__()

    @override
    def _draw(self) -> None:
        image: MlxImage | None = self.get_string_image(self.text)
        if (image is None):
            logger.e(f"Failed to generate image for string '{self.text}'")
            return
        self.rect = Rect((image.width, image.height), self.global_position)
        self.window.put_image(image, self.global_position[0], self.global_position[1])
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
        im_path: str = f"/tmp/PILtemp_{uuid.uuid1()}.png" 
        im.save(im_path)
        return MlxImage.from_image(self.window.mlx, self.window.mptr, im_path)

