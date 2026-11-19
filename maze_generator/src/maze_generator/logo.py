from .config import MazeConfig
from collections import deque
import sys
from .helpers import Logger, ManualExit

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
    '>': ["#..", ".#.", "..#", ".#.", "#.."]
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
        if not self.logo:
            return[[False for _ in range(self.width)] for _ in range(self.height)]
        for i, char in enumerate(self.logo):
            glyph = self.GridChars(char.upper())
            for r in range(glyph_rows):
                if i > 0 and not char == ' ':
                    logo_grid[r].append(False)
                logo_grid[r].extend(glyph[r])

        logo_width = len(logo_grid[0])
        logo_len = 0
        for i in range(len(self.logo)):
            logo_len += 3
            if i < len(self.logo) - 1 and self.logo[i + 1] != " ":
                logo_len += 1
            if self.height < 7 or self.width < logo_len + 2:
                Logger.get().w(f"Maze too small for logo: must be at least {logo_len + 2}"
                               f" wide and 7 high.")
                Logger.get().w("Continue printing maze without logo? (y/n) ", end="")
                sys.stdout.flush()
                y_n = sys.stdin.readline().strip()
                if y_n.lower() == "y":
                    self.logo = ""
                else: 
                    raise ManualExit("User exited program - quitting")
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

    def GridChars(self, char: str) -> list[list[bool]]:
        if char not in CHARS:
            Logger.get().w(f"No Glyph for: {char}. Using space instead.")
            char = ' '
        return [[c == '#' for c in row] for row in CHARS[char]]