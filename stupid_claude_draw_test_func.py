
def draw_maze(grid, use_north=True):
    """Print a maze as ASCII art.

    Each cell is a number whose bits are walls (1 = closed, 0 = open):
    bit 0 (1) = North, bit 1 (2) = East, bit 2 (4) = South, bit 3 (8) = West.

    A wall is drawn if EITHER of the two cells sharing it says it is closed.
    use_north=False ignores the North bit for interior walls and only trusts
    the South bit of the cell above (useful if your data has every North bit set).
    """
    N, E, S, W = 1, 2, 4, 8
    rows, cols = len(grid), len(grid[0])
    out = []

    for r in range(rows + 1):
        # Horizontal wall line above row r
        line = "+"
        for c in range(cols):
            if r == 0:
                closed = grid[0][c] & N
            elif r == rows:
                closed = grid[-1][c] & S
            else:
                closed = grid[r - 1][c] & S
                if use_north:
                    closed = closed or grid[r][c] & N
            line += "---+" if closed else "   +"
        out.append(line)

        if r == rows:
            break

        # Cells and vertical walls in row r
        line = ""
        for c in range(cols + 1):
            if c == 0:
                closed = grid[r][0] & W
            elif c == cols:
                closed = grid[r][-1] & E
            else:
                closed = grid[r][c - 1] & E or grid[r][c] & W
            line += "|" if closed else " "
            if c < cols:
                line += "   "
        out.append(line)

    print("\n".join(out))
    print("DONE")
