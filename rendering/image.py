from pathlib import Path

from mlx import Mlx
from PIL import Image, ImageFont

from logger import Logger
from rendering.colors import Color, Colors

class MlxImage:
    """
    Class to store an Mlx image
    """
    def __init__(self, pixels: memoryview,
                 bppixels: int,
                 sizeline: int,
                 iformat: int,
                 width: int, 
                 height: int,
                 pointer: int) -> None:
        self.pixels: memoryview = pixels
        self.bppixels: int = bppixels
        self.sizeline: int = sizeline
        self.iformat: int = iformat
        self.width: int = width
        self.height: int = height
        self.pointer: int = pointer

    @classmethod
    def new_image(cls, mlx: Mlx, mlxptr: int, width: int, height: int) -> "MlxImage":
        """
        Returns a new ImageData object from image at the specified
        pointer
        """
        ptr: int | None = mlx.mlx_new_image(mlxptr, width, height)
        if ptr == None:
            raise RuntimeError("Unexpected error, failed to create an image.")
        (p, bpp, sl, f) = mlx.mlx_get_data_addr(ptr) 
        return MlxImage(
                pixels=p,
                bppixels=bpp,
                sizeline=sl,
                iformat=f,
                width=width,
                height=height,
                pointer=ptr
                )

    @classmethod
    def from_image(cls, mlx: Mlx, mlxptr: int, image_path: str, scale: float = 1) -> "MlxImage | None":
        """
        Creates a new MlxImage instance from an existing image
        """
        path = Path(image_path)
        if (not path.exists() or not path.is_file()):
            return Logger.get().e(f"Failed to create image: no file at path '{image_path}'.")
        if (path.suffix == '.png'):
            (ptr, width, height) = mlx.mlx_png_file_to_image(mlxptr, image_path)
        elif (path.suffix == '.xpm'):
            (ptr, width, height) = mlx.mlx_xpm_file_to_image(mlxptr, image_path)
        else:
            return Logger.get().e(
                    f"Failed to create image: ({image_path}) unknown file extension '{path.suffix}'."
                    )
        if (ptr is None):
            return Logger.get().e(f"Failed to create image: ptr is None.")
        (p, bpp, sl, f) = mlx.mlx_get_data_addr(ptr) 
        return MlxImage(
                pixels=p,
                bppixels=bpp,
                sizeline=sl,
                iformat=f,
                width=width,
                height=height,
                pointer=ptr,
                )
    
    def destroy(self, mlx: Mlx, mptr: int) -> None:
        """
        frees the memory associated with the image.
        Renders this image unusable.
        """
        mlx.mlx_destroy_image(mptr, self.pointer)

    def set_pixel(self, x: int, y: int, color: Color):
        """
        Sets the pixel at pos x, y of an image
        """
        offset = y * self.sizeline + x * (self.bppixels // 8)
        self.pixels[offset: offset + 4] = color.to_bytes(cformat=self.iformat)

    def clear_image(self, color: Color = Colors.BLACK):
        """
        Sets all the pixels of an image to one color
        """
        for x in range(self.width):
            for y in range(self.height):
                self.set_pixel( x, y, color)
