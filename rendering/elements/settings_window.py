from maze_generator import MazeConfig, Logger
from ..canvas import CanvasElement, Rect
from ..colors import Colors
from .text import CanvasText
from .textbox import CanvasTextBox
from .button import CanvasButton
from .container import CanvasBoxContainer
class CanvasSettings(CanvasElement):
    """
    Canvas element that displays the maze configuration as editable settings.

    Reads the config file at `conf_path` and builds one row per setting: a
    label and a text box holding the value. A save button below the rows
    writes the edited values back to the file. All children are positioned
    relative to this element, so a parent container can move it freely.
    """
    def __init__(self, conf: MazeConfig, conf_path: str) -> None:
        super().__init__()
        self.conf_path = conf_path
        self.conf = conf
        self.settings_dict: dict[str, CanvasTextBox] = {}
        self.vbox = CanvasBoxContainer(10, 0, True)

    def get_rect(self) -> Rect:
        # !!!!! IF SETTINGS WINDOW IS NOT CLEARING PROPERLY UNCOMMENT THE LINES BELOW
        # AND COMMENT THE OTHER RETURN, I DONt KNOW WHY THIS WORKS AND IT DOESNT MATTER
        # WE'LL JUST HAVE TO BE FINE WITH THE CLEARING WHEN OYU FIRST OPEN THE SETTINGS

        # self.rect =  self.vbox.get_rect()
        # return self.rect
        return self.vbox.get_rect()

    def _draw(self) -> None:
        self.rect = self.get_rect()
        super()._draw()

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
            MazeConfig().from_file(self.conf_path)
        except MazeConfig.ParseError as e:
            Logger.get().e(f"{e.msg}")
            new_settings = old_settings
        except Exception as e:
            Logger.get().e(f"{e}")
            new_settings = old_settings
        with open(self.conf_path, "w") as final:
            final.write(new_settings)
        self.rect = self.get_rect()
        self.parent.remove_child(self)

    def _initialize(self) -> None:
        self.add_child(self.vbox)
        with open(self.conf_path, "r") as conf_file:
            for line in conf_file:
                line = line.strip("\n")
                setting, setting_val = line.split("=")
                hbox = CanvasBoxContainer(10, 0, False)
                self.vbox.add_child(hbox)
                hbox.add_child(CanvasText(f"{setting} = ", 30, Colors.RED))
                val_box = CanvasTextBox(f"{setting_val}", 30, Colors.RED)
                hbox.add_child(val_box)
                self.settings_dict[setting] = val_box
        save_button = CanvasButton(
            "Save settings?", self.save_settings, 30, Colors.GREEN)
        self.vbox.add_child(save_button)