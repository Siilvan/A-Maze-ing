from mlx import Mlx
from PIL import Image

from rendering.colors import Color, Colors


class MlxImage:
    """
    Class to store the data of an image from the mlx_get_data_addr call
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
    def from_image(cls, mlx: Mlx, mlxprt: int, image_path: str, scale: float = 1) -> "MlxImage":
        """
        Creates a new MlxImage instance from an existing image
        """
        pimg = Image.open(image_path).convert("RGBA")
        if scale != 1:
            width = round(pimg.width * scale)
            height = round(pimg.height * scale)
            pimg = pimg.resize((width, height), Image.Resampling.NEAREST)
        width, height = pimg.size
        image = MlxImage.new_image(mlx, mlxprt, width, height)
        src = pimg.tobytes()
        for y in range(height):
            src_start = y * width * 4
            dst_start = y * image.sizeline
            row = bytearray(src[src_start:src_start + width * 4])
            for x in range(width):
                i = x * 4
                if image.iformat == 0:
                    # RGBA -> BGRA (little endian)
                    row[i], row[i + 2] = row[i + 2], row[i]
                else:
                    # RGBA -> ARGB (big endian)
                    row[i:i+4] = row[i+3:i+4] + row[i:i+3]
            image.pixels[dst_start:dst_start + width * 4] = row
        return image
    
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
