from .config import MazeConfig
from . import errors
from collections import deque

CHARS: dict[str, list[str]] = {
    '0': ["##.", "#.#", "#.#", "#.#", ".##"],
    '1': ["##.", ".#.", ".#.", ".#.", "###"],
    '2': ["###", "..#", "###", "#..", "###"],
    '3': ["###", "..#", "###", "..#", "###"],
    '4': ["#..", "#..", "###", "..#", "..#"],
    '5': ["###", "#..", "###", "..#", "##."],
    '6': ["###", "#..", "###", "#.#", "###"],
    '7': ["###", "..#", ".##", ".#.", ".#."],
    '8': ["###", "#.#", "###", "#.#", "###"],
    '9': ["###", "#.#", "###", "..#", "###"],
    ' ': ["...", "...", "...", "...", "..."],
    'A': [".#.", "#.#", "###", "#.#", "#.#"],
    'B': ["##.", "#.#", "##.", "#.#", "##."],
    'C': [".##", "#..", "#..", "#..", ".##"],
    'D': ["##.", "#.#", "#.#", "#.#", "##."],
    'E': ["###", "#..", "###", "#..", "###"],
    'F': ["###", "#..", "###", "#..", "#.."],
    'G': ["###", "#..", "#.#", "#.#", "###"],
    'H': ["#.#", "#.#", "###", "#.#", "#.#"],
    'I': ["###", ".#.", ".#.", ".#.", "###"],
    'J': ["..#", "..#", "..#", "#.#", "###"],
    'K': ["#.#", "#.#", "##.", "#.#", "#.#"],
    'L': ["#..", "#..", "#..", "#..", "###"],
    'M': ["#.#", "###", "###", "#.#", "#.#"],
    'N': ["##.", "#.#", "#.#", "#.#", "#.#"],
    'O': ["###", "#.#", "#.#", "#.#", "###"],
    'P': ["###", "#.#", "###", "#..", "#.."],
    'Q': ["###", "#.#", "#.#", "###", "..#"],
    'R': ["###", "#.#", "##.", "#.#", "#.#"],
    'S': ["###", "#..", "###", "..#", "###"],
    'T': ["###", ".#.", ".#.", ".#.", ".#."],
    'U': ["#.#", "#.#", "#.#", "#.#", "###"],
    'V': ["#.#", "#.#", "#.#", "#.#", ".#."],
    'W': ["#.#", "#.#", "#.#", "###", "#.#"],
    'X': ["#.#", "#.#", ".#.", "#.#", "#.#"],
    'Y': ["#.#", "#.#", ".#.", ".#.", ".#."],
    'Z': ["###", "..#", ".#.", "#..", "###"],
    ':': ["...", ".#.", "...", ".#.", "..."],
    '(': [".#.", "#..", "#..", "#..", ".#."],
    ')': [".#.", "..#", "..#", "..#", ".#."],
    '+': ["...", ".#.", "###", ".#.", "..."],
    '-': ["...", "...", "###", "...", "..."],
    '=': ["...", "###", "...", "###", "..."],
    '[': ["###", "#..", "#..", "#..", "###"],
    ']': ["###", "..#", "..#", "..#", "###"],
    "'": [".#.", ".#.", "...", "...", "..."],
    '!': [".#.", ".#.", ".#.", "...", "###"],
    '~': ["#.#", "###", "###", ".#.", "..."],
    '.': ["...", "...", "...", "##.", "##."],
    '?': ["###", "..#", ".#.", "...", ".#."],
    '{': [".##", ".#.", "##.", ".#.", ".##"],
    '}': ["##.", ".#.", ".##", ".#.", "##."],
    '<': ["..#", ".#.", "#..", ".#.", "..#"],
    '>': ["#..", ".#.", "..#", ".#.", "..#"]
}

class Logos():
    def __init__(self, logo: str, conf: MazeConfig) -> None:
        self.logo = logo
        self.width = conf.width
        self.height = conf.height
        self.full_logo: list[list[int]] = [
                    [False for _ in range(self.width)]
                    for _ in range(self.height)]

    def MakeLogo(self) -> list[list[bool]]:
        glyph_rows = 5
        logo_grid: list[list[bool]] = [[] for _ in range(glyph_rows)]

        for i, char in enumerate(self.logo):
            glyph = self.GridNumbers(char.upper())
            for r in range(glyph_rows):
                if i > 0 and not char == ' ':
                    logo_grid[r].append(False)
                logo_grid[r].extend(glyph[r])

        logo_width = len(logo_grid[0])
        if self.width < logo_width + 2 or self.height < 7:
            raise errors.MazeSizeException(
                f"Maze too small: must be at least {logo_width + 2}"
                f" wide and 7 high.")
        start_r = (self.height - glyph_rows) // 2
        start_c = (self.width - logo_width) // 2

        for r_idx, row in enumerate(logo_grid):
            for c_idx, val in enumerate(row):
                self.full_logo[start_r + r_idx][start_c + c_idx] = val

        self.glyph = [row[:] for row in self.full_logo]
        self.fill_pockets()
        return self.full_logo

    def fill_pockets(self) -> None:
        seen = [[False] * self.width for _ in range(self.height)]
        queue = deque([(0, 0)])
        seen[0][0] = True
        while queue:
            r, c = queue.popleft()
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if (0 <= nr < self.height and 0 <= nc < self.width
                        and not seen[nr][nc] and not self.full_logo[nr][nc]):
                    seen[nr][nc] = True
                    queue.append((nr, nc))
        for r in range(self.height):
            for c in range(self.width):
                if not self.full_logo[r][c] and not seen[r][c]:
                    self.full_logo[r][c] = True

    def GridNumbers(self, char: str) -> list[list[bool]]:
        if char not in CHARS:
            raise errors.CharNotFound(f"no glyph for {char!r}")
        return [[c == '#' for c in row] for row in CHARS[char]]