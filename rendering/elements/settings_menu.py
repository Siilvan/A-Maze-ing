from maze_generator import MazeConfig, Logger
from ..canvas import CanvasElement, Rect
from ..colors import Colors
from .text import CanvasText
from .textbox import CanvasTextBox
from .button import CanvasButton
from .container import CanvasContainer
from typing import Any, Callable
import os


class CanvasSettings(CanvasElement):
    """
    Canvas element that displays the maze configuration as editable settings.

    Reads the config file at `conf_path` and builds one row per setting: a
    label and a text box holding the value. A save button below the rows
    writes the edited values back to the file. All children are positioned
    relative to this element, so a parent container can move it freely.
    """

    def __init__(
            self,
            conf: MazeConfig,
            conf_path: str | None,
            path_set: Callable | None = None,
            ) -> None:
        super().__init__()
        self.conf_path = conf_path
        self.conf = conf
        self.path_set = path_set
        self.conf_fields: dict[str, Any] = {
            key: val for key, val in
            conf.__dict__.items() if key != "expected_types"
            }
        self.settings_dict: dict[str, CanvasTextBox] = {}
        self.vbox = CanvasContainer(10, 0, True)

    def get_rect(self) -> Rect:
        self.rect = self.vbox.get_rect()
        return self.rect

    def _draw(self) -> None:
        self.rect = self.get_rect()
        super()._draw()

    def save_settings(self) -> None:
        if self.conf_path is None:
            Logger.get().e(
                "No config path specified. "
                "Saving to default path instead (maze.conf)")
            self.conf_path = "maze.conf"
        new_lines: list[str] = [
            key.upper() + "=" + val_box.text
            for key, val_box in self.settings_dict.items()
        ]
        new_settings = "\n".join(new_lines)

        try:
            with open(self.conf_path, "r") as curr_conf:
                old_settings = curr_conf.read()
        except FileNotFoundError:
            old_settings = None

        new_conf: MazeConfig | None = None
        try:
            with open(self.conf_path, "w") as file:
                file.write(new_settings)
            new_conf = MazeConfig.from_file(self.conf_path)
        except MazeConfig.ParseError as e:
            Logger.get().e(f"{e.msg}")
        except Exception as e:
            Logger.get().e(f"{e}")

        if new_conf is None:
            if old_settings is not None:
                with open(self.conf_path, "w") as final:
                    final.write(old_settings)
            else:
                os.remove(self.conf_path)
        else:
            for key, val in new_conf.__dict__.items():
                setattr(self.conf, key, val)
            if self.path_set is not None:
                self.path_set(self.conf_path)
        self.get_rect()

        if (self.parent is not None):
            self.parent.remove_child(self)

    def _initialize(self) -> None:
        self.add_child(self.vbox)
        for setting, val in self.conf_fields.items():
            hbox = CanvasContainer(10, 0, False)
            self.vbox.add_child(hbox)
            val = str(val)
            if setting == "entry_pos":
                setting = "entry"
                val = val.strip("()")
            elif setting == "exit_pos":
                setting = "exit"
                val = val.strip("()")
            setting = setting.upper()
            hbox.add_child(CanvasText(f"{setting} = ", 32, Colors.WHITE))
            val_box = CanvasTextBox(f"{val}", 32, Colors.WHITE, Colors.BLACK)
            hbox.add_child(val_box)
            self.settings_dict[setting] = val_box
        save_button = CanvasButton(
            "Save settings?", self.save_settings, 32, Colors.GREEN
        )
        self.vbox.add_child(save_button)
