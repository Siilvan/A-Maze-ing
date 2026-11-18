from maze_generator import MazeConfig
from . import Canvas, CanvasText
from .colors import Colors


class SettingsWindow():
    def __init__(self, conf: MazeConfig, canvas: Canvas) -> None:
        self.set_dict = vars(conf)
        self.canvas = canvas

    def draw_settings(self) -> None:
        line = 0
        for setting, set_val in self.set_dict.items():
            setting_label = CanvasText(f"{setting} = '{str(set_val).rstrip("\n")}'", 30, Colors.RED)
            setting_label.global_position = (50, line)
            line += 60
            self.canvas.add_child(setting_label)
        
        self.canvas.render_canvas()
