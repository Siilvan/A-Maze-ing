from typing import Any
from .utils import *
from .helpers import MazeGenerationException, MazeSizeException


class MazeConfig:

    class ParseError(Exception):
        def __init__(self, msg: str, line_n: int, line: str) -> None:
            self.msg = msg
            self.line_n = line_n
            self.line = line

    def __init__(self,
                 exit_pos: tuple[int, int] | None = None,
                 entry_pos: tuple[int, int] = (0, 0),
                 output_path: str = "output.mz",
                 perfect: bool = False,
                 width: int = 50,
                 height: int = 50,
                 logo:str = "42"
                 ) -> None:
        self.width: int = width
        self.height: int = height
        self.entry_pos: tuple[int, int] = entry_pos
        if (exit_pos is None):
            self.exit_pos: tuple[int, int] = (self.width - 1,
                                              self.height - 1)
        else:
            self.exit_pos = exit_pos
        self.output_path: str = output_path
        self.perfect: bool = perfect
        self.logo: str = logo

    def validate_config(self) -> bool:
        """
        Validates the config and it's current parameters.
        ensures everything is how it should be.

        returns True or False if the config is correct or not
        """
        if self.width < 2 or self.height < 2:
            raise MazeSizeException(
                "Maze must be at least 2 wide and 2 high")
        if (not 0 <= self.entry_pos[0] < self.height
            or not 0 <= self.entry_pos[1] < self.width):
            raise MazeGenerationException(
                "Entry position outside of maze.")
        if (not 0 <= self.exit_pos[0] < self.height
            or not 0 <= self.exit_pos[1] < self.width):
            raise MazeGenerationException(
                "Exit position outside of maze")

        return (True)

    @classmethod
    def from_file(cls, path: str) -> "MazeConfig":
        """
        Attemps to parse a config object from a file of 
        KEY=VALUE pairs.

        returns None on failure
        """
        config: "MazeConfig" = cls()
        with open(path, "r") as f:
            line_n : int = 1
            line: str = f.readline()
            while (line != ""):
                if (config._should_skip_line(line)):
                    line = f.readline()
                    line_n += 1
                    continue
                key, val = config._parse_line(line, line_n)
                if (not config._assign_key(key, val)):
                    raise MazeConfig.ParseError(
                            msg=f"Failed to assign \033[32m\"{val}\"\033[0m to \033[33m{key}\033[0m, " +
                            "ensure the type and naming are correct.",
                            line_n=line_n,
                            line=line
                            )
                line = f.readline()
                line_n += 1
        config.validate_config()
        return config

    def _should_skip_line(self, line: str) -> bool:
        """
        Checks wether the provided line should be skipped:
        (comment or empty line)
        """
        line = line.strip()
        return (line.startswith("#") or line == "")

    def _parse_line(self, line: str, line_n: int) -> tuple[str, str]:
        """
        Parses a config line, returns a tuple containing (key, val)
        """
        line = line.strip()
        eq_pos: int = line.find("=")
        if (eq_pos == -1):
            raise MazeConfig.ParseError(
                    msg="Unparseable line",
                    line_n=line_n,
                    line=line)
        key: str = line[:eq_pos]
        comment_pos: int = line.find("#")
        val: str = ""
        if (comment_pos < 0):
            val = line[eq_pos + 1:]
        else:
            val = line[eq_pos + 1:comment_pos]
        return (key, val)

    def _assign_key(self, key: str, val: Any) -> bool:
        """
        Assigns the key with id `key` with the value `val`.
        only attemps to do so if val is of the right type,
        and key exists.
        """
        key = key.lower()
        # Ensure that this object has an attribute with the keyname
        if (hasattr(self, key)):
            parsed: Any = try_parse(val, type(getattr(self, key)))
            if (parsed is None):
                return False
            setattr(self, key, parsed)
            return True
        if (key == "entry"):
            return self._assign_key("entry_pos", val)
        if (key == "exit"):
            return self._assign_key("exit_pos", val)
        return False

    def __str__(self) -> str:
        return "\n".join([f"{k}={v}" for k, v in self.__dict__])

    def __repr__(self) -> str:
        return str(self)

