from enum import Enum
import random

class Color:
    def __init__(self, r: int, g: int, b: int, a: int = 255) -> None:
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    @classmethod
    def random(cls) -> "Color":
        return Color(
                r=random.randint(0, 255),
                g=random.randint(0, 255),
                b=random.randint(0, 255),
                a=random.randint(0, 255),
                )

    def to_int(self) -> int:
        return (self.a << 24) | (self.r << 16) | (self.g << 8) | self.b

    def to_bytes(self, cformat: int = 0) -> bytes:
        if (cformat == 0):
            return bytes([self.b, self.g, self.r, self.a])
        else:
            return bytes([self.a, self.r, self.g, self.b])

class Colors(Color, Enum):
    # Basics
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GRAY = (128, 128, 128)
    LIGHT_GRAY = (211, 211, 211)
    DARK_GRAY = (64, 64, 64)

    # Primary s
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)

    # Secondary s
    YELLOW = (255, 255, 0)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)

    # Warm s
    ORANGE = (255, 140, 0)
    CORAL = (255, 127, 80)
    SALMON = (250, 128, 114)
    GOLD = (255, 215, 0)
    PINK = (255, 105, 180)

    # Cool s
    PURPLE = (128, 0, 128)
    VIOLET = (138, 43, 226)
    INDIGO = (75, 0, 130)
    TEAL = (0, 128, 128)
    TURQUOISE = (64, 224, 208)
    SKY_BLUE = (135, 206, 235)
    NAVY = (0, 0, 128)

    # Greens
    LIME = (50, 205, 50)
    FOREST_GREEN = (34, 139, 34)
    MINT = (152, 255, 152)
    OLIVE = (128, 128, 0)

    # Pastels
    LAVENDER = (230, 230, 250)
    BABY_BLUE = (173, 216, 230)
    PEACH = (255, 218, 185)
    MINT_CREAM = (245, 255, 250)
    ROSE = (255, 228, 225)

    # Earth tones
    BROWN = (139, 69, 19)
    TAN = (210, 180, 140)
    BEIGE = (245, 245, 220)
    CHOCOLATE = (210, 105, 30)
