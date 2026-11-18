from maze_generator import MazeConfig
from . import Canvas
from .elements import CanvasText, CanvasTextBox, CanvasButton
from .colors import Colors
from . import Vector2
from typing import Any


class SettingsWindow():
    def __init__(self, conf: MazeConfig, canvas: Canvas, conf_path: str) -> None:
        self.set_dict = vars(conf)
        self.canvas = canvas
        self.conf_path = conf_path
        self.settings_dict: dict[str, CanvasTextBox] = {}

    def save_settings(self) -> None:
        new_settings: list[str] = []
        for key, val_box in self.settings_dict.items():
            line = ""
            line = key.upper() + "=" + val_box.text
            new_settings.append(line)
        file_content = "\n".join(new_settings)
        with open(self.conf_path, "w") as file:
            file.write(file_content)


    def draw_settings(self) -> None:
        line = 0
        for setting, set_val in self.set_dict.items():
            parsed_val = str(set_val).rstrip("\n")
            setting_key = CanvasText(f"{setting} = ", 30, Colors.RED)
            setting_key.global_position = Vector2(20, line)
            self.canvas.add_child(setting_key)
            setting_key._draw()
            setting_val = CanvasTextBox(f"{parsed_val}", 30, Colors.RED)
            setting_val.global_position = Vector2(setting_key.rect.end.x + 20, line)
            self.canvas.add_child(setting_val)
            self.settings_dict[setting] = setting_val
            line += 60
        save_button = CanvasButton("Save settings?", self.save_settings, 30, Colors.GREEN)
        bottom_right = Vector2(self.canvas.window.width - 193, self.canvas.window.height - 213)
        save_button.global_position = bottom_right
        self.canvas.add_child(save_button)
        self.canvas.render_canvas()
 