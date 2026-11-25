class Vector2:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def __add__(self, other: "Vector2 | int") -> "Vector2":
        if isinstance(other, int):
            return Vector2(self.x + other, self.y + other)
        if isinstance(other, Vector2):
            return Vector2(self.x + other.x, self.y + other.y)
        raise TypeError("Cannot add vector2 to given type")

    def __sub__(self, other: "Vector2") -> "Vector2":
        if not isinstance(other, Vector2):
            raise TypeError("Second argument is not a vector.")
        return Vector2(self.x - other.x, self.y - other.y)

    def __eq__(self, value: object, /) -> bool:
        if not isinstance(value, Vector2):
            raise TypeError("Second argument is not a vector.")
        return self.x == value.x and self.y == value.y

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Vector2):
            raise TypeError("Second argument is not a vector.")
        return self.x < other.x and self.y < other.y

    def __le__(self, other: object) -> bool:
        if not isinstance(other, Vector2):
            raise TypeError("Second argument is not a vector.")
        return self.x <= other.x and self.y <= other.y

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, Vector2):
            raise TypeError("Second argument is not a vector.")
        return self.x > other.x and self.y > other.y

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, Vector2):
            raise TypeError("Second argument is not a vector.")
        return self.x >= other.x and self.y >= other.y

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    @classmethod
    def from_tuple(cls, t: tuple[int, int]) -> "Vector2":
        return cls(t[0], t[1])
