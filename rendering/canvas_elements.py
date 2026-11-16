from pathlib import Path

from PIL import Image, ImageFont
from typing import Callable, override

from logger import Logger
from rendering.image import MlxImage

from .canvas import CanvasElement

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
    _char_table: dict[str, MlxImage] = {}
    FONT_DIR: Path = Path(__file__).resolve().parent / "./static/fonts/"

    def __init__(self, text: str, character_spacing: int = 12) -> None:
        self.text = text
        self.character_spacing = character_spacing
        super().__init__()

    @override
    def _draw(self) -> None:
        for i, c in enumerate(self.text):
            image: MlxImage | None = self.get_char_image(c)
            if (image is None):
                continue
            self.window.put_image(image,
                                  self.position[0] + (i * self.character_spacing),
                                  self.position[1])
        return super()._draw()

    def get_char_image(self, char: str, point_size: int = 12) -> MlxImage | None:
        if (len(char) != 1):
            return logger.e("CanvasText: Passed parameter is not a char!")
        if (char in CanvasText._char_table):
            return CanvasText._char_table[char]
        logger.i(f"No character image for char '{char}', generating and caching it.")
        font: ImageFont.FreeTypeFont = ImageFont.truetype(CanvasText.FONT_DIR /
                                                          "Roboto-Regular.ttf", point_size)
        im = Image.Image()._new(font.getmask(char, start=(10, 10)))
        im_path: str = f"/tmp/PILtemp_{ord(char)}.png" 
        im.save(im_path)
        mlx_image: MlxImage | None = MlxImage.from_image(self.window.mlx, self.window.mptr, im_path)
        if (mlx_image is not None):
            CanvasText._char_table[char] = mlx_image
            logger.i(f"Successfully generated and cached image for char '{char}'")
            return mlx_image
        logger.e(f"Failed to generate image for char '{char}'")
