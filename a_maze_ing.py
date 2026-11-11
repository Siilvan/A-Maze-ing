from maze_generator import *
from stupid_claude_draw_test_func import draw_maze

def main() -> None:
    try:
        conf = MazeConfig.from_file("sdcc.txt")
    except MazeConfig.ParseError as e:
        print(f"Parse Error on line {e.line_n}: {e.msg}\nLine content: {e.line}")
        return
    generator = RowByRowMazeGenerator(conf)
    generator.generate_maze()
    draw_maze(generator.grid)


if __name__ == "__main__":
    main()