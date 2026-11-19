from maze_generator import MazeConfig, Logger
from . import Canvas
from .elements import CanvasText, CanvasTextBox, CanvasButton
from .colors import Colors
from . import Vector2


class SettingsWindow():
    def __init__(self, conf: MazeConfig,
                 canvas: Canvas,
                 conf_path: str
                 ) -> None:
        self.canvas = canvas
        self.conf_path = conf_path
        self.conf = conf
        self.settings_dict: dict[str, CanvasTextBox] = {}

    def save_settings(self) -> None:
        new_lines: list[str] = []
        for key, val_box in self.settings_dict.items():
            line = ""
            line = key.upper() + "=" + val_box.text
            new_lines.append(line)
        with open(self.conf_path, "r") as curr_conf:
            old_settings = curr_conf.read()
        new_settings = "\n".join(new_lines)
        with open(self.conf_path, "w") as file:
            file.write(new_settings)
        try:
            temp_conf = MazeConfig().from_file(self.conf_path)
        except MazeConfig.ParseError as e:
            Logger.get().e(f"{e.msg}")
            new_settings = old_settings
        except Exception as e:
            Logger.get().e(f"{e}")
            new_settings = old_settings
        with open(self.conf_path, "w") as final:
            final.write(new_settings)
        self.conf = temp_conf
    
    def draw_settings(self) -> None:
        canvas_line = 0
        with open(self.conf_path, "r") as conf_file:
            for line in conf_file:
                line = line.strip("\n")
                setting, setting_val = line.split("=")
                key_label = CanvasText(f"{setting} = ", 30, Colors.RED)
                key_label.global_position = Vector2(20, canvas_line)
                self.canvas.add_child(key_label)
                key_label._draw()
                val_box = CanvasTextBox(f"{setting_val}", 30, Colors.RED)
                val_box.global_position = Vector2(
                    key_label.rect.end.x + 20, canvas_line
                    )
                self.canvas.add_child(val_box)
                self.settings_dict[setting] = val_box
                canvas_line += 60
        save_button = CanvasButton(
            "Save settings?", self.save_settings, 30, Colors.GREEN)
        bottom_right = Vector2(
            self.canvas.window.width - 193,
            self.canvas.window.height - 213)
        save_button.global_position = bottom_right
        self.canvas.add_child(save_button)
        self.canvas.render_canvas()
